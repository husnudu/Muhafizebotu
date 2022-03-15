import html
import random
import LaylaRobot.modules.truth_and_dare_string as truth_and_dare_string
from LaylaRobot import dispatcher
from telegram import ParseMode, Update, Bot
from LaylaRobot.modules.disable import DisableAbleCommandHandler
from telegram.ext import CallbackContext, run_async

@run_async
def dogruluq(update: Update, context: CallbackContext):
    args = context.args
    update.effective_message.reply_text(random.choice(truth_and_dare_string.TRUTH))

@run_async
def cesaret(update: Update, context: CallbackContext):
    args = context.args
    update.effective_message.reply_text(random.choice(truth_and_dare_string.DARE))

    
TRUTH_HANDLER = DisableAbleCommandHandler("dogruluq", dogruluq)
DARE_HANDLER = DisableAbleCommandHandler("cesaret", cesaret)


dispatcher.add_handler(TRUTH_HANDLER)
dispatcher.add_handler(DARE_HANDLER)

