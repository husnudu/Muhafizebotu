import datetime
from typing import List

import requests
from LaylaRobot import TIME_API_KEY
from LaylaRobot.laylabot import layla
from telethon import types
from telethon.tl import functions


def generate_time(to_find: str, findtype: List[str]) -> str:
    data = requests.get(
        f"http://api.timezonedb.com/v2.1/list-time-zone"
        f"?key={TIME_API_KEY}"
        f"&format=json"
        f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
    ).json()

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                country_name = zone["countryName"]
                country_zone = zone["zoneName"]
                country_code = zone["countryCode"]

                if zone["dst"] == 1:
                    daylight_saving = "Yes"
                else:
                    daylight_saving = "No"

                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=gmt_offset)
                current_date = timestamp.strftime(date_fmt)
                current_time = timestamp.strftime(time_fmt)
                current_day = timestamp.strftime(day_fmt)

                break

    try:
        result = (
            f"<b>🌍Ölkə :</b> <code>{country_name}</code>\n"
            f"<b>⏳Zona Adı :</b> <code>{country_zone}</code>\n"
            f"<b>🗺Ölkə Kodu :</b> <code>{country_code}</code>\n"
            f"<b>🌞Yaz işığı :</b> <code>{daylight_saving}</code>\n"
            f"<b>🌅Gün :</b> <code>{current_day}</code>\n"
            f"<b>⌚Cari vaxt:</b> <code>{current_time}</code>\n"
            f"<b>📆Hal-hazırki Tarix :</b> <code>{current_date}</code>"
        )
    except BaseException:
        result = None

    return result

@layla(pattern="^/datetime")
async def _(event):
    if event.fwd_from:
        return

    message = event.text

    try:
        query = message.strip().split(" ", 1)[1]
    except BaseException:
        await event.reply("Tapmaq üçün bir ölkə adı/qısaltması/saat qurşağı verin.")
        return
    send_message = await event.reply(
        f"saat qurşağı məlumatı axtarılır <b>{query}</b>", parse_mode="html"
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = generate_time(query_timezone, ["countryCode"])
    else:
        result = generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        await send_message.edit(
            f"Saat qurşağı haqqında məlumat mövcud deyil <b>{query}</b>", parse_mode="html"
        )
        return

    await send_message.edit(result, parse_mode="html")
