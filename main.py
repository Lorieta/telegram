from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import asyncio

# Your Telegram API credentials
api_id = '21398172'
api_hash = '4bb0f51ffa700b91f87f07742d6f1d33'

# Phone number to search (without +63)
target_phone = '9955578757'

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Step 1: Add the user temporarily as a contact
    contact = InputPhoneContact(client_id=0, phone=f'+63{target_phone}', first_name='Temp', last_name='User')
    result = await client(ImportContactsRequest([contact]))

    if not result.users:
        print("User not found.")
        return

    user = result.users[0]
    print(f"Found user: {user.first_name} {user.last_name} (ID: {user.id})")

    # Step 2: Retrieve messages from this user
    async for message in client.iter_messages(user.id, limit=10):
        print(f"{user.last_name}:{message.date}: {message.text}")

with client:
    client.loop.run_until_complete(main())
