from LaylaRobot.modules.helper_funcs.telethn.chatstatus import (
    can_delete_messages, user_is_admin)
from LaylaRobot import telethn
import time
from telethon import events


@telethn.on(events.NewMessage(pattern="^[!/]purge$"))
async def purge_messages(event):
    start = time.perf_counter()
    if event.from_id is None:
        return

    if not await user_is_admin(
            user_id=event.from_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Bu əmrdən yalnız Adminlərin istifadəsinə icazə verilir🕹")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Mesajı təmizləmək görünmür")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply(
            "Təmizləməyə haradan başlayacağınızı seçmək üçün mesajı cavablandırın.")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    await event.client.delete_messages(event.chat_id, messages)
    time_ = time.perf_counter() - start
    text = f"Super Təmizləmə {time_:0.2f} saniyədə tamamlandı"
    await event.respond(text, parse_mode='markdown')


@telethn.on(events.NewMessage(pattern="^[!/]del$"))
async def delete_messages(event):
    if event.from_id is None:
        return

    if not await user_is_admin(
            user_id=event.from_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Bu əmrdən yalnız Adminlərin istifadəsinə icazə verilir🕹")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Bunu silməyi bilmirsən?")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("Nəyi silmək istəyirsən?")
        return
    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)

@telethn.on(events.NewMessage(pattern="^[!/]tagall$"))
async def tagging_powerful(event):
    mentions = "📢 Hərkas tağ olundu"
    chat = await event.get_input_chat()
    async for x in telethn.iter_participants(chat, 100):
        mentions += f"[\u2063](tg://user?id={x.id})"
    await event.reply(mentions)
    await event.delete()


__help__ = """
*Sadəcə adminlər:*
 - /del:  yanıtlanan mesajı silir
 - /purge:yanıtlanan mesajdan aşağıdakı bütün mesajları silir.
 - /purge <x ədədi>: yanıtlanan mesajdan aşağıdakı x sayda mesajı silir.
"""

__mod_name__ = "🗑Silinmə"
