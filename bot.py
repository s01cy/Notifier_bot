from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging 
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import random
import os
PORT = int(os.environ.get('PORT', 5000))
TOKEN = '' #Place your bot token here
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

""" Send notification message """
def start_notifying(update, context, notification_text):
    context.bot.send_message(chat_id = update.effective_chat.id, text=notification_text)

""" /start command """
def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="I'm a bot that will keep notifying you!!! DO YOUR JOB!!!")
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Type /help for more")

def echo(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="I don't understand you! Type /help")

""" Create a notification using scheduler """

def create_notification(update, context):
    #Get a text after /notify NOTIFY_TEXT#TIME
    entered_text = " ".join(context.args)
    #Check if the input is empty
    if not entered_text:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Seems like you entered nothing. Type /help")
    else:
        notification_args = entered_text.split("#")
        notification_text = notification_args[0]
        #Check if the time input is correct
        if notification_args[1].isdigit():
            time_interval = int(notification_args[1])
            if time_interval == 0:
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="A zero? Generating random time amount...")
                time_interval = random.randint(1, 60)
            #chat_id is used as a key because it is unique for each user and allows us to restrict user from creating more than 1 notification
            key = update.effective_message.chat_id
            #store key in a user_data
            context.user_data[key] = key
            try:  
                #Add a job with and id of a key
                scheduler.add_job(lambda : start_notifying(update, context, notification_text), 'interval', minutes=time_interval, id=str(key))  
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="Here you go. I will notify you every " + str(time_interval) + " minutes.")
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="If you want me to stop, type /stop :)")
            #Check if the scheduler is already running for this user
            except apscheduler.jobstores.base.ConflictingIdError:
                context.bot.sendMessage(chat_id=update.effective_chat.id, text="You already have a running notification. Stop it using /stop command.")

        else:
            context.bot.sendMessage(chat_id=update.effective_chat.id, text="Seems like you entered empty or incorrect time value. Type /help")

def stop_notification(update, context):
    try:
        #If user_data is empty, notify user that he has nothing to disable
        job_id = str(context.user_data.popitem()[0])
        scheduler.remove_job(job_id)
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="Notification disabled succesfully. I hope you did that job.")
    except KeyError:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text = "Nothing to disable!")

def help(update,context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="To start receiving notifications, type /notify TEXT#TIME(minutes), ex. /notify Make your room clean!#15")
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="If you enter 0 as a time value, bot will generate it (1-59 minutes)")
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="To stop receiving notifications, type /stop")
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="You can use only one notification process now. To make a new notification, stop existing and make a new one.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def unknown(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Unknown command.")

def main():
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    dispatcher.add_handler(CommandHandler("notify", create_notification))

    dispatcher.add_handler(CommandHandler("stop", stop_notification))

    dispatcher.add_handler(CommandHandler("help", help))

    dispatcher.add_error_handler(error)

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    #Input your heroku URL in ''
    updater.bot.setWebhook('' + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()