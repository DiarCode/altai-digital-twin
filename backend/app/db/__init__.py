from prisma import Prisma

client = Prisma()

async def connect_db():
    await client.connect()

async def disconnect_db():
    await client.disconnect()
