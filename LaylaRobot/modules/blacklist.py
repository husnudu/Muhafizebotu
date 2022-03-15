import html
import re

from telegram import ParseMode, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram.utils.helpers import mention_html

import LaylaRobot.modules.sql.blacklist_sql as sql
from LaylaRobot import dispatcher, LOGGER
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from LaylaRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from LaylaRobot.modules.helper_funcs.extraction import extract_text
from LaylaRobot.modules.helper_funcs.misc import split_message
from LaylaRobot.modules.log_channel import loggable
from LaylaRobot.modules.warns import warn
from LaylaRobot.modules.helper_funcs.string_handling import extract_time
from LaylaRobot.modules.connection import connected

from LaylaRobot.modules.helper_funcs.alternate import send_message, typing_action

BLACKLIST_GROUP = 11


@run_async
@user_admin
@typing_action
def blacklist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        else:
            chat_id = update.effective_chat.id
            chat_name = chat.title

    filter_list = "Cari qara siyahıya alınan sözlər<b>{}</b>:\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "Cari qara siyahıya alınan sözlər<b>{}</b>:\n".format(
                html.escape(chat_name)):
            send_message(
                update.effective_message,
                "Qara siyahıya alınmış söz yoxdur<b>{}</b>!".format(
                    html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@run_async
@user_admin
@typing_action
def add_blacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(
            set(trigger.strip()
                for trigger in text.split("\n")
                if trigger.strip()))
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "Qara siyahı əlavə edildi <code>{}</code> söhbətdə: <b>{}</b>!".format(
                    html.escape(to_blacklist[0]), html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "Qara siyahı tətiqləyicisi əlavə edildi: <code>{}</code> in <b>{}</b>!".format(
                    len(to_blacklist), html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )

    else:
        send_message(
            update.effective_message,
            "Qara siyahıya hansı sözləri əlavə etmək istədiyinizi deyin.",
        )


@run_async
@user_admin
@typing_action
def unblacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            set(trigger.strip()
                for trigger in text.split("\n")
                if trigger.strip()))
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "Qara <code>{}</code> siyahıdan silindi <b>{}</b>!"
                    .format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(update.effective_message,
                             "Bu qara siyahı tətiqləyicisi deyil!")

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "Qara <code>{}</code> siyahıdan silindi <b>{}</b>!".format(
                    successful, html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "Bu tətiqləyicisindən hec biri yoxdur, buna görə silinemez.".format(
                    successful,
                    len(to_unblacklist) - successful),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "Qara <code>{}</code> siyahıdan silindi.{} Mövcud deyildi, "
                "belə çıxarılmadı.".format(successful,
                                              len(to_unblacklist) - successful),
                parse_mode=ParseMode.HTML,
            )
    else:
        send_message(
            update.effective_message,
            "Qara siyahıdan hansı sözləri çıxarmaq istədiyinizi söyləyin!",
        )


@run_async
@loggable
@user_admin
@typing_action
def blacklist_mode(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "Bu əmr yalnız PM-də olmayan qrupda istifadə edilə bilər",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if (args[0].lower() == "off" or args[0].lower() == "nothing" or
                args[0].lower() == "no"):
            settypeblacklist = "do nothing"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() == "del" or args[0].lower() == "delete":
            settypeblacklist = "will delete blacklisted message"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "warn the sender"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "mute the sender"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "kick the sender"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ban the sender"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """Qara siyahı üçün vaxt dəyərini təyin etməyə çalışdınız, ancaq vaxt təyin etməmisiniz; Cəhd edin, `/blacklistmode tban <vaxtdəyəri>`.
				
Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Yanlış vaxt dəyəri!
Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "temporarily ban for {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """Qara siyahı üçün vaxt dəyərini təyin etməyə çalışdınız, ancaq vaxt təyin etməmisiniz; cəhd edin, `/blacklistmode tmute <vaxtdəyəri>`.

Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Yanlış vaxt dəyəri!
Vaxt dəyərinin nümunələri: 4m = 4 dəqiqə, 3h = 3 saat, 6d = 6 gün, 5w = 5 həftə."""
                send_message(
                    update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "temporarily mute for {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "Mən yalnız başa düşürəm: off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return ""
        if conn:
            text = "Dəyişdirilən qara siyahı rejimi:`{}` in *{}*!".format(
                settypeblacklist, chat_name)
        else:
            text = "Dəyişdirilən qara siyahı rejimi: `{}`!".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return ("<b>{}:</b>\n"
                "<b>Admin:</b> {}\n"
                "Qara siyahı rejimi dəyişdirildi. olacaq {}.".format(
                    html.escape(chat.title),
                    mention_html(user.id, html.escape(user.first_name)),
                    settypeblacklist,
                ))
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "do nothing"
        elif getmode == 1:
            settypeblacklist = "delete"
        elif getmode == 2:
            settypeblacklist = "warn"
        elif getmode == 3:
            settypeblacklist = "mute"
        elif getmode == 4:
            settypeblacklist = "kick"
        elif getmode == 5:
            settypeblacklist = "ban"
        elif getmode == 6:
            settypeblacklist = "üçün müvəqqəti qadağa {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "üçün müvəqqəti səssizdir {}".format(getvalue)
        if conn:
            text = "Cari qara siyahı rejimi: *{}* in *{}*.".format(
                settypeblacklist, chat_name)
        else:
            text = "Cari qara siyahı rejimi: *{}*.".format(settypeblacklist)
        send_message(
            update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@run_async
@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = extract_text(message)
    if not to_match:
        return

    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        ("Qara siyahıdakı tətiqləyicisi istifadəsi: {}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"Susduruldu {user.first_name} Qara Siyahıdakı sözün istifadəsi üçün: {trigger}!",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            f"Tulladım Səni {user.first_name} Qara Siyahıdakı sözün istifadəsi üçün: {trigger}!",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.kick_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"Banladım ay Mal {user.first_name} Qara Siyahıdakı sözün istifadəsi üçün {trigger}",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.kick_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"Qara siyahıdakı{user.first_name} Sözün istifadəsinə '{value}' qədər qadağa qoyulub {trigger}!",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"Susdurdum {user.first_name} səni '{value}' Qara Siyahıdakı sözün istifadəsi: {trigger}!",
                    )
                    return
            except BadRequest as excp:
                if excp.message == "Silmək üçün mesaj tapılmadı":
                    pass
                else:
                    LOGGER.exception("Qara siyahıdakı mesaj silinərkən xəta baş verdi.")
            break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "Qara siyahıya{} alınmış söz var..".format(blacklisted)


def __stats__():
    return "• {} blacklist triggers, across {} chats.".format(
        sql.num_blacklist_filters(), sql.num_blacklist_filter_chats())


__mod_name__ = "🆘Qara Siyahı"

__help__ = """

Siz Qara siyahının köməyi ilə qrupda müəyyən sözləri istifadə edənləri cəzalandıra bilərsiniz!


*QEYD*: Qara siyahı qrup adminlərinə təsir etmir.

 • `/blacklist`*:* qara siyahıdakı sözləri göstərir.

Admin only:
 • `/addblacklist <triggers>`*:* Qara siyahıya bir trigger əlavə edin. Hər sətir bir tetikleyici sayılır, buna görə fərqli sətirlərdən istifadə etmək çox tətik əlavə etməyə imkan verəcəkdir.
 • `/unblacklist <triggers>`*:* Triggerləri qara siyahıdan silin. Eyni yeni satır məntiqi burada tətbiq olunur, beləliklə birdən çox tətiyi silə bilərsiniz.
 • `/blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>`*:* AQara siyahıdakı sözləri istifadə edənlərə veriləcək cəza.

"""
BLACKLIST_HANDLER = DisableAbleCommandHandler(
    "blacklist", blacklist, pass_args=True, admin_ok=True)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist)
UNBLACKLIST_HANDLER = CommandHandler("unblacklist", unblacklist)
BLACKLISTMODE_HANDLER = CommandHandler(
    "blacklistmode", blacklist_mode, pass_args=True)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo)
    & Filters.group,
    del_blacklist,
    allow_edit=True,
)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER, ADD_BLACKLIST_HANDLER, UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER, (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP)
]
