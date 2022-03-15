import random
import threading
from typing import Union

from LaylaRobot.modules.helper_funcs.msg_types import Types
from LaylaRobot.modules.sql import BASE, SESSION
from sqlalchemy import (BigInteger, Boolean, Column, Integer, String,
                        UnicodeText)

DEFAULT_WELCOME = 'Salam {first}, necəsən?'
DEFAULT_GOODBYE = 'Ok! Get burdan'

DEFAULT_WELCOME_MESSAGES = [
    "{first} burada!",  #Discord welcome messages copied
    "Gözəl, {first} burada.",
    "{first} Aslan kimi içəri girdi!",
    "{first} Qrupunda görməyimizə çox şadıq.Xoş gəldiniz 🥰",
    "Xoş gəlmisiniz, {first}. Sizi gözləyirdik",
    "Xoş gəlmisiniz,{first}. Ümid edirik pizza gətirdiniz.",
    "Xoş Gəldin, {first}. Silahlarını qapının yanında qoy.",
    "Vicuuuu. {first} indicə göydən endi.",
    "Möhkəm dayanın. {first} söhbətə qatıldı.",
    "{first} yeni qatıldı. Yeməklərinizi gizlədin.",
    "{first} qrupumuza gəlişinlə bizim üçün bir fərqlilik gətirəcəyivə inanırıq 🥰 ",
    "{first} qrupumuza xoş gəldiz. İnanırıq ki, burda keçirəcəyiniz dəqiqlər sizin üçün xoş və mənalı dəqiqələr olacaq🤗.",
    "{first} Dostluğun, hörmətin və sayqının kəsişdiyi qrupumuzda sizi görmək bizim üçün çox xoş oldu😍",
    "Sizi gözləyirdik😄✨ {first}",
    "Heyy {first} qrupuna xoş gəldin🤗 Qrupumuzda qalıb bizlərə qoşularaq gününüzü xoş və əyləncəli keçirə bilərsiz🥳 Xoş əyləncələr✨💫",
    "{first}, Mark Zuckerberg, CIA və digər 35 nəfər tərəfindən oxunan qrupa qatıldı."
    "Salam {first}, düşən meymunlara diqqət yetirin.",
    "Hər kəs etdiyiniz işi dayandırır. Biz indi {first}."
    "Hey {first}, bu izləri necə aldığımı bilmək istəyirsən?",
    "Salam {first}, silahlarınızı atın və casus skanerinə keçin.",
    "Təhlükəsiz qalın {first}, mesajlarınız arasında 3 metr sosial məsafə saxlayın.", #Corona memes lmao
    "Hey {first}, bir dəfə meteoritlə bir yumruq vurduğumu bilirsinizmi?",
    "İndi buradasınız {first}, müqavimət əbəsdir",
    "{first} yeni gəldi, qüvvə bu ilə güclüdür.",
    "{first} yeni prezidentin əmrləri ilə qatıldı.",
    "Salam {first}, stəkanın yarısı doludur, yoxsa yarısı boş?",
    "Yipee Kayaye {first} gəldi.",
    "Xoş gəldiniz {first}, əgər gizli agentsinizsə 1-ə basın, əks halda söhbətə başlayın",
    "{first}, artıq Kanzasda olmadığımızı hiss edirəm.",
    "Onlar canımızı ala bilərlər, amma heç vaxt {first} almayacaqlar.",
    "Sahil aydındır! Çıxa bilərsiniz uşaqlar, sadəcə {first}.",
    "Xoş gəldiniz {first}, gizlənən oğlana əhəmiyyət verməyin.",
    "Xoş gəlmisiniz {əvvəlcə}, güc sizinlə ola bilər.",
    "{first} sizinlə olsun.",
    "{first} yenicə qatıldı. Hey, Perry haradadır?",
    "{first} yenicə qatıldı. Oh, buradasan, Perry.",
    "Xanımlar və cənablar, sizə verirəm ... {first}.",
    "barmaqlarını çırpır və teleportları {first} burada",
    "{first}! Balıq və dovşan nədir?", #Lifereload - kaizoku üzvü
    "Salam {first}, 1000-7 nədir?", # Tokyo ghoul
    "Gəl. Buranı dağıtmaq istəmirəm", #hunter x hunter
    "Hey {first} ... bu sözləri heç eşitmisən?", #BNHA
    "Bir adam burada biraz yata bilmirmi?", # Kamina Falls - Gurren Lagann
    "Birinin səni yerinə qoyma vaxtı gəldi, ilk növbədə.", #Hellsing
    "Unit-01 yenidən aktivləşdi ..", # Neon Genesis: Evangelion
    "Çətinliyə hazırlaşın ... Və ikiqat edin", # Pokemon
    "Hey {first}, məni çağırırsan?", # Shaggy
    "Oh? Mənə yaxınlaşırsan?", #Jojo
    "{first} yalnız qrupa düşdü!",
    "Mən..bu ... sadəcə {first}.",
    "Sugoi, Dekai. {first} Qoşuldu!",
    "{first}, ölüm tanrılarını bilirsinizmi almaları sevirsiniz?", # Ölüm Qeydləri var
    "Mən bir kartof çipi götürəcəm .... yeyəcəyəm", # Ölüm Qeydləri var
    "{first} qoşuldu !, Açılış Qapısı ... açıq!",
    "{first} qoşuldu !, Şəfa Qapısı ... açıq!",
    "{first} qoşuldu !, Həyat Qapısı ... açıq!",
    "{first} qoşuldu !, Ölüm Qapısı ... açıq!",
    "{first}! Mən, Botam! səni ən güclü elan edirəm",
    "{first}, bu dəfə sənə gücümü verəcəyəm.", #Kyuubi naruto-ya
    "{first}, gizli yarpaq kəndinə xoş gəlmisiniz!", # Naruto şeyləri burada bitir
    "Ormanda gözləmək lazımdır ... zar beş-səkkiz oxunana qədər.", #Jumanji məhsulları
    "Dr. {first} Məşhur arxeoloq və beynəlxalq kəşfiyyatçı, \ nJumanjiyə xoş gəldiniz! \ NJumanjinin taleyi sizin ixtiyarınızdadır.",
    "{first}, bu asan bir missiya olmayacaq - meymunlar ekspedisiyanı yavaşlatır.", # Jumanji məhsullarının sonu  
  


    
]
DEFAULT_GOODBYE_MESSAGES = [
     "{first} qaçırılacaq.",
     "{username} Gorbagor oldu.",
    "{first} yeni oflayn oldu.",
    "{first} lobbidən ayrıldı.",
    "{first} klandan ayrıldı.",
    "{first} oyunu tərk etdi.",
    "{first} ərazidən qaçdı.",
    "{first} işləmir.",
    "Nə yaxşı bilirsən, {first}!",
    "Əyləncəli bir vaxt idi {first}.",
    "Ümid edirik ki, tezliklə yenidən görüşəcəyik, {first}.",
    "Mən vida etmək istəyirəm, ilk növbədə..",
    "Əlvida {first}! Kim olduğunu darıxacaq: ')",
    "Əlvida {first}! Sənsiz tənha olacaq.",
    "Xahiş edirəm məni bu yerdə tək qoymayın, {first}!",
    "Bizdən daha yaxşı bok afişalar tapmaqda uğurlar, {first}!",
    "Bilirsən, sənin üçün darıxacağıq {first}. Doğrudanmı? Təbiki yox 😂",
    "Təbrik edirik, {first}! Rəsmi olaraq bu qarışıqlıqdan azadsınız.",
    "{first}. Döyüşməyə dəyər bir rəqib idiniz.",
    "Gedirsən, {first}? ",
    "Fotonu ona gətir",
    "Çölə çıxın!",
    "Sonra yenidən soruşun",
    "Özün haqqında düşün",
    "Sual səlahiyyətləri",
    "Günəş tanrısına ibadət edirsən",
    "Bu gün evdən çıxma",
    "İmtina etmək!",
    "Evlənin və çoxalın",
    "Yuxuda qal",
    "Oyan Get",
    "La luna bax",
    "Steven yaşayır bilirdin?",
    "Yabancılarla qərəzsiz görüşün",
    "Asılan adam bu gün sizə bəxt gətirməyəcək",
    "Bu gün nə etmək istəyirsən?",
    "İçiniz qaranlıqdır",
    "Çıxışını gördünmü?",
    "Bir körpə ev heyvanı alın, bu sizi sevindirəcək.",
    "Şahzadəniz başqa bir qaladadır.",
    "Yanlış oynayırsan mənə nəzarətçi ver",
    "Yaxşı insanlara etibar edin",
    "Ölmək üçün yaşa.",
    "Həyat sənə limon təkrarladıqda!",
    "Yaxşı, bu dəyərsiz idi",
    "Mən yuxuya getdim!",
    "Dərdləriniz çox olsun",
    "Köhnə həyatınız xarabadır",
    "Həmişə parlaq tərəfə baxın",
    "Tək getmək təhlükəlidir",
    "Sən heç vaxt bağışlanmayacaqsan",
    "Özünüzdən başqa günahlandıracaq heç kiminiz yoxdur",
    "Yalnız günahkar",
    "Bomba ağıllı istifadə edin",
    "Gördüyünüz bəlaları heç kim bilmir",
    "Şişman görünürsən, daha çox idman etməlisən",
    "Zebranı izləyin",
    "Niyə bu qədər mavisən?",
    "Maskalanmış şeytan",
    "Çölə çıx",
    "Hər zaman başınız bulud içindədir",
]
# Line 111 to 152 are references from https://bindingofisaac.fandom.com/wiki/Fortune_Telling_Machine


class Welcome(BASE):
    __tablename__ = "welcome_pref"
    chat_id = Column(String(14), primary_key=True)
    should_welcome = Column(Boolean, default=True)
    should_goodbye = Column(Boolean, default=True)
    custom_content = Column(UnicodeText, default=None)

    custom_welcome = Column(
        UnicodeText, default=random.choice(DEFAULT_WELCOME_MESSAGES))
    welcome_type = Column(Integer, default=Types.TEXT.value)

    custom_leave = Column(
        UnicodeText, default=random.choice(DEFAULT_GOODBYE_MESSAGES))
    leave_type = Column(Integer, default=Types.TEXT.value)

    clean_welcome = Column(BigInteger)

    def __init__(self, chat_id, should_welcome=True, should_goodbye=True):
        self.chat_id = chat_id
        self.should_welcome = should_welcome
        self.should_goodbye = should_goodbye

    def __repr__(self):
        return "<Qrup Əhli {} yeni istifadəçiləri salamlamalıyıq: {}>".format(
            self.chat_id, self.should_welcome)


class WelcomeButtons(BASE):
    __tablename__ = "welcome_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class GoodbyeButtons(BASE):
    __tablename__ = "leave_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class WelcomeMute(BASE):
    __tablename__ = "welcome_mutes"
    chat_id = Column(String(14), primary_key=True)
    welcomemutes = Column(UnicodeText, default=False)

    def __init__(self, chat_id, welcomemutes):
        self.chat_id = str(chat_id)  # ensure string
        self.welcomemutes = welcomemutes


class WelcomeMuteUsers(BASE):
    __tablename__ = "human_checks"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(String(14), primary_key=True)
    human_check = Column(Boolean)

    def __init__(self, user_id, chat_id, human_check):
        self.user_id = (user_id)  # ensure string
        self.chat_id = str(chat_id)
        self.human_check = human_check


class CleanServiceSetting(BASE):
    __tablename__ = "clean_service"
    chat_id = Column(String(14), primary_key=True)
    clean_service = Column(Boolean, default=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)

    def __repr__(self):
        return "<Çat təmiz xidmətdən istifadə etdi ({})>".format(self.chat_id)


Welcome.__table__.create(checkfirst=True)
WelcomeButtons.__table__.create(checkfirst=True)
GoodbyeButtons.__table__.create(checkfirst=True)
WelcomeMute.__table__.create(checkfirst=True)
WelcomeMuteUsers.__table__.create(checkfirst=True)
CleanServiceSetting.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
WELC_BTN_LOCK = threading.RLock()
LEAVE_BTN_LOCK = threading.RLock()
WM_LOCK = threading.RLock()
CS_LOCK = threading.RLock()


def welcome_mutes(chat_id):
    try:
        welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
        if welcomemutes:
            return welcomemutes.welcomemutes
        return False
    finally:
        SESSION.close()


def set_welcome_mutes(chat_id, welcomemutes):
    with WM_LOCK:
        prev = SESSION.query(WelcomeMute).get((str(chat_id)))
        if prev:
            SESSION.delete(prev)
        welcome_m = WelcomeMute(str(chat_id), welcomemutes)
        SESSION.add(welcome_m)
        SESSION.commit()


def set_human_checks(user_id, chat_id):
    with INSERTION_LOCK:
        human_check = SESSION.query(WelcomeMuteUsers).get(
            (user_id, str(chat_id)))
        if not human_check:
            human_check = WelcomeMuteUsers(user_id, str(chat_id), True)

        else:
            human_check.human_check = True

        SESSION.add(human_check)
        SESSION.commit()

        return human_check


def get_human_checks(user_id, chat_id):
    try:
        human_check = SESSION.query(WelcomeMuteUsers).get(
            (user_id, str(chat_id)))
        if not human_check:
            return None
        human_check = human_check.human_check
        return human_check
    finally:
        SESSION.close()


def get_welc_mutes_pref(chat_id):
    welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
    SESSION.close()

    if welcomemutes:
        return welcomemutes.welcomemutes

    return False


def get_welc_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_welcome, welc.custom_welcome, welc.custom_content, welc.welcome_type

    else:
        # Welcome by default.
        return True, DEFAULT_WELCOME, None, Types.TEXT


def get_gdbye_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_goodbye, welc.custom_leave, welc.leave_type
    else:
        # Welcome by default.
        return True, DEFAULT_GOODBYE, Types.TEXT


def set_clean_welcome(chat_id, clean_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id))

        curr.clean_welcome = int(clean_welcome)

        SESSION.add(curr)
        SESSION.commit()


def get_clean_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()

    if welc:
        return welc.clean_welcome

    return False


def set_welc_preference(chat_id, should_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_welcome=should_welcome)
        else:
            curr.should_welcome = should_welcome

        SESSION.add(curr)
        SESSION.commit()


def set_gdbye_preference(chat_id, should_goodbye):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_goodbye=should_goodbye)
        else:
            curr.should_goodbye = should_goodbye

        SESSION.add(curr)
        SESSION.commit()


def set_custom_welcome(chat_id,
                       custom_content,
                       custom_welcome,
                       welcome_type,
                       buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_welcome or custom_content:
            welcome_settings.custom_content = custom_content
            welcome_settings.custom_welcome = custom_welcome
            welcome_settings.welcome_type = welcome_type.value

        else:
            welcome_settings.custom_welcome = DEFAULT_WELCOME
            welcome_settings.welcome_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with WELC_BTN_LOCK:
            prev_buttons = SESSION.query(WelcomeButtons).filter(
                WelcomeButtons.chat_id == str(chat_id)).all()
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = WelcomeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_welcome(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_WELCOME
    if welcome_settings and welcome_settings.custom_welcome:
        ret = welcome_settings.custom_welcome

    SESSION.close()
    return ret


def set_custom_gdbye(chat_id, custom_goodbye, goodbye_type, buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_goodbye:
            welcome_settings.custom_leave = custom_goodbye
            welcome_settings.leave_type = goodbye_type.value

        else:
            welcome_settings.custom_leave = DEFAULT_GOODBYE
            welcome_settings.leave_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with LEAVE_BTN_LOCK:
            prev_buttons = SESSION.query(GoodbyeButtons).filter(
                GoodbyeButtons.chat_id == str(chat_id)).all()
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = GoodbyeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_gdbye(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_GOODBYE
    if welcome_settings and welcome_settings.custom_leave:
        ret = welcome_settings.custom_leave

    SESSION.close()
    return ret


def get_welc_buttons(chat_id):
    try:
        return SESSION.query(WelcomeButtons).filter(
            WelcomeButtons.chat_id == str(chat_id)).order_by(
                WelcomeButtons.id).all()
    finally:
        SESSION.close()


def get_gdbye_buttons(chat_id):
    try:
        return SESSION.query(GoodbyeButtons).filter(
            GoodbyeButtons.chat_id == str(chat_id)).order_by(
                GoodbyeButtons.id).all()
    finally:
        SESSION.close()


def clean_service(chat_id: Union[str, int]) -> bool:
    try:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if chat_setting:
            return chat_setting.clean_service
        return False
    finally:
        SESSION.close()


def set_clean_service(chat_id: Union[int, str], setting: bool):
    with CS_LOCK:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if not chat_setting:
            chat_setting = CleanServiceSetting(chat_id)

        chat_setting.clean_service = setting
        SESSION.add(chat_setting)
        SESSION.commit()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Welcome).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)

        with WELC_BTN_LOCK:
            chat_buttons = SESSION.query(WelcomeButtons).filter(
                WelcomeButtons.chat_id == str(old_chat_id)).all()
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        with LEAVE_BTN_LOCK:
            chat_buttons = SESSION.query(GoodbyeButtons).filter(
                GoodbyeButtons.chat_id == str(old_chat_id)).all()
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        SESSION.commit()
