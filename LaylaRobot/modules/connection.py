import time
import re

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update, Bot
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CommandHandler, CallbackQueryHandler, run_async, CallbackContext

import LaylaRobot.modules.sql.connection_sql as sql
from LaylaRobot import dispatcher, DRAGONS, DEV_USERS
from LaylaRobot.modules.helper_funcs import chat_status
from LaylaRobot.modules.helper_funcs.alternate import send_message, typing_action

user_admin = chat_status.user_admin


@user_admin
@run_async
@typing_action
def allow_connections(update, context) -> str:

    chat = update.effective_chat
    args = context.args

    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var == "no":
                sql.set_allow_connect_to_chat(chat.id, False)
                send_message(
                    update.effective_message,
                    "Bu söhbət üçün əlaqə deaktiv edildi",
                )
            elif var == "yes":
                sql.set_allow_connect_to_chat(chat.id, True)
                send_message(
                    update.effective_message,
                    "Bu söhbət üçün əlaqə aktiv edildi",
                )
            else:
                send_message(
                    update.effective_message,
                    "Zəhmət olmasa daxil edin `yes` or `no`!",
                    parse_mode=ParseMode.MARKDOWN,
                )
        else:
            get_settings = sql.allow_connect_to_chat(chat.id)
            if get_settings:
                send_message(
                    update.effective_message,
                    "Bu qrupa bağlantılar üzvlər üçün *İcazə* verilir!",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                send_message(
                    update.effective_message,
                    "Bu qrupa qoşulma üzvlər üçün *İcazəsizdir*!",
                    parse_mode=ParseMode.MARKDOWN,
                )
    else:
        send_message(update.effective_message,
                     "Bu əmr yalnız qrup üçündür. PM-də deyil!")


@run_async
@typing_action
def connection_chat(update, context):

    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=True)

    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type != "private":
            return
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if conn:
        message = "Hal hazırda bağlıdır{}.\n".format(chat_name)
    else:
        message = "Hal-hazırda heç bir qrupa bağlı deyilsiniz.\n"
    send_message(update.effective_message, message, parse_mode="markdown")


@run_async
@typing_action
def connect_chat(update, context):

    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if update.effective_chat.type == "private":
        if args and len(args) >= 1:
            try:
                connect_chat = int(args[0])
                getstatusadmin = context.bot.get_chat_member(
                    connect_chat, update.effective_message.from_user.id)
            except ValueError:
                try:
                    connect_chat = str(args[0])
                    get_chat = context.bot.getChat(connect_chat)
                    connect_chat = get_chat.id
                    getstatusadmin = context.bot.get_chat_member(
                        connect_chat, update.effective_message.from_user.id)
                except BadRequest:
                    send_message(update.effective_message, "Etibarsız Chat ID!")
                    return
            except BadRequest:
                send_message(update.effective_message, "Etibarsız Chat ID!")
                return

            isadmin = getstatusadmin.status in ("administrator", "creator")
            ismember = getstatusadmin.status in ("member")
            isallow = sql.allow_connect_to_chat(connect_chat)

            if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
                connection_status = sql.connect(
                    update.effective_message.from_user.id, connect_chat)
                if connection_status:
                    conn_chat = dispatcher.bot.getChat(
                        connected(
                            context.bot,
                            update,
                            chat,
                            user.id,
                            need_admin=False))
                    chat_name = conn_chat.title
                    send_message(
                        update.effective_message,
                        "Uğurla əlaqələndirildi *{}*. \nMövcud əmrləri yoxlamaq /helpconnect üçün istifadə edin"
                        .format(chat_name),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
                else:
                    send_message(update.effective_message, "Connection failed!")
            else:
                send_message(update.effective_message,
                             "Bu söhbətə qoşulmağa icazə verilmir!")
        else:
            gethistory = sql.get_history_conn(user.id)
            if gethistory:
                buttons = [
                    InlineKeyboardButton(
                        text="❎ Bağla düyməsini", callback_data="connect_close"),
                    InlineKeyboardButton(
                        text="🧹 Keçmişi silin", callback_data="connect_clear"),
                ]
            else:
                buttons = []
            conn = connected(
                context.bot, update, chat, user.id, need_admin=False)
            if conn:
                connectedchat = dispatcher.bot.getChat(conn)
                text = "Hal hazırda bağlıdır *{}* (`{}`)".format(
                    connectedchat.title, conn)
                buttons.append(
                    InlineKeyboardButton(
                        text="🔌 Ayırın",
                        callback_data="connect_disconnect"))
            else:
                text = "Qoşulmaq üçün söhbət kimliyini və ya etiketi yazın!"
            if gethistory:
                text += "\n\n*Bağlantı tarixi:*\n"
                text += "╒═══「 *İnfo* 」\n"
                text += "│  Çeşidləndi: Ən yeni`\n"
                text += "│\n"
                buttons = [buttons]
                for x in sorted(gethistory.keys(), reverse=True):
                    htime = time.strftime("%d/%m/%Y", time.localtime(x))
                    text += "╞═「 *{}* 」\n│   `{}`\n│   `{}`\n".format(
                        gethistory[x]["chat_name"], gethistory[x]["chat_id"],
                        htime)
                    text += "│\n"
                    buttons.append([
                        InlineKeyboardButton(
                            text=gethistory[x]["chat_name"],
                            callback_data="connect({})".format(
                                gethistory[x]["chat_id"]),
                        )
                    ])
                text += "╘══「 Ümumi {} Chatlar 」".format(
                    str(len(gethistory)) +
                    " (max)" if len(gethistory) == 5 else str(len(gethistory)))
                conn_hist = InlineKeyboardMarkup(buttons)
            elif buttons:
                conn_hist = InlineKeyboardMarkup([buttons])
            else:
                conn_hist = None
            send_message(
                update.effective_message,
                text,
                parse_mode="markdown",
                reply_markup=conn_hist,
            )

    else:
        getstatusadmin = context.bot.get_chat_member(
            chat.id, update.effective_message.from_user.id)
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(chat.id)
        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            connection_status = sql.connect(
                update.effective_message.from_user.id, chat.id)
            if connection_status:
                chat_name = dispatcher.bot.getChat(chat.id).title
                send_message(
                    update.effective_message,
                    "Uğurla əlaqələndirildi *{}*.".format(chat_name),
                    parse_mode=ParseMode.MARKDOWN,
                )
                try:
                    sql.add_history_conn(user.id, str(chat.id), chat_name)
                    context.bot.send_message(
                        update.effective_message.from_user.id,
                        "Siz bağlısınız *{}*. \nMövcud əmrləri yoxlamaq üçün `/helpconnect` istifadə edin."
                        .format(chat_name),
                        parse_mode="markdown",
                    )
                except BadRequest:
                    pass
                except Unauthorized:
                    pass
            else:
                send_message(update.effective_message, "Bağlantı alınmadı!")
        else:
            send_message(update.effective_message,
                         "Bu söhbətə qoşulmağa icazə verilmir!")


def disconnect_chat(update, context):

    if update.effective_chat.type == "private":
        disconnection_status = sql.disconnect(
            update.effective_message.from_user.id)
        if disconnection_status:
            sql.disconnected_chat = send_message(update.effective_message,
                                                 "Çat əlaqəsi kəsildi!")
        else:
            send_message(update.effective_message, "You're not connected!")
    else:
        send_message(update.effective_message,
                     "Bu əmr yalnız PM-də mövcuddur.")


def connected(bot: Bot, update: Update, chat, user_id, need_admin=True):
    user = update.effective_user

    if chat.type == chat.PRIVATE and sql.get_connected_chat(user_id):

        conn_id = sql.get_connected_chat(user_id).chat_id
        getstatusadmin = bot.get_chat_member(
            conn_id, update.effective_message.from_user.id)
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(conn_id)

        if ((isadmin) or (isallow and ismember) or (user.id in DRAGONS) or
            (user.id in DEV_USERS)):
            if need_admin is True:
                if (getstatusadmin.status in ("administrator", "creator") or
                        user_id in DRAGONS or user.id in DEV_USERS):
                    return conn_id
                else:
                    send_message(
                        update.effective_message,
                        "Bağlı qrupda bir admin olmalısınız!",
                    )
            else:
                return conn_id
        else:
            send_message(
                update.effective_message,
                "Qrup əlaqə hüquqlarını dəyişdirdi, yoxsa siz admin deyilsiniz.\nMən səni ayırdım.",
            )
            disconnect_chat(update, bot)
    else:
        return False


CONN_HELP = """
 Tədbirlər əlaqəli qruplarla mövcuddur:
 • Qeydlərə baxın və redaktə edin.
 • Filtrlərə baxın və redaktə edin.
 • Söhbətin dəvət linki alın.
 • AntiFlood parametrlərini qurun və idarə edin.
 • Qara siyahı parametrlərini qurun və idarə edin.
 • Söhbətin kilidlərini və kilidlərini açın.
 • Söhbəti əmrləri aktivləşdir və söndür.
 • Sohbet yedeklemesinin ixracı və idxalı.
 • Gələcəkdə daha çox!"""


@run_async
def help_connect_chat(update, context):

    args = context.args

    if update.effective_message.chat.type != "private":
        send_message(update.effective_message,
                     "PM me with that command to get help.")
        return
    else:
        send_message(update.effective_message, CONN_HELP, parse_mode="markdown")


@run_async
def connect_button(update, context):

    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user

    connect_match = re.match(r"connect\((.+?)\)", query.data)
    disconnect_match = query.data == "connect_disconnect"
    clear_match = query.data == "connect_clear"
    connect_close = query.data == "connect_close"

    if connect_match:
        target_chat = connect_match.group(1)
        getstatusadmin = context.bot.get_chat_member(target_chat,
                                                     query.from_user.id)
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(target_chat)

        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            connection_status = sql.connect(query.from_user.id, target_chat)

            if connection_status:
                conn_chat = dispatcher.bot.getChat(
                    connected(
                        context.bot, update, chat, user.id, need_admin=False))
                chat_name = conn_chat.title
                query.message.edit_text(
                    "Uğurla əlaqələndirildi *{}*. \nMövcud əmrləri yoxlamaq üçün `/helpconnect` istifadə edin."
                    .format(chat_name),
                    parse_mode=ParseMode.MARKDOWN,
                )
                sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
            else:
                query.message.edit_text("Bağlantı alınmadı!")
        else:
            context.bot.answer_callback_query(
                query.id,
                "Bu söhbətə qoşulmağa icazə verilmir!",
                show_alert=True)
    elif disconnect_match:
        disconnection_status = sql.disconnect(query.from_user.id)
        if disconnection_status:
            sql.disconnected_chat = query.message.edit_text(
                "Çat əlaqəsi kəsildi!")
        else:
            context.bot.answer_callback_query(
                query.id, "Bağlı deyilsiniz!", show_alert=True)
    elif clear_match:
        sql.clear_history_conn(query.from_user.id)
        query.message.edit_text("Bağlı tarix silindi!")
    elif connect_close:
        query.message.edit_text("Bağlı.\nYenidən açmaq üçün yazın /connect")
    else:
        connect_chat(update, context)


__mod_name__ = "🔁Əlaqələr"

__help__ = """
Bəzən, yalnız bir qrup söhbətinə bəzi qeydlər və filtrlər əlavə etmək istəyirsən, amma hamının görməsini istəmirsən; Bağlantıların daxil olduğu yer budur ...
Bu, bir sohbet verilənlər bazasına qoşulmağa və ona əmrlər görünmədən bir şey əlavə etməyə imkan verir! Məlum səbəblərdən, şeylər əlavə etmək üçün admin olmağınız lazımdır; lakin qrupdakı hər hansı bir üzv məlumatlarınızı görə bilər

 • /connect: Qrup ilə əlaqə yaradır (Qrupda /connect yazaraq
 • /connection: Qoşulmuş qrupların siyahısı
 • /disconnect: Qrup ilə əlaqəni kəsir
 • /helpconnect: Mövcud əmrləri göstərir

*Sadəcə adminlər:*
 • /allowconnect <yes/no>: Qoşulmaları aktiv/deaktiv edir
"""

CONNECT_CHAT_HANDLER = CommandHandler("connect", connect_chat, pass_args=True)
CONNECTION_CHAT_HANDLER = CommandHandler("connection", connection_chat)
DISCONNECT_CHAT_HANDLER = CommandHandler("disconnect", disconnect_chat)
ALLOW_CONNECTIONS_HANDLER = CommandHandler(
    "allowconnect", allow_connections, pass_args=True)
HELP_CONNECT_CHAT_HANDLER = CommandHandler("helpconnect", help_connect_chat)
CONNECT_BTN_HANDLER = CallbackQueryHandler(connect_button, pattern=r"connect")

dispatcher.add_handler(CONNECT_CHAT_HANDLER)
dispatcher.add_handler(CONNECTION_CHAT_HANDLER)
dispatcher.add_handler(DISCONNECT_CHAT_HANDLER)
dispatcher.add_handler(ALLOW_CONNECTIONS_HANDLER)
dispatcher.add_handler(HELP_CONNECT_CHAT_HANDLER)
dispatcher.add_handler(CONNECT_BTN_HANDLER)
