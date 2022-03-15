import requests
import bs4 
import re
from telethon import *
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


@layla(pattern="^/app (.*)")
async def apk(e):
    if e.is_group:
     if not (await is_register_admin(e.input_chat, e.message.sender_id)):
          await e.reply("🙄Burda admin deyilsən .. Amma bu əmri pm-də istifadə edə bilərsən 😜🙈")
          return
    try:
        app_name = e.pattern_match.group(1)
        remove_space = app_name.split(' ')
        final_name = '+'.join(remove_space)
        page = requests.get("https://play.google.com/store/search?q="+final_name+"&c=apps")
        lnk = str(page.status_code)
        soup = bs4.BeautifulSoup(page.content,'lxml', from_encoding='utf-8')
        results = soup.findAll("div","ZmHEEd")
        app_name = results[0].findNext('div', 'Vpfmgd').findNext('div', 'WsMG1c nnK0zc').text
        app_dev = results[0].findNext('div', 'Vpfmgd').findNext('div', 'KoLSrc').text
        app_dev_link = "https://play.google.com"+results[0].findNext('div', 'Vpfmgd').findNext('a', 'mnKHRc')['href']
        app_rating = results[0].findNext('div', 'Vpfmgd').findNext('div', 'pf5lIe').find('div')['aria-label']
        app_link = "https://play.google.com"+results[0].findNext('div', 'Vpfmgd').findNext('div', 'vU6FJ p63iDd').a['href']
        app_icon = results[0].findNext('div', 'Vpfmgd').findNext('div', 'uzcko').img['data-src']
        app_details = "<a href='"+app_icon+"'>📲&#8203;</a>"
        app_details += " <b>"+app_name+"</b>"
        app_details += "\n\n<code>Yaradıcı :</code> <a href='"+app_dev_link+"'>"+app_dev+"</a>"
        app_details += "\n<code>Reytinq :</code> "+app_rating.replace("Qiymətləndirilib ", "⭐ ").replace(" out of ", "/").replace(" stars", "", 1).replace(" stars", "⭐ ").replace("five", "5")
        app_details += "\n<code>Xüsusiyyətləri :</code> <a href='"+app_link+"'>Play Mağazada baxın</a>"
        app_details += "\n\n 🍀 @AzRobotlar 🍀"
        await e.reply(app_details, link_preview = True, parse_mode = 'HTML')
    except IndexError:
        await e.reply("Axtarışda heç bir nəticə tapılmadı. Zəhmət olmasa **Etibarlı tətbiq adı daxil edin**")
    except Exception as err:
        await e.reply("İstisna baş verdi:- "+str(err))
