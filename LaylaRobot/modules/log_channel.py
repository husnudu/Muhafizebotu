from datetime import datetime
from functools import wraps

from telegram.ext import CallbackContext

from LaylaRobot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import ParseMode, Update
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, JobQueue, run_async
    from telegram.utils.helpers import escape_markdown

    from LaylaRobot import EVENT_LOGS, LOGGER, dispatcher
    from LaylaRobot.modules.helper_funcs.chat_status import user_admin
    from LaylaRobot.modules.sql import log_channel_sql as sql

    def loggable(func):

        @wraps(func)
        def log_action(update: Update,
                       context: CallbackContext,
                       job_queue: JobQueue = None,
                       *args,
                       **kwargs):
            if not job_queue:
                result = func(update, context, *args, **kwargs)
            else:
                result = func(update, context, job_queue, *args, **kwargs)

            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += f"\n<b>Tədbir damğası</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">click here</a>'
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return log_action

    def gloggable(func):

        @wraps(func)
        def glog_action(update: Update, context: CallbackContext, *args,
                        **kwargs):
            result = func(update, context, *args, **kwargs)
            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += "\n<b>Tədbir damğası</b>: <code>{}</code>".format(
                    datetime.utcnow().strftime(datetime_fmt))

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">click here</a>'
                log_chat = str(EVENT_LOGS)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return glog_action

    def send_log(context: CallbackContext, log_chat_id: str, orig_chat_id: str,
                 result: str):
        bot = context.bot
        try:
            bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)
        except BadRequest as excp:
            if excp.message == "Çat tapılmadı":
                bot.send_message(
                    orig_chat_id,
                    "Bu günlük kanal silindi - ayarlanmadı.")
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Could not parse")

                bot.send_message(
                    log_chat_id, result +
                    "\n\nFormatlaşdırma gözlənilməz səhv səbəbindən deaktiv edildi."
                )

    @run_async
    @user_admin
    def logging(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                f"Bu qrupda göndərilən bütün qeydlər var:"
                f" {escape_markdown(log_channel_info.title)} (`{log_channel}`)",
                parse_mode=ParseMode.MARKDOWN)

        else:
            message.reply_text("Bu qrup üçün giriş kanalı təyin edilməyib!")

    @run_async
    @user_admin
    def setlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat
        if chat.type == chat.CHANNEL:
            message.reply_text(
                "İndi /setlog əmrini bağlamaq istədiyiniz kanala yönlənirin"
            )

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Silmək üçün mesaj tapılmadı":
                    pass
                else:
                    LOGGER.exception(
                        "Giriş kanalındakı mesaj silinərkən xəta baş verdi. Hər halda işləməli."
                    )

            try:
                bot.send_message(
                    message.forward_from_chat.id,
                    f"Bu Kanal log kanalı olaraq təyin edilmişdir {chat.title or chat.first_name}."
                )
            except Unauthorized as excp:
                if excp.message == "Qadağandır: bot kanal söhbətinin üzvü deyil":
                    bot.send_message(chat.id, "Log kanalı uğurla quruldu!")
                else:
                    LOGGER.exception("Log kanalını qurarkən XATA.")

            bot.send_message(chat.id, "Log kanalı uğurla quruldu!")

        else:
            message.reply_text("Bir log kanalı qurmaq üçün addımlar bunlardır: \n "
                                "- istənilən kanala bot əlavə edin \n"
                                "- kanala /setlog yazın\n"
                                "- /setlog u qrupa yönləndirin\n")

    @run_async
    @user_admin
    def unsetlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(log_channel,
                             f"Kanal əlaqəsi kəsildi {chat.title}")
            message.reply_text("Log kanalı ayarlanmamışdır.")

        else:
            message.reply_text("Hələ log kanalı qurulmayıb!")

    def __stats__():
        return f"• {sql.num_logchannels()} log kanalları quruldu."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return f"Bu qrupda göndərilən bütün qeydlər var: {escape_markdown(log_channel_info.title)} (`{log_channel}`)"
        return "Bu qrup üçün log kanalı təyin edilməyib!"

    __help__ = """
*Administratorlar:*
• `/logchannel`:  giriş kanalı məlumatlarını əldə edin
• `/setlog`: giriş kanalını qurun.
• `/unsetlog`:  giriş kanalını sıfırlayın.

Giriş kanalının qurulması aşağıdakılardır:
• botu istədiyiniz kanala əlavə etmək (admin olaraq!)
• kanalda `/setlog` göndərilməsi
• `/setlog` u qrupa yönləndirmək
"""

    __mod_name__ = "🧰Loq"

    LOG_HANDLER = CommandHandler("logchannel", logging)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func

    def gloggable(func):
        return func
