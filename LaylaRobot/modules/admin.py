import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html, mention_markdown, escape_markdown

from LaylaRobot import DRAGONS, dispatcher
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from LaylaRobot.modules.helper_funcs.chat_status import (bot_admin, can_pin,
                                                           can_promote,
                                                           connection_status,
                                                           user_admin)
from LaylaRobot.modules.helper_funcs.extraction import (extract_user,
                                                          extract_user_and_text)
from LaylaRobot.modules.log_channel import loggable
from LaylaRobot.modules.helper_funcs.alternate import send_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if not (promoter.can_promote_members or
            promoter.status == "creator") and not user.id in DRAGONS:
        message.reply_text("Bunu etmək üçün lazımi hüquqlarınız yoxdur!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "Deyəsən bir istifadəçiyə istinad etmirsiniz və ya göstərilən identifikator səhvdir .."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text(
            "Onsuz da admin olan birini təbliğ etmək üçün necə düşünərəm?")
        return

    if user_id == bot.id:
        message.reply_text(
            "Mən özümü tanıda bilmərəm! Bunu etmək üçün bir admin alın.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages)
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(
                "Qrupda olmayan birini təbliğ edə bilmirəm.")
        else:
            message.reply_text("Tanıtım zamanı bir səhv baş verdi.")
        return

    bot.sendMessage(
        chat.id,
        f"Uğurla yüksəldi <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML)

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>İstifadəçi:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Görünür bir istifadəçiyə istinad etmirsiniz və ya göstərilən şəxsiyyət nömrəsi səhvdir.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == 'creator':
        message.reply_text(
            "Bu adam sohbəti SAHİBİDİ, onları necə vəzifəsindən aşağı salardım?")
        return

    if not user_member.status == 'administrator':
        message.reply_text("Vəzifəsi olmayan istifadəçini aşağı salmaq olmur!")
        return

    if user_id == bot.id:
        message.reply_text(
            "Özümün yetkisini alacaq qədər malam? Bunu mənim üçün etmək üçün sahib çağırın.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False)

        bot.sendMessage(
            chat.id,
            f"Uğurla dərəcəsi endirildi <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML)

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>İstifadəçi:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "Dərəcəsi endirilə bilmədi. Bəlkə admin olmaya bilərəm və ya admin statusu başqası tərəfindən təyin edilmişdir"
            " istifadəçi, buna görə də onlara əməl edə bilmirəm!")
        return


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "Deyəsən bir istifadəçiyə istinad etmirsiniz və ya göstərilən identifikator səhvdir .."
        )
        return

    if user_member.status == 'creator':
        message.reply_text(
            "Bu şəxs sohbəti YARATDI, onun üçün xüsusi başlıq necə təyin edə bilərəm?")
        return

    if not user_member.status == 'administrator':
        message.reply_text(
            "Admin olmayan şəxslər üçün başlıq təyin oluna bilməz!\nXüsusi başlıq təyin etmək üçün əvvəlcə onları admin edin!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "Öz başlığımı özüm təyin edə bilmirəm! Məni admin edəni mənə tapşırsın."
        )
        return

    if not title:
        message.reply_text("Boş başlıq qurmaq heç nə etmir!")
        return

    if len(title) > 16:
        message.reply_text(
            "Başlıq uzunluğu 16 simvoldan çoxdur\n16 simvol qədər kəsilir."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "Təqdim etmədiyim adminlər üçün xüsusi başlıq təyin edə bilmirəm!")
        return

    bot.sendMessage(
        chat.id,
        f"Başlığı uğurla təyin edildi <code>{user_member.user.first_name or user_id}</code> "
        f"üçün <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML)


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower()
                         == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id,
                prev_message.message_id,
                disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PINNED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNPINNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}")

    return log_message


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "Dəvət linkinə girişim yoxdur, icazələrimi dəyişdirməyə çalışın!"
            )
    else:
        update.effective_message.reply_text(
            "Sizə yalnız açıq qruplar və kanallar üçün dəvətlər verə bilərəm, üzr istəyirəm!"
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message,
                     "Bu əmr yalnız Qruplarda işləyir.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            'Qrup adminləri alınır ...', parse_mode=ParseMode.MARKDOWN)
    except BadRequest:
        msg = update.effective_message.reply_text(
            'Qrup adminləri alınır...',
            quote=False,
            parse_mode=ParseMode.MARKDOWN)

    administrators = bot.getChatAdministrators(chat_id)
    text = "Adminlər Budur *{}*:".format(update.effective_chat.title)

    bot_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == '':
            name = "☠ Hesab silindi"
        else:
            name = "{}".format(
                mention_markdown(user.id, user.first_name + " " +
                                 (user.last_name or "")))

        if user.is_bot:
            bot_admin_list.append(name)
            administrators.remove(admin)
            continue

        #if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Sahib:"
            text += "\n` • `{}\n".format(name)

            if custom_title:
                text += f"┗━ `{escape_markdown(custom_title)}`\n"

    text += "\n🔱 Adminlər:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == '':
            name = "☠ Hesab silindi"
        else:
            name = "{}".format(
                mention_markdown(user.id, user.first_name + " " +
                                 (user.last_name or "")))
        #if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n` • `{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n` • `{} | `{}`".format(custom_admin_list[admin_group][0],
                                              escape_markdown(admin_group))
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group in custom_admin_list:
        text += "\n🔘 `{}`".format(admin_group)
        for admin in custom_admin_list[admin_group]:
            text += "\n` • `{}".format(admin)
        text += "\n"

    text += "\n🤖 Botlar:"
    for each_bot in bot_admin_list:
        text += "\n` • `{}".format(each_bot)

    try:
        msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
 • `/admins`*:* Söhbətdəki idarəçilərin siyahısı

*Yalnız administratorlar:*
 • `/tagall`*:* Qrup üzvlərindən tağ edin
 • `/pin`*:* Səssizcə mesaja cavab verir - istifadəçilərə bildiriş vermək üçün "yüksək" və ya "bildir" əlavə edin.
 • `/unpin`*:*Hazırda sabitlənmiş mesajı açar
 • `/invitelink`*:*Link dəvətnaməsi alır
 • `/promote`*:*Yetki vermək istədiyiniz istifadəçiyə cavab verin
 • `/demote`*:*Yetki almaq istədiyiniz istifadəçiyə cavab verin
 • `/title <başlıq buraya>`*:* Botun təqdim etdiyi bir admin üçün xüsusi bir başlıq təyin edir
 • /zombies: Qrupunuzdakı silinmiş hesab sayını göstərir
 • /zombies clean: Silinmiş hesabları qrupdan çıxardın ..
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)

__mod_name__ = "👮🏻‍♂️Admin"
__command_list__ = ["adminlist", "admins", "invitelink", "promote", "demote"]
__handlers__ = [
    ADMINLIST_HANDLER, PIN_HANDLER, UNPIN_HANDLER, INVITE_HANDLER,
    PROMOTE_HANDLER, DEMOTE_HANDLER, SET_TITLE_HANDLER
]
