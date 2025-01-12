import re
from html import escape

import telegram
from telegram import ParseMode, InlineKeyboardMarkup, Message, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    DispatcherHandlerStop,
    CallbackQueryHandler,
    run_async,
    Filters,
)
from telegram.utils.helpers import mention_html, escape_markdown

from LaylaRobot import dispatcher, LOGGER, DRAGONS
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from LaylaRobot.modules.helper_funcs.chat_status import user_admin
from LaylaRobot.modules.helper_funcs.extraction import extract_text
from LaylaRobot.modules.helper_funcs.filters import CustomFilters
from LaylaRobot.modules.helper_funcs.misc import build_keyboard_parser
from LaylaRobot.modules.helper_funcs.msg_types import get_filter_type
from LaylaRobot.modules.helper_funcs.string_handling import (
    split_quotes,
    button_markdown_parser,
    escape_invalid_curly_brackets,
    markdown_to_html,
)
from LaylaRobot.modules.sql import cust_filters_sql as sql

from LaylaRobot.modules.connection import connected

from LaylaRobot.modules.helper_funcs.alternate import send_message, typing_action

HANDLER_GROUP = 10

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
    # sql.Types.VIDEO_NOTE.value: dispatcher.bot.send_video_note
}


@run_async
@typing_action
def list_handlers(update, context):
    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
        filter_list = "*Filtrlər  {}:*\n"
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Lokal filtrlər"
            filter_list = "*lokal filtrlər:*\n"
        else:
            chat_name = chat.title
            filter_list = "*Filtrlər {}*:\n"

    all_handlers = sql.get_chat_triggers(chat_id)

    if not all_handlers:
        send_message(update.effective_message,
                     "Heç bir filtr qeyd edilmədi {}!".format(chat_name))
        return

    for keyword in all_handlers:
        entry = " • `{}`\n".format(escape_markdown(keyword))
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            send_message(
                update.effective_message,
                filter_list.format(chat_name),
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            filter_list = entry
        else:
            filter_list += entry

    send_message(
        update.effective_message,
        filter_list.format(chat_name),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


# NOT ASYNC BECAUSE DISPATCHER HANDLER RAISED
@user_admin
@typing_action
def filters(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = msg.text.split(
        None,
        1)  # use python's maxsplit to separate Cmd, keyword, and reply_text

    conn = connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "local filters"
        else:
            chat_name = chat.title

    if not msg.reply_to_message and len(args) < 2:
        send_message(
            update.effective_message,
            "Zəhmət olmasa cavab vermək üçün bu filtrə klaviatura açar söz təqdim edin!",
        )
        return

    if msg.reply_to_message:
        if len(args) < 2:
            send_message(
                update.effective_message,
                "Zəhmət olmasa cavab vermək üçün bu filtr üçün açar söz verin!",
            )
            return
        else:
            keyword = args[1]
    else:
        extracted = split_quotes(args[1])
        if len(extracted) < 1:
            return
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()

    # Add the filter
    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in dispatcher.handlers.get(HANDLER_GROUP, []):
        if handler.filters == (keyword, chat_id):
            dispatcher.remove_handler(handler, HANDLER_GROUP)

    text, file_type, file_id = get_filter_type(msg)
    if not msg.reply_to_message and len(extracted) >= 2:
        offset = len(extracted[1]) - len(
            msg.text)  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            extracted[1], entities=msg.parse_entities(), offset=offset)
        text = text.strip()
        if not text:
            send_message(
                update.effective_message,
                "Qeyd mesajı yoxdur - SADƏCƏ düymələr ola bilməz, onunla getmək üçün bir mesaja ehtiyacınız var!",
            )
            return

    elif msg.reply_to_message and len(args) >= 2:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(text_to_parsing
                    )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset)
        text = text.strip()

    elif not text and not file_type:
        send_message(
            update.effective_message,
            "Zəhmət olmasa bu filtr cavabı üçün açar söz təqdim edin!",
        )
        return

    elif msg.reply_to_message:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(text_to_parsing
                    )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset)
        text = text.strip()
        if (msg.reply_to_message.text or
                msg.reply_to_message.caption) and not text:
            send_message(
                update.effective_message,
                "Qeyd mesajı yoxdur - SADƏCƏ düymələr ola bilməz, onunla getmək üçün bir mesaja ehtiyacınız var!",
            )
            return

    else:
        send_message(update.effective_message, "Invalid filter!")
        return

    add = addnew_filter(update, chat_id, keyword, text, file_type, file_id,
                        buttons)
    # This is an old method
    # sql.add_filter(chat_id, keyword, content, is_sticker, is_document, is_image, is_audio, is_voice, is_video, buttons)

    if add == True:
        send_message(
            update.effective_message,
            "Saxlanan filtr '{}' in *{}*!".format(keyword, chat_name),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    raise DispatcherHandlerStop


# NOT ASYNC BECAUSE DISPATCHER HANDLER RAISED
@user_admin
@typing_action
def stop_filter(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = update.effective_message.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Lokal filtrlər"
        else:
            chat_name = chat.title

    if len(args) < 2:
        send_message(update.effective_message, "Niə dayanım? MAL!")
        return

    chat_filters = sql.get_chat_triggers(chat_id)

    if not chat_filters:
        send_message(update.effective_message, "Burada filtr aktiv deyil!")
        return

    for keyword in chat_filters:
        if keyword == args[1]:
            sql.remove_filter(chat_id, args[1])
            send_message(
                update.effective_message,
                "Tamam, həmin filtrə cavab verməyi dayandıracağam *{}*.".format(
                    chat_name),
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            raise DispatcherHandlerStop

    send_message(
        update.effective_message,
        "Bu bir filtr deyil - Basın: /filters filtrləri əldə etmək üçündür.",
    )


@run_async
def reply_filter(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]

    if not update.effective_user or update.effective_user.id == 777000:
        return
    to_match = extract_text(message)
    if not to_match:
        return

    chat_filters = sql.get_chat_triggers(chat.id)
    for keyword in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            filt = sql.get_filter(chat.id, keyword)
            if filt.reply == "there is should be a new reply":
                buttons = sql.get_buttons(chat.id, filt.keyword)
                keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                VALID_WELCOME_FORMATTERS = [
                    "first",
                    "last",
                    "fullname",
                    "username",
                    "id",
                    "chatname",
                    "mention",
                ]
                if filt.reply_text:
                    valid_format = escape_invalid_curly_brackets(
                        filt.reply_text, VALID_WELCOME_FORMATTERS)
                    if valid_format:
                        filtext = valid_format.format(
                            first=escape(message.from_user.first_name),
                            last=escape(message.from_user.last_name or
                                        message.from_user.first_name),
                            fullname=" ".join(
                                [
                                    escape(message.from_user.first_name),
                                    escape(message.from_user.last_name),
                                ] if message.from_user.last_name else
                                [escape(message.from_user.first_name)]),
                            username="@" + escape(message.from_user.username)
                            if message.from_user.username else mention_html(
                                message.from_user.id,
                                message.from_user.first_name),
                            mention=mention_html(message.from_user.id,
                                                 message.from_user.first_name),
                            chatname=escape(message.chat.title)
                            if message.chat.type != "private" else escape(
                                message.from_user.first_name),
                            id=message.from_user.id,
                        )
                    else:
                        filtext = ""
                else:
                    filtext = ""

                if filt.file_type in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    try:
                        context.bot.send_message(
                            chat.id,
                            markdown_to_html(filtext),
                            reply_to_message_id=message.message_id,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        error_catch = get_exception(excp, filt, chat)
                        if error_catch == "noreply":
                            try:
                                context.bot.send_message(
                                    chat.id,
                                    markdown_to_html(filtext),
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Filtrlərdə xəta: " +
                                                 excp.message)
                                send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                        else:
                            try:
                                send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Mesaj göndərilmədi: " +
                                                 excp.message)
                                pass
                else:
                    ENUM_FUNC_MAP[filt.file_type](
                        chat.id,
                        filt.file_id,
                        caption=markdown_to_html(filtext),
                        reply_to_message_id=message.message_id,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )
                break
            else:
                if filt.is_sticker:
                    message.reply_sticker(filt.reply)
                elif filt.is_document:
                    message.reply_document(filt.reply)
                elif filt.is_image:
                    message.reply_photo(filt.reply)
                elif filt.is_audio:
                    message.reply_audio(filt.reply)
                elif filt.is_voice:
                    message.reply_voice(filt.reply)
                elif filt.is_video:
                    message.reply_video(filt.reply)
                elif filt.has_markdown:
                    buttons = sql.get_buttons(chat.id, filt.keyword)
                    keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                    keyboard = InlineKeyboardMarkup(keyb)

                    try:
                        send_message(
                            update.effective_message,
                            filt.reply,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        if excp.message == "Dəstəklənməyən url protokolu":
                            try:
                                send_message(
                                    update.effective_message,
                                    "Deyəsən dəstəklənməyən url protokolundan istifadə etməyə çalışırsınız. "
                                    "Telegram, tg kimi bəzi protokollar üçün düymələri dəstəkləmir://. Zəhmət olmasa cəhd edin "
                                    "yenidən...",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Filtrlərdə xəta: " +
                                                 excp.message)
                                pass
                        elif excp.message == "Reply message not found":
                            try:
                                context.bot.send_message(
                                    chat.id,
                                    filt.reply,
                                    parse_mode=ParseMode.MARKDOWN,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Filtrlərdə xəta: " +
                                                 excp.message)
                                pass
                        else:
                            try:
                                send_message(
                                    update.effective_message,
                                    "Bu mesaj səhv biçimləndiyindən göndərilə bilmədi.",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Filtrlərdə xəta: " +
                                                 excp.message)
                                pass
                            LOGGER.warning("Mesaj %s təhlil edilə bilmədi",
                                           str(filt.reply))
                            LOGGER.exception(
                                "Söhbətində %s filtri %s təhlil edilə bilmədi",
                                str(filt.keyword),
                                str(chat.id),
                            )

                else:
                    # LEGACY - all new filters will have has_markdown set to True.
                    try:
                        send_message(update.effective_message, filt.reply)
                    except BadRequest as excp:
                        LOGGER.exception("Filtrlərdə xəta: " + excp.message)
                        pass
                break


@run_async
def rmall_filters(update, context):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Yalnız söhbət sahibi bir anda bütün qeydləri silə bilər.")
    else:
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text="Bütün filtrləri dayandırın", callback_data="filters_rmall")
        ], [
            InlineKeyboardButton(text="Ləğv et", callback_data="filters_cancel")
        ]])
        update.effective_message.reply_text(
            f"BÜTÜN filtrləri dayandırmaq istədiyinizə əminsiniz {chat.title}? Bu əməliyyat geri qaytarıla bilməz.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN)


@run_async
def rmall_callback(update, context):
    query = update.callback_query
    chat = update.effective_chat
    msg = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == 'filters_rmall':
        if member.status == "creator" or query.from_user.id in DRAGONS:
            allfilters = sql.get_chat_triggers(chat.id)
            if not allfilters:
                msg.edit_text("Bu söhbətdə filtr olmadığından, dayanacaq bir şey yoxdur!")
                return

            count = 0
            filterlist = []
            for x in allfilters:
                count += 1
                filterlist.append(x)

            for i in filterlist:
                sql.remove_filter(chat.id, i)

            msg.edit_text(f"Təmizləndi{count} filters in {chat.title}")

        if member.status == "administrator":
            query.answer("Bunu yalnız söhbət sahibi edə bilər.")

        if member.status == "member":
            query.answer("Bunu etmək üçün admin olmalısınız.")
    elif query.data == 'filters_cancel':
        if member.status == "creator" or query.from_user.id in DRAGONS:
            msg.edit_text("Bütün filtrlərin təmizlənməsi ləğv edildi.")
            return
        if member.status == "administrator":
            query.answer("Bunu yalnız söhbət sahibi edə bilər.")
        if member.status == "member":
            query.answer("Bunu etmək üçün admin olmalısınız.")


# NOT ASYNC NOT A HANDLER
def get_exception(excp, filt, chat):
    if excp.message == "Dəstəklənməyən url protokolu":
        return "Deyəsən dəstəklənməyən URL protokolundan istifadə etməyə çalışırsınız. Telegram, tg: // kimi birdən çox protokol üçün açarı dəstəkləmir. Zəhmət olmasa bir daha cəhd edin!"
    elif excp.message == "Cavab mesajı tapılmadı":
        return "noreply"
    else:
        LOGGER.warning("Mesajlar %s təhlil edilə bilmədi", str(filt.reply))
        LOGGER.exception("%s Söhbətində %s filtri təhlil edilə bilmədi ",
                         str(filt.keyword), str(chat.id))
        return "Bu məlumatlar səhv formatlandığı üçün göndərilə bilmədi."


# NOT ASYNC NOT A HANDLER
def addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons):
    msg = update.effective_message
    totalfilt = sql.get_chat_triggers(chat_id)
    if len(totalfilt) >= 150:  # Idk why i made this like function....
        msg.reply_text("Bu qrup maksimum filtr limitinə 150-ə çatdı.")
        return False
    else:
        sql.new_add_filter(chat_id, keyword, text, file_type, file_id, buttons)
        return True


def __stats__():
    return "• {} filters, across {} chats.".format(sql.num_filters(),
                                                   sql.num_chats())


def __import_data__(chat_id, data):
    # set chat filters
    filters = data.get("filters", {})
    for trigger in filters:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    cust_filters = sql.get_chat_triggers(chat_id)
    return "Burada `{}` burada xüsusi filtrlər var.".format(len(cust_filters))


__help__ = """
 • `/filters`*:* Qurupdakı Cari Filter'ləri göstərir

*Admin Əmrləri:*
 • `/filter <açar söz > <mesaj>`*:* Bu söhbətə bir filtr əlavə edin. İndi bot 'açar söz' olduqda bu mesajı cavablandıracaq
qeyd olunur. Bir açar sözlə bir stikerə cavab verərsənsə, bot həmin stikerlə cavab verəcəkdir.
Açar sözünüzün bir cümlə olmasını istəyirsinizsə, sitatlardan istifadə edin. Məsələn: /filter "hey orada" necəsən?
    
Məsələn:
/filter "Açar söz" Açar söz yazılanda veriləcək mesaj

 • `/stop <söz>`*:* Filtri dayandırmaq
*Qeyd:* Takma adı olan filtrlər üçün bir təxəllüsü dayandırsanız, filtr digər takma adlar üzərində işləməyi dayandıracaq.
Misal üçün: Yuxarıdakı nümunədən "Açar söz 1" i dayandırsanız, bot "Açar söz 2" yə cavab verməyəcəkdir.

*Yalnız söhbət yaradıcısı:*
 • `/removeallfilters`*:* Bütün söhbət filtrlərini bir anda silin.

"""

__mod_name__ = "💬Filtrlər"

FILTER_HANDLER = CommandHandler("filter", filters)
STOP_HANDLER = CommandHandler("stop", stop_filter)
RMALLFILTER_HANDLER = CommandHandler(
    "removeallfilters", rmall_filters, filters=Filters.group)
RMALLFILTER_CALLBACK = CallbackQueryHandler(
    rmall_callback, pattern=r"filters_.*")
LIST_HANDLER = DisableAbleCommandHandler(
    "filters", list_handlers, admin_ok=True)
CUST_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & ~Filters.update.edited_message, reply_filter)

dispatcher.add_handler(FILTER_HANDLER)
dispatcher.add_handler(STOP_HANDLER)
dispatcher.add_handler(LIST_HANDLER)
dispatcher.add_handler(CUST_FILTER_HANDLER, HANDLER_GROUP)
dispatcher.add_handler(RMALLFILTER_HANDLER)
dispatcher.add_handler(RMALLFILTER_CALLBACK)

__handlers__ = [
    FILTER_HANDLER, STOP_HANDLER, LIST_HANDLER,
    (CUST_FILTER_HANDLER, HANDLER_GROUP, RMALLFILTER_HANDLER)
]
