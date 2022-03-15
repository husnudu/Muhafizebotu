import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from LaylaRobot import (DEV_USERS, LOGGER, OWNER_ID, DRAGONS, DEMONS, TIGERS,
                          WOLVES, dispatcher)
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from LaylaRobot.modules.helper_funcs.chat_status import (
    bot_admin, can_restrict, connection_status, is_user_admin,
    is_user_ban_protected, is_user_in_chat, user_admin, user_can_ban)
from LaylaRobot.modules.helper_funcs.extraction import extract_user_and_text
from LaylaRobot.modules.helper_funcs.string_handling import extract_time
from LaylaRobot.modules.log_channel import gloggable, loggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Belə istifadəçi olduğuna şübhə edirəm.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçini tapa bilədim":
            message.reply_text("Bu adamı tapa bilmirəm.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Oh Yeah, özümü qadağan edirəm gözlə😂") 
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text(
                "Məni Tanrı səviyyəsində bir fəlakətə qarşı qoymağa çalışırsan ha?")
            return log_message
        elif user_id in DEV_USERS:
            message.reply_text("Mən özümüzə qarşı hərəkət edə bilmərəm.")
            return log_message
        elif user_id in DRAGONS:
            message.reply_text(
                "Bu Ejderha ilə mübarizə, mülki həyatını riskə atacaq.")
            return log_message
        elif user_id in DEMONS:
            message.reply_text(
                "Bir Şeytan fəlakətcisi ilə mübarizə aparmaq üçün @AzRobotGroup dərnəyindən bir sifariş gətirin."
            )
            return log_message
        elif user_id in TIGERS:
            message.reply_text(
                "Bir Pələng fəlakətcisi ilə mübarizə aparmaq üçün @AzRobotGroup dərnəyindən bir sifariş gətirin."
            )
            return log_message
        elif user_id in WOLVES:
            message.reply_text("Canavar qabiliyyətləri onları immunitetə qadağa qoyur!")
            return log_message
        else:
            message.reply_text("Bu istifadəçinin toxunulmazlığı var və qadağan edilə bilməz.")
            return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#QADAĞA🚫\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>Cavan Getdi😒</b>\n"
            f"<code> </code><b>•  İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  Səbəb🗣:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML, quote=False)
        return log

    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text('Qəşəy,Banlandı Artıq!', quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("Xəta səbəbiylə %s söhbətdə %s (%s) qadağan etdi %s",
                             user_id, chat.title, chat.id, excp.message)
            message.reply_text("Uhm ...işə yaramadı ... ")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Belə istifadəçi olduğuna şübhə edirəm.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Görünür bu istifadəçini tapa bilmirəm.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Mən özüm QƏNAƏT ETMƏYƏMƏM, dəli olmusan?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Mən bunu hiss etmirəm.")
        return log_message

    if not reason:
        message.reply_text("Bu istifadəçini qadağan edəcək bir vaxt təyin etməmisiniz!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#QADAĞA🚫\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Vaxt:</b> {time_val}")
    if reason:
        log += "\n<b>Səbəb:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Qadağan olan! İstifadəçi {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"üçün qadağan ediləcək{time_val}.",
            parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text(
                f"Qadağandır! İstifadəçi qadağan olunacaq {time_val}.", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("Xəta səbəbiylə %s söhbətdə %s (%s) qadağan etdi %s",
                             user_id, chat.title, chat.id, excp.message)
            message.reply_text("Toba, o istifadəçini qadağan edə bilmərəm")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Belə istifadəçi olduğuna şübhə edirəm.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Görünür bu istifadəçini tapa bilmirəm.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Bəli, bunu etməyəcəyəm.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Bu istifadəçini təpikləməyimi çox istərdim....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Atdım! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML)
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#Atıldı\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Səbəb:</b> {reason}"

        return log

    else:
        message.reply_text("Malsan?, mən o istifadəçini ata bilmirəm.")

    return log_message


@run_async
@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text(
            "Kaş biləydim etağa ... amma adminsən.")
        return

    res = update.effective_chat.unban_member(
        user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*səni qrupdan qovur*")
    else:
        update.effective_message.reply_text("Hə? Bacarmıram:/")


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Belə istifadəçi olduğuna şübhə edirəm.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Görünür bu istifadəçini tapa bilmirəm.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Burda olmasaydım özümü necə açardım...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Bu adam artıq burda deyil??")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Yep, bu istifadəçi qoşula bilər!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#BanAçıldı\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Səbəb:</b> {reason}"

    return log


@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Etibarlı söhbət id verin.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Görünür bu istifadəçini tapa bilmirəm.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Onsuz da burda deyilsənki???")
        return

    chat.unban_member(user.id)
    message.reply_text("Yep, səni qadağan etmişəm qırıl.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#BanAçıldı\n"
        f"<b>İstifadəçi:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


__help__ = """
 • `/punchme`*:* bu əmri işlədən istifadəçini qrupdan atır

*Sadəcə adminlər:*
 • `/ban <istifadəçi>`*:*  istifadəçini banlayır. (ID,taq vasitəsilə və ya cavab verin)
 • `/tban <istifadəçi> x(m/h/d)`*:*  x(m/h/d): istifadəçini x müddətlik banlayır. m = dəqiqə, h = saat, d = gün.
 • `/unban <istifadəçi>`*:*  istifadəçinin banını açır.
 • `/kick <istifadəçi>`*:* istifadəçini qrupdan atır.
"""

BAN_HANDLER = CommandHandler("ban", ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
KICK_HANDLER = CommandHandler("kick", kick)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kick", kickme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)

__mod_name__ = "⛔️Ban"
__handlers__ = [
    BAN_HANDLER, TEMPBAN_HANDLER, KICK_HANDLER, UNBAN_HANDLER, ROAR_HANDLER,
    KICKME_HANDLER
]
