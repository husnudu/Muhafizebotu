import requests
import wikipedia
from emoji import UNICODE_EMOJI
from googletrans import LANGUAGES, Translator
from LaylaRobot.modules.helper_funcs.chat_status import user_admin
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from LaylaRobot import dispatcher

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import MessageEntity, ParseMode, Update
from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext, Filters, CommandHandler
from wikipedia.exceptions import DisambiguationError, PageError

MARKDOWN_HELP = f"""
Markdown, telegram tərəfindən dəstəklənən çox güclü bir formatlaşdırma vasitəsidir. {dispatcher.bot.first_name} əmin olmaq üçün bəzi inkişaflara malikdir \
qeyd edilmiş mesajlar düzgün təhlil olunur və düymələr yaratmağınıza imkan verir.

• <code>_italic_</code>: mətni sarma '_' italik mətn çıxaracaq
• <code>*bold*</code>: mətni sarma '*' qalın mətn çıxaracaq
• <code>`code`</code>: mətni sarma '`' kimi də bilinən tək aralı mətn çıxaracaq 'code'
• <code>[yazı](URL)</code>: bu bir əlaqə yaradacaq - mesaj yalnız bir müddət <code> göstərəcəkdir</code>, \
və üzərinə vurmaq səhifəni <code> bəzi URL-lərdə açacaqdır</code>.
<b>Misal:</b><code>[test](misal.com)</code>

• <code>[buton yazısı](buttonurl:bəziURL)</code>: bu istifadəçilərin teleqrama sahib olmasına imkan verən xüsusi bir inkişafdır \
işarələrindəki düymələr. <code>buttontext</code> düyməsində görünən nə olacaq və <code>URL</code> \
açılmış url olacaqdır.
<b>Misal:</b> <code>[Bu Butondur](buttonurl:misal.com)</code>

Eyni sətirdə birdən çox düymə istəyirsinizsə, istifadə edin: eyni, belə:
<code>[bir](buttonurl://misal.com)
[iki](buttonurl://google.com:bənzər)</code>
Bu, hər sətirdə bir düymə əvəzinə bir sətirdə iki düymə yaradacaqdır.

Unutmayın ki, mesajınız yalnız bir düymədən  <b>MÜTLƏQ</b> başqa bir neçə mətn ehtiva edir. 
"""

@run_async
def ud(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text[len('/ud '):]
    results = requests.get(
        f'https://api.urbandictionary.com/v0/define?term={text}').json()
    try:
        reply_text = f'*{text}*\n\n{results["list"][0]["definition"]}\n\n_{results["list"][0]["example"]}_'
    except:
        reply_text = "Heç bir nəticə tapılmadı."
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


@run_async
def wiki(update: Update, context: CallbackContext):
    msg = update.effective_message.reply_to_message if update.effective_message.reply_to_message else update.effective_message
    res = ""
    if msg == update.effective_message:
        search = msg.text.split(" ", maxsplit=1)[1]
    else:
        search = msg.text
    try:
        res = wikipedia.summary(search)
    except DisambiguationError as e:
        update.message.reply_text(
            "Ayrılmış səhifələr tapıldı! Sorğunuzu uyğun olaraq tənzimləyin.\n<i>{}</i>"
            .format(e),
            parse_mode=ParseMode.HTML)
    except PageError as e:
        update.message.reply_text(
            "<code>{}</code>".format(e), parse_mode=ParseMode.HTML)
    if res:
        result = f"<b>{search}</b>\n\n"
        result += f"<i>{res}</i>\n"
        result += f"""<a href="https://az.wikipedia.org/wiki/{search.replace(" ", "%20")}">Daha çox oxu...</a>"""
        if len(result) > 4000:
            with open("result.txt", 'w') as f:
                f.write(f"{result}\n\nUwU OwO OmO UmU")
            with open("result.txt", 'rb') as f:
                context.bot.send_document(
                    document=f,
                    filename=f.name,
                    reply_to_message_id=update.message.message_id,
                    chat_id=update.effective_chat.id,
                    parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)


@run_async
@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True)
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode="MARKDOWN",
            disable_web_page_preview=True)
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(
        MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Aşağıdakı mesajı mənə ötürməyə çalışın, sonra da istifadə edin #test!"
    )
    update.effective_message.reply_text(
        "/testi saxla Bu qeyddirtest. __əyri__, *qalın*, code, "
        "[URL](misal.com) [button](buttonurl:instagram.com) "
        "[button2](buttonurl://google.com:bənzər)")


@run_async
def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            'Özəldən mənə müraciət edin',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "Markdown kömək",
                    url=f"t.me/{context.bot.username}?start=markdownhelp")
            ]]))
        return
    markdown_help_sender(update)


@run_async
def totranslate(update: Update, context: CallbackContext):
    msg = update.effective_message
    problem_lang_code = []
    for key in LANGUAGES:
        if "-" in key:
            problem_lang_code.append(key)
    try:
        if msg.reply_to_message:
            args = update.effective_message.text.split(None, 1)
            if msg.reply_to_message.text:
                text = msg.reply_to_message.text
            elif msg.reply_to_message.caption:
                text = msg.reply_to_message.caption

            message = update.effective_message
            dest_lang = None

            try:
                source_lang = args[1].split(None, 1)[0]
            except:
                source_lang = "en"

            if source_lang.count('-') == 2:
                for lang in problem_lang_code:
                    if lang in source_lang:
                        if source_lang.startswith(lang):
                            dest_lang = source_lang.rsplit("-", 1)[1]
                            source_lang = source_lang.rsplit("-", 1)[0]
                        else:
                            dest_lang = source_lang.split("-", 1)[1]
                            source_lang = source_lang.split("-", 1)[0]
            elif source_lang.count('-') == 1:
                for lang in problem_lang_code:
                    if lang in source_lang:
                        dest_lang = source_lang
                        source_lang = None
                        break
                if dest_lang is None:
                    dest_lang = source_lang.split("-")[1]
                    source_lang = source_lang.split("-")[0]
            else:
                dest_lang = source_lang
                source_lang = None

            exclude_list = UNICODE_EMOJI.keys()
            for emoji in exclude_list:
                if emoji in text:
                    text = text.replace(emoji, '')

            trl = Translator()
            if source_lang is None:
                detection = trl.detect(text)
                tekstr = trl.translate(text, dest=dest_lang)
                return message.reply_text(
                    f"Tərcümə edilmişdir `{detection.lang}` to `{dest_lang}`:\n`{tekstr.text}`",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                tekstr = trl.translate(text, dest=dest_lang, src=source_lang)
                message.reply_text(
                    f"Tərcümə edilmişdir `{source_lang}` to `{dest_lang}`:\n`{tekstr.text}`",
                    parse_mode=ParseMode.MARKDOWN)
        else:
            args = update.effective_message.text.split(None, 2)
            message = update.effective_message
            source_lang = args[1]
            text = args[2]
            exclude_list = UNICODE_EMOJI.keys()
            for emoji in exclude_list:
                if emoji in text:
                    text = text.replace(emoji, '')
            dest_lang = None
            temp_source_lang = source_lang
            if temp_source_lang.count('-') == 2:
                for lang in problem_lang_code:
                    if lang in temp_source_lang:
                        if temp_source_lang.startswith(lang):
                            dest_lang = temp_source_lang.rsplit("-", 1)[1]
                            source_lang = temp_source_lang.rsplit("-", 1)[0]
                        else:
                            dest_lang = temp_source_lang.split("-", 1)[1]
                            source_lang = temp_source_lang.split("-", 1)[0]
            elif temp_source_lang.count('-') == 1:
                for lang in problem_lang_code:
                    if lang in temp_source_lang:
                        dest_lang = None
                        break
                    else:
                        dest_lang = temp_source_lang.split("-")[1]
                        source_lang = temp_source_lang.split("-")[0]
            trl = Translator()
            if dest_lang is None:
                detection = trl.detect(text)
                tekstr = trl.translate(text, dest=source_lang)
                return message.reply_text(
                    "Tərcümə edilmişdir `{}` to `{}`:\n`{}`".format(
                        detection.lang, source_lang, tekstr.text),
                    parse_mode=ParseMode.MARKDOWN)
            else:
                tekstr = trl.translate(text, dest=dest_lang, src=source_lang)
                message.reply_text(
                    "Tərcümə edilmişdir `{}` to `{}`:\n`{}`".format(
                        source_lang, dest_lang, tekstr.text),
                    parse_mode=ParseMode.MARKDOWN)

    except IndexError:
        update.effective_message.reply_text(
            "İstədiyiniz dilə tərcümə etmək üçün mesajlara cavab verin və ya başqa dillərdən mesaj yazın\n\n"
            "Misal: `/tr en-ml` İngilis dilindən Malayalam dilinə tərcümə etmək\n"
            "İstifadə: `/tr en` avtomatik aşkarlama və İnglis dilinə tərcümə etmək üçün\n"
            "Bax [Dil Kodlarının Siyahısı](https://t.me/AzRobotGroup/502) dil kodlarının siyahısı üçün.",
            parse_mode="markdown",
            disable_web_page_preview=True)
    except ValueError:
        update.effective_message.reply_text(
            "İstədiyiniz dil tapılmadı!")
    else:
        return


__help__ = """
*Mövcud əmrlər:*
*Doğruluq və cəsarət:*
 ➩ /dogruluq : təsadüfi doğruluq sualı verər.
 ➩ /cesaret : təsadüfi cəsarət üçün söz atar.
*Divar kağızı*
 ➩ /wall <axtardığın>: Təsadüfi divar kağızlarını birbaşa botdan əldə edin!
*Şəkil axtarışları*
 ➩ /reverse <link>: Google-da axtarış şəklini və ya stikerləri tərsinə çevirin.
*Yazını səsli formata çevirib göndərir:*
 ➩ /tts <yazı>:  mətndən səs(mp3).
*Markdown:*
 ➩ /markdownhelp : yalnız xüsusi söhbətlərdə
*Paste:*
 ➩ /paste : Cavablandırılmış mətn `nekobin.com`a yazır və url ilə cavab verir
*Reaksiya:*
 ➩ /react : Təsadüfi reaksiya ilə reaksiya verir
*Axtarma lüğəti:*
 ➩ /ud <söz>: Axtarışda istifadə etmək istədiyiniz sözü və ya ifadəni yazın
*Wikipedia:*
 ➩ /wiki <sorğu>: wikipedia sorğunuzu göstərər
*SürətTest:*
 ➩ /SpeedTest : İnternet sürətini yoxlayın
*Kino Qiymətləndirmələri:*
 ➩ /imdb <kino adı>: İmdb nəticəsini imbd.com saytından əldə edinm
*Tətbiq haqqında məlumat:*
 ➩ /app <Proqram adı>: Tətbiq haqqında məlumat alın
*Nömrə məlumat:*
 ➩ /nomre <tam nömrə>: Detalları yoxlayır
"""

ECHO_HANDLER = DisableAbleCommandHandler("echo", echo, filters=Filters.group)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
UD_HANDLER = DisableAbleCommandHandler(["ud"], ud)
TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], totranslate)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(TRANSLATE_HANDLER)

__mod_name__ = "🤖Əlavələr"
__command_list__ = ["id", "echo", "ud", "tr", "tl"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    UD_HANDLER,
    TRANSLATE_HANDLER,
]
