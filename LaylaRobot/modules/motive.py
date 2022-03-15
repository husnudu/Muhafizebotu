import random

from LaylaRobot import dispatcher
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.ext import CallbackContext, run_async

reactions = [
    "Başqasının uğuruna sevinə bilmeyen uğur qazana bilməz🪔", "Məqsədlərin üçün vuruş.🪐", "Xəyalların səni qorxutmursa demək ki yetərincə böyük deyil🔗", "Bir gün hədəfimizə çatmaq ümidiylə🗣", "Gəmilər ətrafında su olduğuna görə yox, içlərində su olduğuna görə batır. Ətrafında baş verənlərin içinə daxil olub səni aşağı çəkməsinə imkan vermə🌊", "İmkansız deyə bir şey yoxdur.Yeri gəlsə imkansız olanı bacararsan,təki inanmağdan əl çəkmə🗝",
    "Bir kitabda oxumuşdum ki, Dünya cəsarətli axmaqları sevir💥", "Böyük xəyalların böyük mübarizələri vardır💫", "Öz işığına görə yaşa.Daxilində öz işığını tap və heç bir qorxu olmadan onu yaşat\n©Osho", "Zamanı, Sevgini və Dəyəri olan layiq olanlara verin➰",
    "Sən səhv edə bilərsən, bu mümkündür və bağışlanandır. Bağışlanmayan səhvdən peşman olmamaq, onu düzəltməyə çalışmamaqdır əsl səhf✨", "The two most powerful warriors are patience and time.\nƏn güclü iki döyüşçü səbr və zamandır.♾🧠", "Bir gün bacardim deye çığlıqlar atacam👍🏻",
    "Hədəfi olmayan gəmiyə heç bir külək kömək edə bilməz🪁", "Risk almaqdan çəkinmə🧠", "Unutma ki, gülərkən itirdiklərini ağlamaqla geri qaytara bilməzsən💞", "-Marcel'dən ayrılacam.\n+Niyə?\n-Mənə ehtiyacı yoxdur. Tək sevdiyi kitablarıdı.\n\nKitablari sevin, qoruyun.Bezen kitab sene heyati anladar🤍",
    "İnsanlar son anlarını yaşayarkən əsl üzlərini göstərirlər.🔮", "Başqalarının sənin duyğuların, fikirlərin və hərəkətlərini kontrol etməsinə icazə vermə📒", "Yaşadıqca anlayırsan,zəif oldunsa əziləcəksən hər cəhətdən.Ruhən zəif olsan da qətiyyən biruzə vermək olmaz👁",
    "Allah qəlblərimizi paklaşdırsın, gözəlləşdirsin və qarşımıza qəlbi gözəl insanlar çıxartsın🙏🏼", "Yaxşılıq ticarət deyil\nAllah rızası üçün edilməli və unudulmalıdır🗣", "Özünüzlə qürur duyana qədər risk alın.✨", "Nə olursa olsun güclü qalmağı bacarın\nBu dünyada heçnə qalıcı deyil🥂",
    "Heç yorulmadan ,hədəfinizə doğru sevərək addımlayın.", "Məncə şanssiz insan deye bir şey yoxdu her bir insan öz şansini ozu yaradir.Yaradanlar şanslilar qrupuna.Yaratmayanlar ise Şanssizlar qrupuna aiddir🧩", "Bir çox məğlubiyyətlə qarşılaşa bilərik, ancaq məğlub olmamalıyıq.",
    "Hər qorxan qaçmaz,amma hər qaçan qorxaqdır.❕", "Bəzən bəzi şeylərin dəyərini itirdikdə anlayırıq.⛓", "Bir şeyi istəmirsinizsə xeyr deməyi bacarın🥰", "𝐙𝐚𝐦𝐚𝐧 𝐡ə𝐲𝐚𝐭𝐝ı𝐫, 𝐡ə𝐲𝐚𝐭 𝐢𝐬ə 𝐛𝐨𝐬̧𝐚 𝐜̧ı𝐱𝐦𝐚𝐲𝐚𝐧 𝐛𝐢𝐫 𝐝ə𝐲ə𝐫𝐝𝐢𝐫🤍", "Səni öldürməyən birşeyin səni qəribə göstərəcəyinə inanıram.🙏🏽",
    "3  addımla necə xoşbəxt ola bilərsən?🥢\n\n•Kofe'ni götür\n\n•Şokalad ilə kruassanını əlinə al\n\n•Ləzzətini çıxart☕️🥐", "Kiməsə nifrət etmək əvəzinə sadəcə işinə diqqət etdikdə qazanan sən olursan.\nBunu unutma❗️",
    "Risk et. Alınsa xoşbəxt, alınmasa təcrübəli olacaqsan.⚡️🍀", "Sən çox gözəlsən nə deyirlərsə desinler, Dinləmə onları💫", "Bəzən düzgün istiqamətdə atılmış ən kiçik addım həyatının ən böyük addımı ola bilər🌞💐", "Öz xəyallarından vazkeçmiş birinin sənin xəyallarına rəy bildirməsinə icazə vermə💫",
    "Bəzən daha yaxşı görmək üçün uzaqlaşmaq lazımdır.🤍", "Planların işləmirsə,planını dəyiş.Məqsədini yox🗞", "Böyük uğurlar kiçik cəhdlərdən başlar🦋.", "Kiməsə həddindən artıq güvənsən sonu iki cür ola bilər.Ya çox gözəl bir dost qazanarsan,ya da çox gözəl bir dərs👍🏽",
    "Bu günki tənbəlliklər sabahkı göz yaşlarına çevrilə bilər🎡", "Həyatın rəngləri sənin əlindədir.Müsbət tonları seç🐠", "Öncə edə bilmərsən deyərlər.Sonra necə etdiyini soruşarlar💫", "Pis keçən dünəni düşünərək,gözəl bir günü məhvetmə🤍", "Ağılın gücündən qüvvətli olan tək şey qəlbin cəsarətidir.🧡",
    "Bəhanə axtarma❕\n\nSəndə olmayan bir şeyi əldə etmək üçün heç vaxt etmədiyini etməlisən✅", "Məqsədimiz mümkünsüzü mümkün etmək, mümkünü asan etmək, asanı da zərif və zövqlü etmənin yollarını tapmaqdır.💭", "Həyatdakı hər dəqiqə hər şeyi dəyişdirmək üçün bir şansdır🔍",
    "Özüne inan və davam et💫", "İnsanlar ədalətsizliyi ancaq öz başlarına gələndə düşünürlər💫", "",
    
    
    
]


@run_async
def motivasiya(update: Update, context: CallbackContext):
    message = update.effective_message
    motivasiya = random.choice(reactions)
    if message.reply_to_message:
        message.reply_to_message.reply_text(motivasiya)
    else:
        message.reply_text(motivasiya)


REACT_HANDLER = DisableAbleCommandHandler("motivasiya", motivasiya)

dispatcher.add_handler(REACT_HANDLER)

__command_list__ = ["motivasiya"]
__handlers__ = [REACT_HANDLER]
