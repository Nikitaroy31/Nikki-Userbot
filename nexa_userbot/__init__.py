# Copyright (c) 2021 Itz-fork
# Part of: Nexa-Userbot
from time import time
from pyrogram import Client
from config import Config

# Configs
CMD_HELP = {}
StartTime = time()

NEXAUB = Client(
    Config.PYRO_STR_SESSION,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=10
)

bot = Client(
    ":nikki:",
    api_hash=Config.API_HASH,
    api_id=Config.APP_ID,
    bot_token=Config.BOT_TOKEN,
)
