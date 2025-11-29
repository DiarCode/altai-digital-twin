from prisma import Prisma
import asyncio


class PrismaWrapper:
    """
    Prisma client wrapper to manage connect/disconnect concurrency and expose the underlying client.
    Use this wrapper as `from app.db import client` so it behaves like the Prisma client but prevents
    race conditions during connection and provides centralized connection management.
    """

    def __init__(self):
        self._client = Prisma()
        self._lock = asyncio.Lock()
        self._connected = False

    async def connect(self):
        async with self._lock:
            if not self._connected:
                await self._client.connect()
                self._connected = True

    async def disconnect(self):
        async with self._lock:
            if self._connected:
                await self._client.disconnect()
                self._connected = False

    @property
    def client(self):
        return self._client

    def __getattr__(self, name):
        # Delegate attribute access to the underlying Prisma client
        return getattr(self._client, name)


client = PrismaWrapper()

