import random

from LaylaRobot import dispatcher
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.ext import CallbackContext, run_async

reactions = [
    "Şəhid Adları Modulu Aktif Deyildir😊\nYaxın Zamanda Aktif Olacaqdır🌹\n@AzRobotlar Kanala Qatılıb Botlarla Bağlı🤖\nYeni Xəbərləri Qaçırmayın✅",
    
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
    
