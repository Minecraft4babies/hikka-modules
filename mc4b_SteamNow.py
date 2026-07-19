#    ____  __  __ _                            __ _   _  _   _           _     _
#   / __ \|  \/  (_)_ __   ___  ___ _ __ __ _ / _| |_| || | | |__   __ _| |__ (_) ___  ___
#  / / _` | |\/| | | '_ \ / _ \/ __| '__/ _` | |_| __| || |_| '_ \ / _` | '_ \| |/ _ \/ __|
# | | (_| | |  | | | | | |  __/ (__| | | (_| |  _| |_|__   _| |_) | (_| | |_) | |  __/\__ \
#  \ \__,_|_|  |_|_|_| |_|\___|\___|_|  \__,_|_|  \__|  |_| |_.__/ \__,_|_.__/|_|\___||___/
#   \____/

import requests
import json
import logging
import telethon
import asyncio
from .. import loader, utils

def register(cb):
    cb(Mc4bSteamNowMod())

@loader.tds
class Mc4bSteamNowMod(loader.Module):
    """Module for showing you Steam activity in bio."""
    strings = {
        "name": "SteamNow",
        "autobio": "<b>SteamNow autobio turned {}!</b>",
        "autobio_on": "on",
        "autobio_off": "off",
        "config_required": "<b>Type <code>.config</code> and set your SteamAPI with SteamID and <code>.restart</code>!</b>",
        "_cmd_doc_steambio":"""Toggle bio Steam activity streaming

        👨‍💻Made by: @Minecraft4babies_Modules"""
    }

    strings_ru = {
        "name": "SteamNow",
        "autobio": "<b>SteamNow autobio {}!</b>",
        "autobio_on": "включено",
        "autobio_off": "выключено",
        "config_required": "<b>Пропиши <code>.config</code> и настрой свои SteamAPI с SteamID и потом <code>.restart</code>!</b>",
        "_cls_doc": "Модуль для показа в био игровой активности Steam.",
        "_cmd_doc_steambio": """Включение / выключение Steambio

        👨‍💻Made by: @Minecraft4babies_Modules"""
    }

    strings_ua = {
        "name": "SteamNow",
        "autobio": "<b>SteamNow autobio {}!</b>",
        "autobio_on": "увімкнено",
        "autobio_off": "вимкнено",
        "config_required": "<b>Пропиши <code>.config</code> та налаштуй свої SteamAPI з SteamID і потім <code>.restart</code>!</b>",
        "_cls_doc": "Модуль для показу в біо ігрової активності Steam.",
        "_cmd_doc_steambio": """Вмикання та вимикання Steambio

        👨‍💻Made by: @Minecraft4babies_Modules"""
    }

    def __init__(self):
        self.bio_task = None
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "NoActivityBio",
                "",
                "Bio when there is no activity."
            ),
            loader.ConfigValue(
                "AutoBioTemplate",
                "🟢Online Steam: 🎮{}",
                "Template for Steam AutoBio. Instead of \"{}\" will be the game's name."
            ),
            loader.ConfigValue(
                "SteamAPI",
                None,
                "SteamAPI from https://steamcommunity.com/dev/apikey."
            ),
            loader.ConfigValue(
                "SteamID",
                None,
                "User's Steam ID from https://steamdb.info/calculator/."
            ),
        )

    async def autobio(self) -> None:
        while True:
            last_bio = (await self.client(telethon.tl.functions.users.GetFullUserRequest(await self.client.get_me()))).full_user.about
            url = (
                "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
                f"?key={self.config['SteamAPI']}&steamids={self.config['SteamID']}"
            )
    
            try:
                request = requests.get(url)
                request_dict = json.loads(request.text)
    
                player = request_dict["response"]["players"][0]
                playing_game = player.get("gameextrainfo")
    
                if playing_game:
                    bio = self.config["AutoBioTemplate"].format(playing_game)
                    delay = 20
                else:
                    bio = self.config["NoActivityBio"] or ""
                    delay = 60
                
                if bio != last_bio:
                    await self.client(
                        telethon.tl.functions.account.UpdateProfileRequest(
                            about=bio[:70]
                        )
                    )
                    last_bio = bio
    
            except Exception as e:
                logging.exception("SteamNow autobio error: %s", e)
                delay = 60
    
            await asyncio.sleep(delay)

    def stop(self) -> None:
        if not self.bio_task:
            return

        self.bio_task.cancel()

    async def client_ready(self, client, db) -> None:
        self.db = db
        self.client = client
        if db.get(self.name, 'autobio', False):
            self.bio_task = asyncio.ensure_future(self.autobio())

    async def steambiocmd(self, message) -> None:
        if not (self.config["SteamAPI"] and self.config["SteamID"]):
            await utils.answer(message, self.strings('config_required'))
            return
        current = self.db.get(self.name, 'autobio', False)
        new = not current
        self.db.set(self.name, 'autobio', new)
        await utils.answer(message, self.strings('autobio').format(self.strings('autobio_on') if new else self.strings('autobio_off')))
        if new:
            self.bio_task = asyncio.ensure_future(self.autobio())
        else:
            self.stop()
