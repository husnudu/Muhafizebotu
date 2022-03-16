import random

from LaylaRobot import dispatcher
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.ext import CallbackContext, run_async

reactions = [
    "əsgər Abakarov Nail Müzəffər 24.07.2001",
    "əsgər Abasov Ağababa Səfər 14.03.2002",
    "MAHHXHQ əsgər Abasov Ayaz Nizami 20.12.1998"
    "kiçik gizir Abasov Davud Yalçın 19.11.1999"
    "əsgər Abasov Elvin Səxavət 17.06.1993"
    "əsgər Abasov Ruslan Hikmət 24.05.2000"
    "əsgər Abasov Samir Adəm 24.08.2001"
    "kiçik çavuş Abasov Seymur Adil 10.08.1999"
    
]


@run_async
def sehid(update: Update, context: CallbackContext):
    message = update.effective_message
    sehid = random.choice(reactions)
    if message.reply_to_message:
        message.reply_to_message.reply_text(sehid)
    else:
        message.reply_text(sehid)


REACT_HANDLER = DisableAbleCommandHandler("sehid", sehid)

dispatcher.add_handler(REACT_HANDLER)

__command_list__ = ["sehid"]
__handlers__ = [REACT_HANDLER]
    
