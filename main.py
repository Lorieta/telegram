from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import os

api_id = os.getenv['TELEGRAM_API_ID']
api_hash = os.getenv['TELEGRAM_API_HASH']
session = 'name'

client = TelegramClient(session, api_id, api_hash)

async def main(receiver_phone, receiver_first_name='', receiver_last_name=''):
    me = await client.get_me()
    sender = f"{me.first_name} {me.last_name or ''}".strip()
    contact = InputPhoneContact(0, f'+63{receiver_phone}', receiver_first_name, receiver_last_name)
    res = await client(ImportContactsRequest([contact]))
    if not res.users:
        print("User not found.")
        return
    receiver = res.users[0]
    rec_name = f"{receiver.first_name} {receiver.last_name or ''}".strip()
    print(f"Sender: {sender}")
    print(f"Receiver: {rec_name} (ID: {receiver.id})")
    async for msg in client.iter_messages(receiver.id, limit=10):
        name = sender if msg.out else rec_name
        print(f"{name}: {msg.date}: {msg.text}")

if __name__ == '__main__':
    target_phone = input("Enter receiver's phone number (without +63): ")
    first_name = input("Enter receiver's first name (optional): ")
    last_name = input("Enter receiver's last name (optional): ")
    with client:
        client.loop.run_until_complete(main(target_phone, first_name, last_name))