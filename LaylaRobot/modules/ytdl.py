import os
import time
import math
import asyncio
import shutil
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from telethon.tl.types import DocumentAttributeAudio
from collections import deque
from googleapiclient.discovery import build
from LaylaRobot.laylabot import layla
from LaylaRobot import YOUTUBE_API_KEY
from html import unescape
import requests



@layla(pattern="^/yt(mahni|video) (.*)")
async def download_video(v_url):
    """ For .ytdl command, download media from YouTube and many other sites. """
    url = v_url.pattern_match.group(2)
    type = v_url.pattern_match.group(1).lower()
    lmao = await v_url.reply("`Yükləməyə hazırlaşır ...`")
    if type == "mahni":
        opts = {
            'format':
            'bestaudio',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'writethumbnail':
            True,
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'outtmpl':
            '%(id)s.mp3',
            'quiet':
            True,
            'logtostderr':
            False
        }
        video = False
        mahni = True
    elif type == "video":
        opts = {
            'format':
            'best',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
            '%(id)s.mp4',
            'logtostderr':
            False,
            'quiet':
            True
        }
        mahni = False
        video = True
    try:
        await lmao.edit("`Məlumat alınır, xahiş edirəm gözləyin ..💃🏻`")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await lmao.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await lmao.edit("`Endirmə məzmunu çox qısa idi.`")
        return
    except GeoRestrictedError:
        await lmao.edit(
            "`Veb sayt tərəfindən qoyulmuş coğrafi məhdudiyyətlər səbəbindən video coğrafi məkandan əldə edilə bilməz.`"
        )
        return
    except MaxDownloadsReached:
        await lmao.edit("`Maksimum yükləmə limitinə çatıldı.`")
        return
    except PostProcessingError:
        await lmao.edit("`Sonrakı işləmə zamanı bir xəta baş verdi.`")
        return
    except UnavailableVideoError:
        await lmao.edit("`Media tələb olunan formatda mövcud deyil.`")
        return
    except XAttrMetadataError as XAME:
        await lmao.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await lmao.edit("`Məlumat çıxarılması zamanı xəta baş verdi.`")
        return
    except Exception as e:
        await lmao.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if mahni:
        await lmao.edit(f"`Mahnı yükləməyə hazırlaşır:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{ytdl_data['id']}.mp3",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(duration=int(ytdl_data['duration']),
                                       title=str(ytdl_data['title']),
                                       performer=str(ytdl_data['uploader']))
            ])
        os.remove(f"{ytdl_data['id']}.mp3")
    elif video:
        await lmao.edit(f"`Video yükləməyə hazırlaşır:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{ytdl_data['id']}.mp4",
            supports_streaming=True,
            caption=ytdl_data['title'])
        os.remove(f"{ytdl_data['id']}.mp4")
      
__help__ = """
 • `/mahni`** <mahnı adı>: umahnını ən yaxşı keyfiyyətdə yükləyir. 
 
 • `/video`** <video adı>: video mahnını ən yaxşı keyfiyyətdə yükləyir.
 
 • `/lyrics`** <mahnı adı,sənətkarı(istəyə bağlıdır)>: giriş olaraq verilən mahnının tam sözlərini göndərir
 
 • `/ytmahni`** <link> yaxud `/ytvideo`** <link>: Bir youtube mahnı,videosu link vasitesi ilə ən yaxşı keyfiyyətdə yükəyir
"""
__mod_name__ = "🎵Musiqi"
