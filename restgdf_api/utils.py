from aiohttp import ClientSession


async def get_session():
    async with ClientSession() as session:
        yield session
