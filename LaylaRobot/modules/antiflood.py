import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatPermissions

from LaylaRobot import TIGERS, WOLVES, dispatcher
from LaylaRobot.modules.helper_funcs.chat_status import (
    bot_admin, can_restrict, connection_status, is_user_admin, user_admin,
    user_admin_no_reply)
from LaylaRobot.modules.log_channel import loggable
from LaylaRobot.modules.sql import antiflood_sql as sql
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, run_async
from telegram.utils.helpers import mention_html, escape_markdown
from LaylaRobot import dispatcher
from LaylaRobot.modules.helper_funcs.chat_status import is_user_admin, user_admin, can_restrict
from LaylaRobot.modules.helper_funcs.string_handling import extract_time
from LaylaRobot.modules.log_channel import loggable
from LaylaRobot.modules.sql import antiflood_sql as sql
from LaylaRobot.modules.connection import connected
from LaylaRobot.modules.helper_funcs.alternate import send_message
from LaylaRobot.modules.sql.approve_sql import is_approved

FLOOD_GROUP = 3


@run_async
@loggable
def check_flood(update, context) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]
    if not user:  # ignore channels
        return ""
    
    # ignore approves 
    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return ""

    # ignore admins and whitelists
    if (is_user_admin(chat, user.id) or user.id in WOLVES or user.id in TIGERS):
        sql.update_flood(chat.id, None)
        return ""

    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.kick_member(user.id)
            execstrings = ("Qadağa Olundu🚫")
            tag = "BAN"
        elif getmode == 2:
            chat.kick_member(user.id)
            chat.unban_member(user.id)
            execstrings = ("Atıldı🕺")
            tag = "ATILDI"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False))
            execstrings = ("Susduruldu🔇")
            tag = "SUS"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.kick_member(user.id, until_date=bantime)
            execstrings = ("Qadağa olunan istifadəçi {}".format(getvalue))
            tag = "TBAN"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False))
            execstrings = ("Susdurulan istifadəçi {}".format(getvalue))
            tag = "TMUTE"
        send_message(update.effective_message,
                     "CanCanadır CanCana Urfalıyam Həri🧑🏼‍🦱\n{}!".format(execstrings))

        return "<b>{}:</b>" \
               "\n#{}" \
               "\n<b>İstifadəçi:</b> {}" \
               "\nQrup Flooda Məruz Qaldı".format(tag, html.escape(chat.title),
                                             mention_html(user.id, html.escape(user.first_name)))

    except BadRequest:
        msg.reply_text(
            "Buradakı insanları məhdudlaşdıra bilmərəm, əvvəlcə yetki ver! O vaxta qədər daşqına qarşı mübarizəni deaktiv edəcəyəm."
        )
        sql.set_flood(chat.id, 0)
        return "<b>{}:</b>" \
               "\n#INFO" \
               "\nİstifadəçiləri məhdudlaşdırmaq üçün kifayət qədər icazəniz yoxdur, beləliklə flood əleyhinə avtomatik olaraq əlil edin".format(chat.title)


@run_async
@user_admin_no_reply
@bot_admin
def flood_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"unmute_flooder\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat.id
        try:
            bot.restrict_chat_member(
                chat,
                int(user_id),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True))
            update.effective_message.edit_text(
                f"Səssizdir {mention_html(user.id, html.escape(user.first_name))}.",
                parse_mode="HTML")
        except:
            pass


@run_async
@user_admin
@loggable
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(update.effective_message,
                         "Bu əmr özəl üçün deyil qrupda istifadə etmək üçündür")
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val == "off" or val == "no" or val == "0":
            sql.set_flood(chat_id, 0)
            if conn:
                text = message.reply_text(
                    "Flood əleyhinə qoruma deaktiv edildi {}.".format(chat_name))
            else:
                text = message.reply_text("Flood əleyhinə qoruma deaktiv edildi.")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = message.reply_text(
                        "Antiflood əleyhinə qoruma deaktiv edildi {}.".format(chat_name))
                else:
                    text = message.reply_text("Flood əleyhinə qoruma deaktiv edildi.")
                return "<b>{}:</b>" \
                       "\n#SETFLOOD" \
                       "\n<b>Admin:</b> {}" \
                       "\nAntiFlood Bağlandı.".format(html.escape(chat_name), mention_html(user.id, html.escape(user.first_name)))

            elif amount <= 3:
                send_message(
                    update.effective_message,
                    "Antiflood ya 0 (qeyri aktiv) ya da 3-dən böyük olmalıdır!"
                )
                return ""

            else:
                sql.set_flood(chat_id, amount)
                if conn:
                    text = message.reply_text(
                        "Daşqına qarşı söhbətdə {} olaraq təyin olundu: {}".format(
                            amount, chat_name))
                else:
                    text = message.reply_text(
                        "Daşqın əleyhinə limit {} səviyyəsinə uğurla yeniləndi!".format(
                            amount))
                return "<b>{}:</b>" \
                       "\n#FLOOD" \
                       "\n<b>Admin:</b> {}" \
                       "\nFlooda Qarşı Qur <code>{}</code>.".format(html.escape(chat_name),
                                                                    mention_html(user.id, html.escape(user.first_name)), amount)

        else:
            message.reply_text(
                "Yanlış arqument verildi. Yalnız ədədlər və ya 'off' 'no' istifadə edin'")
    else:
        message.reply_text((
            "Daşqının qarşısını almaq üçün `/setflood rəqəm` istifadə edin.\nvə ya antifloodu deaktiv etmək üçün `/setflood off` istifadə edin"
        ),
                           parse_mode="markdown")
    return ""


@run_async
def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(update.effective_message,
                         "Bu əmr özəldə deyil qrupda istifadə etmək üçündür")
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = msg.reply_text(
                "İçəridə daşqın nəzarətini tətbiq etmirəm {}!".format(chat_name))
        else:
            text = msg.reply_text("Mən burada heç bir flood nəzarətini tətbiq etmirəm!")
    else:
        if conn:
            text = msg.reply_text(
                "Hazırda ardıcıl {} mesajdan sonra üzvləri məhdudlaşdırıram {}."
                .format(limit, chat_name))
        else:
            text = msg.reply_text(
                "Hazırda ardıcıl {} mesajdan sonra üzvləri məhdudlaşdırıram."
                .format(limit))


@run_async
@user_admin
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(update.effective_message,
                         "Bu əmr özəl üçün deyil qrupda istifadə etmək üçündür")
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == 'ban':
            settypeflood = ('ban')
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == 'kick':
            settypeflood = ('kick')
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == 'mute':
            settypeflood = ('mute')
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == 'tban':
            if len(args) == 1:
                teks = """Deyəsən flooda qarşı vaxt dəyərini təyin etməyə çalışdınız, ancaq vaxt göstərmədiniz; Çalışın, "/flood rejimini <timevalue> -dən daha çox seçin".
Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = ("tban for {}".format(args[1]))
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == 'tmute':
            if len(args) == 1:
                teks = update.effective_message, """Deyəsən flooda qarşı vaxt dəyərini təyin etməyə çalışdınız, ancaq vaxt göstərmədiniz; Çalışın, "/flood rejimini <timevalue> -dən daha çox seçin`.

Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = ("tmute for {}".format(args[1]))
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(update.effective_message,
                         "Mən yalnız ban/kick/mute/tban/tmute başa düşürəm!")
            return
        if conn:
            text = msg.reply_text(
                "Ardıcıl daşqın limitini aşmaq {} ilə nəticələnəcəkdir{}!"
                .format(settypeflood, chat_name))
        else:
            text = msg.reply_text(
                "Ardıcıl daşqın limitini aşmaq {} ilə nəticələnəcəkdir!".format(
                    settypeflood))
        return "<b>{}:</b>\n" \
                "<b>Admin:</b> {}\n" \
                "Flood əleyhinə rejim dəyişdi. İstifadəçi edəcək {}.".format(settypeflood, html.escape(chat.title),
                                                                            mention_html(user.id, html.escape(user.first_name)))
    else:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            settypeflood = ('ban')
        elif getmode == 2:
            settypeflood = ('kick')
        elif getmode == 3:
            settypeflood = ('mute')
        elif getmode == 4:
            settypeflood = ('tban for {}'.format(getvalue))
        elif getmode == 5:
            settypeflood = ('tmute for {}'.format(getvalue))
        if conn:
            text = msg.reply_text(
                "Daşqın limitindən çox mesaj göndərməklə nəticələnəcəkdir{} ve {}."
                .format(settypeflood, chat_name))
        else:
            text = msg.reply_text(
                "Daşqın limitindən çox mesaj göndərməklə nəticələnəcəkdir {}."
                .format(settypeflood))
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "Daşqın nəzarətinə məcbur edilmir."
    else:
        return "Antiflood təyin edilmişdir`{}`.".format(limit)


__help__ = """
Antiflood sayəsində qrupunuza flood edənlərə qarşl müəyyən tədbirlər görə bilərsiniz

Eyni vaxtda 10 dan çox mesaj göndərənlər susdurulacaq. Bunu dəyişə də bilərsiniz.
 • `/flood`*:* Hazırki flood ayarını göstərir

• *•Sadəcə adminlər:y:*
 • `/setflood <int/'no'/'off'>`*:* : flood-a nəzarəti aktiv/deaktiv edir
 *Məsələn:* `/setflood 10`
 • `/setfloodmode <ban/kick/mute/tban/tmute> <dəyər>`*:* ood limitini keçənlərə qarşı ediləcək tədbirlər. ban/kick/mute/tmute/tban

• *Qeyd:*
 • tban və tmute üçün bir dəyər vermək məcburidir!!
 dəyərlər aşağıdakı kimi ola bilər:
 `5m` = 5 dəqiqə
 `6h` = 6 saat
 `3d` = 3 gün
 `1w` = 1 həftə
 """

__mod_name__ = "💦Anti-Flood"

FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.group, check_flood)
SET_FLOOD_HANDLER = CommandHandler("setflood", set_flood, filters=Filters.group)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, pass_args=True)  #, filters=Filters.group)
FLOOD_QUERY_HANDLER = CallbackQueryHandler(
    flood_button, pattern=r"unmute_flooder")
FLOOD_HANDLER = CommandHandler("flood", flood, filters=Filters.group)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(FLOOD_QUERY_HANDLER)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)

__handlers__ = [(FLOOD_BAN_HANDLER, FLOOD_GROUP), SET_FLOOD_HANDLER,
                FLOOD_HANDLER, SET_FLOOD_MODE_HANDLER]
