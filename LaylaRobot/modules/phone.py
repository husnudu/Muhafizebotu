import sys
import requests
import json
import time
import urllib
import os
from LaylaRobot.laylabot import layla

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (await client(functions.channels.GetParticipantRequest(chat, user))).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await client.get_peer_id(user)
        ps = (await client(functions.messages.GetFullChatRequest(chat.chat_id))) \
            .full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator)
        )
    else:
        return None

@layla(pattern=r'^/nomre (.*)')
async def nomre(event): 
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
          await event.reply("☎️Admin deyilsen🚶‍♀️")
          return
    information = event.pattern_match.group(1)
    number = information
    key = "fe65b94e78fc2e3234c1c6ed1b771abd" 
    api = "http://apilayer.net/api/validate?access_key=" + key + "&number=" + number + "&country_code=&format=1"
    output = requests.get(api)
    content = output.text
    obj = json.loads(content)
    country_code = obj['country_code']
    country_name = obj['country_name']
    location = obj['location']
    carrier = obj['carrier']
    line_type = obj['line_type']	
    validornot = obj['valid']	
    aa = "Etibarlıdır: "+str(validornot)
    a = "Telefon nömrəsi: "+str(number)
    b = "Ölkə: " +str(country_code)
    c = "Ölkə Adı: " +str(country_name)
    d = "Yer: " +str(location)
    e = "Daşıyıcı: " +str(carrier)
    f = "Qurğu: " +str(line_type)
    g = f"{aa}\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}"
    await event.reply(g)
