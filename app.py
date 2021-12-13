import telegram, itertools, datetime, threading, requests, io, time
from creds import bot_token, bot_user_name, URL, my_chat_id, user_email, user_password
import Eclass as c

from flask import Flask, request

global Editusr
Editusr = False
ListMsg = """INVALID LINK\n\nPlease provide valid google meet link or try other functions\n\n/restart\n/status\n/edituser """


def checker_thread():
    i = 0
    while True:
        if i % 240 == 0:  
            resuscitate = requests.get(URL) 
        time.sleep(5)  
global Upassword
global Umail
global bot
global TOKEN
global MY_CHAT_ID
MY_CHAT_ID = my_chat_id
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
Umail = user_email
Upassword = user_password

app = Flask(__name__)
with open(
        'threadstatus.txt') as f: data = f.read()  
if data != "thread started":
    with open('threadstatus.txt', "w") as f: f.write("thread started")
    x = threading.Thread(target=checker_thread)
    x.start()


def getCommandType(text):
    global Editusr, Umail
    text = text.strip()
    if text == "/start" or text == "/restart":
        with io.open('job.txt', "w", encoding="utf-8") as f:
            f.write("none")
        return """🙏🏽 Namaste, I am a BOT to attend your online class.\n\nJust give me class link and leave everything on me.\n\nYou can also use these functionality\n/restart\n/status\n/edituser\n"""
    elif text == "/status":
        with io.open('job.txt', encoding="utf-8") as f:
            data = f.read()
        if data == "none":
            return "Currently i am free, not attending any class"
        else:
            message = "Currently am attending a class at this link : " + data + "\n\n for user having email : " + Umail + "\n\n/cancel current class\n\n"
            return message
    elif text == "/edituser":
        message = """Please provide Email ID and Password to attend online class for new user in format \n[EMAIL:PASSWORD]\n\nOr\n\n/cancel editing user.  """
        return message

    elif "." in text:
        try:
            x = text.split("/")
            if x[2] == "meet.google.com":
                with io.open('job.txt', "w") as f:
                    f.write(text)
                return "link"
            else:
                return ListMsg
        except:
            return ListMsg
    else:
        return ListMsg


def checkFormat(text1):
    try:
        x = text1.split(":")
        if len(x) == 2:
            return True
        else:
            return False
    except:
        return False


def sendMsg(msg, msg_id):
    bot.sendMessage(chat_id=MY_CHAT_ID, text=msg, reply_to_message_id=msg_id)


def checkEditusr():
    x = Editusr
    print(Editusr)
    if x:
        return True
    else:
        return False


def checkStatus():
    with io.open('job.txt', encoding="utf-8") as f:
        data = f.read()
    if data != "none":
        return True
    else:
        return False


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global Editusr
    global Umail
    global Upassword
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    try:
        print("got text messageeeeee:", update.message.text)
    except Exception as e:
        print(
            f"got that WinError87 most porbably. This is errorrrrrrrrrrrr: {e}")  # get this error whien user sends multi line message. No idea how to fix it.
    if update.message.text != None:  
        text1 = update.message.text.encode('utf-8').decode()
    else:
        return 'ok'

    try:
        if int(chat_id) != int(MY_CHAT_ID):  
            bot.sendMessage(chat_id=MY_CHAT_ID,
                            text=f"Unauthorized usage detected!!1!\n\nSender Chat ID: {update.message.chat.id}\nUsername: {update.message.chat.username}\nFirst Name: {update.message.chat.first_name}\nMessage: {update.message.text}\n\n chat_id: {chat_id}\nGiven_id: {MY_CHAT_ID}")  # MODIFYYYYTHIS #SENSITIZE
            bot.sendMessage(chat_id=chat_id,
                            text="UNAUTHORIZED USER\n\nCarefull Love,This BOT is not your servant.\nEither take permission from @DR_AN0NYMOUS\nor\nF*ck Off!")
        # here we call our super AI
        else:
            if checkStatus():
                if text1 == "/cancel":
                    with io.open('job.txt', 'w') as f:
                        f.write("none")
                        sendMsg("Current Class Canceled Manually", msg_id)
                        c.setendCall()
                elif text1 == "/class_status":
                    c.setCheckstatus()
                else:
                    with io.open('job.txt', encoding="utf-8") as f:
                        data = f.read()
                        message = "Currently am attending a class at this link : " + data + "\n\n for user having email : " + Umail + "\n\n/cancel current class\n\nOR\n\nGet /class_status"
                        sendMsg(message, msg_id)

            elif checkEditusr():

                if checkFormat(text1):
                    x = text1.split(":")
                    Umail = x[0]
                    Upassword = x[1]
                    msg = "User Updated Successfully.\nFrom now on i am going to attend online class for {}".format(Umail)
                    sendMsg(msg, msg_id)
                    Editusr = False
                elif text1 == "/cancel":
                    msg = "Editing user canceled"
                    sendMsg(msg, msg_id)
                    Editusr = False
                else:
                    msg = """INVALID FORMAT.\n\nPlease provide Email ID and Password in format [EMAIL:PASSWORD]\n\nOr\n\n/cancel editing user. """
                    sendMsg(msg, msg_id)
                    Editusr = True
            else:
                msg = getCommandType(text1)
                if msg != "link":
                    response = msg
                    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
                else:
                    response = "Bot waking up to attend your online class"
                    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
                    try:
                        c.startclass(text1)
                    except Exception as e:
                        sendMsg(msg="ERROR in starting class : {}".format(e), msg_id=msg_id)
                    return 'ok'
    except Exception as e:
        sendMsg(msg="ERROR : {} \nPlease try again".format(e), msg_id=msg_id)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return 'This is the Telegram bot.'


if __name__ == '__main__':  
    app.run(threaded=True, debug=True)
