from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from telethon import client,InputPhoneContact

# Assuming imports for Telethon
# from telethon.sync import TelegramClient
# from telethon.tl.types import InputPhoneContact
# from telethon.tl.functions.contacts import ImportContactsRequest

router = APIRouter()

class ContactRequest(BaseModel):
    phone: str
    first_name: str
    last_name: Optional[str] = None

@router.post("/messages")
async def fetch_messages(data: ContactRequest):
    try:
        async with client:
            me = await client.get_me()
            sender = f"{me.first_name} {me.last_name or ''}".strip()

            contact = InputPhoneContact(
                client_id=0,
                phone=f'+63{data.phone}',
                first_name=data.first_name,
                last_name=data.last_name or ""
            )
            res = await client(ImportContactsRequest([contact]))
            if not res.users:
                raise HTTPException(status_code=404, detail="User not found.")

            receiver = res.users[0]
            rec_name = f"{receiver.first_name} {receiver.last_name or ''}".strip()

            messages = []
            async for msg in client.iter_messages(receiver.id, limit=10):
                name = sender if msg.out else rec_name
                messages.append({
                    "from": name,
                    "date": str(msg.date),
                    "text": msg.text
                })

            return {
                "sender": sender,
                "receiver": rec_name,
                "messages": messages
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))