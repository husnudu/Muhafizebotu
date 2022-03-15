import time
import os
import json
from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL

from youtube_dl.utils import (DownloadError, ContentTooShortError,

                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)

from telethon import types
from telethon.tl import functions
from LaylaRobot.laylabot import layla
from youtubesearchpython import SearchVideos
from tswift import Song


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None

JULIASONG = "@MissJuliaRobotMP3"
JULIAVSONG = "@MissJuliaRobotMP4"


@layla(pattern="^/lyrics ?(.*)")
async def download_lyrics(v_url):
    if v_url.is_group:
        if (await is_register_admin(v_url.input_chat, v_url.message.sender_id)):
            pass
        elif v_url.chat_id == iid and v_url.sender_id == userss:
            pass
        else:
            return
    query = v_url.pattern_match.group(1)
    if not query:
        await v_url.reply("Hansı mahnını axtaracağını dəqiqləşdirməmisiniz!")
        return
    song = Song.find_song(query)
    if song:
        if song.lyrics:
            reply = song.format()
        else:
            reply = "Bu mahnının sözlərini tapa bilmədim!"
    else:
        reply = "Mahnı tapılmadı!"
    if len(reply) > 4090:
        with open("lyrics.txt", "w") as f:
            f.write(f"{reply}")
        with open("lyrics.txt", "rb") as f:
            await v_url.client.send_file(
                v_url.chat_id,
                file=f,
                caption="Mesaj uzunluğu maksimum həddi keçdi! Mətn faylı kimi göndərilir.")
    else:
        await v_url.reply(reply)
