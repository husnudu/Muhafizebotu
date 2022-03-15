from typing import Optional

import LaylaRobot.modules.sql.rules_sql as sql
from LaylaRobot import dispatcher
from LaylaRobot.modules.helper_funcs.chat_status import user_admin
from LaylaRobot.modules.helper_funcs.string_handling import markdown_parser
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                      ParseMode, Update, User)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import escape_markdown


@run_async
def get_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    send_rules(update, chat_id)


# Do not async - not from a handler
def send_rules(update, chat_id, from_pm=False):
    bot = dispatcher.bot
    user = update.effective_user  # type: Optional[User]
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message == "Chat not found" and from_pm:
            bot.send_message(
                user.id,
                "Bu söhbət üçün qaydalar qısayolu düzgün qurulmayıb! Adminlərdən soruşun "
                "bunu düzəlt.\nBəlkə də şəxsiyyət vəsiqəsindəki unutdular")
            return
        else:
            raise

    rules = sql.get_rules(chat_id)
    text = f"Qaydalar *{escape_markdown(chat.title)}* üçün var:\n\n{rules}"

    if from_pm and rules:
        bot.send_message(
            user.id,
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
    elif from_pm:
        bot.send_message(
            user.id,
            "Qrup administratorları bu söhbət üçün hələ heç bir qayda təyin etməyiblər. "
            "Bu yəqin ki, qanunsuz olduğu anlamına gəlmir...!")
    elif rules:
        update.effective_message.reply_text(
            "Xahiş olunur qaydaları görmək üçün aşağıdakı düyməni vurun.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="Qaydalar", url=f"t.me/{bot.username}?start={chat_id}")
            ]]))
    else:
        update.effective_message.reply_text(
            "Qrup administratorları bu söhbət üçün hələ heç bir qayda təyin etməyiblər. "
            "Bu yəqin ki, qanunsuz olduğu anlamına gəlmir...!")


@run_async
@user_admin
def set_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    raw_text = msg.text
    args = raw_text.split(None,
                          1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(
            raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(
            txt, entities=msg.parse_entities(), offset=offset)

        sql.set_rules(chat_id, markdown_rules)
        update.effective_message.reply_text(
            "Bu qrup üçün uğurla qaydalar qurun.")


@run_async
@user_admin
def clear_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    update.effective_message.reply_text("Qaydalar uğurla silindi!")


def __stats__():
    return f"• {sql.num_chats()} söhbətlərin müəyyən edilmiş qaydaları var."


def __import_data__(chat_id, data):
    # set chat rules
    rules = data.get('info', {}).get('rules', "")
    sql.set_rules(chat_id, rules)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"Bu söhbətdə qaydalar müəyyən edilmişdir: `{bool(sql.get_rules(chat_id))}`"


__help__ = """
 • `/rules`*:* bu söhbət üçün qaydaları əldə edin.

*Admins only:*
 • `/setrules <qaydaların bura>`*:* bu söhbət üçün qaydaları təyin edin.
 • `/clearrules`*:* bu söhbət üçün qaydaları silin.
"""

__mod_name__ = "🛡Qaydalar"

GET_RULES_HANDLER = CommandHandler("rules", get_rules, filters=Filters.group)
SET_RULES_HANDLER = CommandHandler("setrules", set_rules, filters=Filters.group)
RESET_RULES_HANDLER = CommandHandler(
    "clearrules", clear_rules, filters=Filters.group)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
