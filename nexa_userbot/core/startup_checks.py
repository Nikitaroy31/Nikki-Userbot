# Copyright (c) 2021 Itz-fork
# Part of: Nexa-Userbot
import os
import asyncio
import logging

from pyrogram.errors import YouBlockedUser, PeerIdInvalid
from nexa_userbot import NEXAUB, bot
from nexa_userbot.core.main_cmd import nexaub
from nexa_userbot.core.nexaub_database.nexaub_db_conf import set_log_channel, get_log_channel, set_arq_key, get_arq_key
from nexa_userbot.core.nexaub_database.nexaub_db_sudos import get_custom_plugin_channels
from config import Config


# Log Channel Checker
async def check_or_set_log_channel():
    try:
        al_log_channel = await get_log_channel()
        if al_log_channel:
            return [True, al_log_channel]
        else:
            log_channel = await NEXAUB.create_supergroup(title="Nexa Userbot Logs", description="Logs of your Nexa Userbot")
            log_channel_id = log_channel.id
            await NEXAUB.set_chat_photo(chat_id=log_channel_id, photo="cache/NEXAUB.png")
            await NEXAUB.add_chat_members(log_channel_id,Config.BOT_USERNAME)
            await NEXAUB.promote_chat_member(log_channel_id,Config.BOT_USERNAME)
            welcome_to_nexaub = f"""
**Welcome to Nexa Userbot**
Thanks for trying Nexa Userbot. If you found any error, bug or even a Feature Request please report it at **@NexaUB_Support**

**⌲ Quick Start,**
If you don't know how to use this Userbot please send `{Config.CMD_PREFIX}help` in any chat. It'll show all plugins your userbot has. You can use those plugin names to get info about how to use it. Also check out [Docs](https://nexaub.itz-fork.xyz/)


 **~ Nexa Userbot, Developers**"""
            await set_log_channel(log_channel_id)
            await NEXAUB.send_message(chat_id=log_channel_id, text=welcome_to_nexaub, disable_web_page_preview=True)
            await bot.send_message(chat_id=log_channel_id, text=welcome_to_nexaub, disable_web_page_preview=True)
            return [True, log_channel_id]
    except Exception as e:
        logging.warn(
            f"Error: \n{e} \n\nPlease check all variables and try again! \nReport this with logs at @NexaUB_Support if the problem persists!")
        exit()


# Plugin installer for channels
async def search_and_download_plugs(channel, max_tries=2, counted=0):
    if counted >= max_tries:
        return
    try:
        async for plugin in NEXAUB.search_messages(chat_id=channel, query=".py", filter="document"):
            plugin_name = plugin.document.file_name
            if not os.path.exists(f"nexa_userbot/modules/Extras/{plugin_name}"):
                await NEXAUB.download_media(message=plugin, file_name=f"nexa_userbot/modules/Extras/{plugin_name}")
    except PeerIdInvalid:
        counted += 1
        await nexaub().resolve_peer(channel, max_tries=1)
        return await search_and_download_plugs(channel, counted=counted)

async def download_plugins_in_channel():
    plugin_channels = await get_custom_plugin_channels()
    if plugin_channels:
        for channel in plugin_channels:
            try:
                await search_and_download_plugs(channel)
            except BaseException as e:
                logging.warn(
                    f"Error: \n{e} \n\nUnable to install plugins from custom plugin channels!")
    else:
        logging.info(
            "No Custom Plugin Channels were specified, Nexa-Userbot is running with default plugins only!")


# Custom plugin collector
async def install_custom_plugins():
    custom_plugin_path = "nexa_userbot/modules/Extras"
    if os.path.isdir(custom_plugin_path):
        for plugin in os.listdir(custom_plugin_path):
            if str(plugin).startswith("__"):
                return
            if plugin.endswith(".py"):
                try:
                    nexaub().import_plugin(
                        (os.path.join(custom_plugin_path, plugin)).replace(".py", ""))
                except:
                    logging.warn(
                        f"Error happened while installing {os.path.join(custom_plugin_path, plugin)} plugin")
                    try:
                        os.remove(plugin)
                    except:
                        pass
    else:
        logging.info("No Custom Plugins were found to install!")


# ARQ API KEY Checker
async def check_arq_api():
    try:
        try:
            await NEXAUB.send_message("ARQRobot", "/start")
        except YouBlockedUser:
            await NEXAUB.unblock_user("ARQRobot")
            await asyncio.sleep(0.2)
            await NEXAUB.send_message("ARQRobot", "/start")
        await asyncio.sleep(0.5)
        await NEXAUB.send_message("ARQRobot", "/get_key")
        get_h = (await NEXAUB.get_history("ARQRobot", 1))[0]
        g_history = get_h.text
        if "X-API-KEY:" not in g_history:
            nexaub_user = await NEXAUB.get_me()
            arq_acc_name = nexaub_user.first_name if nexaub_user.first_name else f"Unknown_{nexaub_user.id}"
            await asyncio.sleep(0.4)
            await NEXAUB.send_message("ARQRobot", f"{arq_acc_name}")
            await asyncio.sleep(0.3)
            gib_history = (await NEXAUB.get_history("ARQRobot", 1))[0]
            g_history = gib_history.text
            arq_api_key = g_history.replace("X-API-KEY: ", "")
        else:
            arq_api_key = g_history.replace("X-API-KEY: ", "")
        is_arqed = await get_arq_key()
        if is_arqed is None:
            await set_arq_key(arq_api_key)
        else:
            pass
    except Exception as e:
        logging.warn(
            f"Error: \n{e} \n\nThere was a problem while obtaining ARQ API KEY. However you can set it manually. Send, \n{Config.CMD_PREFIX}setvar ARQ_API_KEY your_api_key_here")
