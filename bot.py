import aiohttp
import asyncpg
import discord
from discord.ext import commands
from typing import Optional
import os
from aiolimiter import AsyncLimiter
import aiofiles

class Green(commands.Bot):
    def __init__(self, config: dict):
        super().__init__(
            command_prefix=commands.when_mentioned,  # type: ignore
            intents=discord.Intents.all(),
            help_command=None,
        )

        self.pool: Optional[asyncpg.Pool] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = config
        self.limiter = AsyncLimiter(25, 30)

    async def setup_hook(self) -> None:
        operator_nation = self.config["nation"]
        self.session = aiohttp.ClientSession(headers={
            "User-Agent":
                f"Green DiscordBot 0.1.0 "
                f"/ Developed by nation:TheSapphire "
                f"/ Operated by nation:{operator_nation}"
        })
        self.pool = await asyncpg.create_pool(dsn=self.config["dsn"])

        for cog in os.listdir("cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f'cogs.{cog[:-3]}')

    async def ns_request(self, params: dict, mode):
        async with self.limiter:
            pass

    async def ns_dump(self):
        async with self.session.get(
                "https://www.nationstates.net/pages/nations.xml.gz"
        ) as resp:
            if resp == 200:
                f = await aiofiles.open('nations.xml.gz', mode='wb')
                async for chunk, _ in resp.content.iter_chunks():
                    await f.write(await chunk)
                await f.close()
                return True
            else:
                return False

    async def close(self) -> None:
        await super().close()
        await self.session.close()
        await self.pool.close()
