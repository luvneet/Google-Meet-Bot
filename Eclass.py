import sys
import io
import schedule
from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException
from creds import bot_token, bot_user_name, URL, my_chat_id
import telegram

# firefox_profile = webdriver.FirefoxProfile()
# firefox_profile.set_preference("browser.privatebrowsing.autostart", True)

global endCall
global checkStatus
checkStatus = False
endCall = False
global gdriver
global bot
global TOKEN
global MY_CHAT_ID
MY_CHAT_ID = my_chat_id
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

chrome_options = FirefoxOptions()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-sh-usage")
fp = webdriver.FirefoxProfile("firefox_profile")
fp.set_preference('media.navigator.permission.disabled', True)
fp.set_preference("permissions.default.microphone", 2)
fp.set_preference("permissions.default.camera", 2)
fp.set_preference("media.volume_scale", "0.0")
# chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--start-maximized")


# chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
# chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.media_stream_mic": 2,
# 1:allow, 2:block
#             "profile.default_content_setting_values.media_stream_camera": 2,
#           "profile.default_content_setting_values.notifications": 2
#        })


def startclass(link):
    global gdriver
    gdriver = webdriver.Firefox(executable_path="GECKO DRIVER PATH", firefox_profile=fp,
                                options=chrome_options)
    gdriver.get(
        "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow")
    time.sleep(2)

    # login_id
    log = gdriver.find_element_by_css_selector('[data-email="??"]')
    log.click()

    time.sleep(4)
    sendMsg("Google Log in Successful.")

    # new_link
    gdriver.get(link)
    time.sleep(1)
    link_check(gdriver, link)
    return


def check_exists_by_css(param, driver):
    try:
        driver.find_element_by_css_selector(param)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(param1, driver):
    try:
        driver.find_element_by_xpath(param1)
    except NoSuchElementException:
        return False
    return True


def checkmembers(driver):
    members = driver.find_elements_by_css_selector("[role='listitem']")
    return len(members)


def join_meet(driver):
    time.sleep(3)
    global endCall
    global checkStatus
    driver.find_element_by_css_selector('[aria-label="Turn off microphone (CTRL + D)"]').click()
    driver.find_element_by_css_selector('[aria-label="Turn off camera (CTRL + E)"]').click()
    if check_exists_by_xpath("//span[@class='NPEfkd RveJvd snByac' and contains(text(), 'Ask to join')]", driver):
        driver.find_element_by_xpath(
            "//span[@class='NPEfkd RveJvd snByac' and contains(text(), 'Ask to join')]").click()
    elif check_exists_by_xpath("//span[@class='NPEfkd RveJvd snByac' and contains(text(), 'Join now')]", driver):
        driver.find_element_by_xpath(
            "//span[@class='NPEfkd RveJvd snByac' and contains(text(), 'Join now')]").click()
    else:
        sendMsg("Error: No Button Found")
        return
    time.sleep(5)
    m = 0
    while m < 3:
        if check_exists_by_css("[aria-label='Show everyone']", driver):
            sendMsg("Class Joined Successfully")
            time.sleep(2)
            show_everyone = driver.find_element_by_css_selector("[aria-label='Show everyone']")
            show_everyone.click()
            getClassStatus(driver)
            time.sleep(5)
            for i in range(806):
                if endCall:
                    sendMsg("Class Terminated Successfully")
                    endCall = False
                    end_meet(driver)
                elif checkStatus:
                    checkStatus = False
                    getClassStatus(driver)
                elif checkmembers(driver) < 4:
                    if i > 52:
                        sendMsg("Class Ended Due To Less Students : " + str(checkmembers(driver)))
                        end_meet(driver)
                    else:
                        time.sleep(5)
                else:
                    time.sleep(5)
            sendMsg("Meeting Ended with Full Class Attended")
            end_meet(driver)
        else:
            time.sleep(5)
            sendMsg("Failed To Join \nRetrying...")
            m = m + 1
    sendMsg("Failed To Join Meeting ,\n(Request Timeout 30 sec")
    end_meet(driver)
    return


def end_meet(driver):
    global endCall
    global checkStatus
    try:
        driver.find_element_by_class_name("kx3Hed.VZhFab").click()
        end_button = driver.find_elements_by_css_selector("[aria-label='Leave call']")
        end_button.click()
    except:
        pass
    with io.open('job.txt', 'w') as f:
        f.write("none")
    endCall = False
    checkStatus = False
    driver.quit()
    return


def link_check(driver, x):
    src = driver.page_source
    if "Your meeting code has expired. Create a new meeting." in src:
        sendMsg(x + "\n\nMeeting Expired")
        end_meet(driver)
    else:
        join_meet(driver)
    return


def check_exists_by_link(linktext, driver):
    try:
        driver.find_element_by_partial_link_text(linktext)
    except NoSuchElementException:
        return False
    return True


def getClassStatus(driver):
    members = "No of students in class : " + str(checkmembers(driver)) + "\n\nStudent List Below\n\n"
    members_list = driver.find_elements_by_css_selector('[class="ZjFb7c"]')
    i = 1
    for member in members_list:
        members = members + str(i) + ") " + str(member.get_attribute("innerText")) + "\n"
        i = i + 1
    sendMsg(members)
    return


def sendMsg(msg):
    bot.sendMessage(chat_id=MY_CHAT_ID, text=msg)


def setendCall():
    global endCall
    endCall = True


def setCheckstatus():
    global checkStatus
    checkStatus = True


