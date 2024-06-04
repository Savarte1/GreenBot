import tomllib
import aiohttp
import asyncpg
import discord
from discord.ext import commands
from typing import Optional
from aiolimiter import AsyncLimiter
import os


class Green(commands.Bot):
    def __init__(self, config):
        super().__init__(
            command_prefix="g!",
            intents=discord.Intents.all(),
            help_command=None,
        )

        self.pool: Optional[asyncpg.Pool] = None
        self.session = None
        self.limiter = AsyncLimiter(25, 30)
        self.config = config

    async def setup_hook(self) -> None:
        operator_nation = self.config["nation"]
        self.pool = await asyncpg.create_pool(dsn=self.config["dsn"])
        self.session = aiohttp.ClientSession(headers={
            "User-Agent": f"Green DiscordBot 0.1.0 "
                          f"/ Developed by nation:TheSapphire "
                          f"/ Operated by nation:{operator_nation}"
        })

        for cog in os.listdir("cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f'cogs.{cog[:-3]}')

    async def close(self) -> None:
        await super().close()
        await self.session.close()
        await self.pool.close()

