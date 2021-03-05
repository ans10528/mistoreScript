from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

import cv2

import numpy as np
import time
import array
import math
import random
import sys

gameUri_ = "http://pc-play.games.dmm.co.jp/play/MistTrainGirlsX/"
userAccount_ = ''
userPassword_ = ''

debuggerAddress_ = ''
driver_ = 0
canvas_ = 0

#Canvas Crop (board4,scroll86)
canvasX_ = 2
canvasY_ = 6
canvasWidth_ = 1136
canvasHeight_ = 640

frame_ = 0

def chromeConfig():
    global driver_
    global debuggerAddress_

    # use current browser
    if debuggerAddress_ != "":
        if len(sys.argv) > 1 and (sys.argv[1] == '127.0.0.1:9223' or 
                                 sys.argv[1] == '127.0.0.1:9224') :
            debuggerAddress_ = sys.argv[1]
            print(f'debuggerAddress_ = {debuggerAddress_} : sys.argv[1]')
        originChrome = webdriver.ChromeOptions()
        originChrome.debugger_address=debuggerAddress_
        driver_ = webdriver.Chrome(options=originChrome)
    else:
        driver_ = webdriver.Chrome()

def isGameSite():
    return driver_.current_url == gameUri_

def gameLogin():
    '''Login DMM service'''
    global driver_
    if not isGameSite():
        driver_.get(gameUri_)
        time.sleep(1)

    #login
    global userAccount_
    global userPassword_

    if not isGameSite():
        time.sleep(3)
        accountTextbox = driver_.find_element_by_id("login_id")
        passwordTextbox = driver_.find_element_by_id("password")
        accountTextbox.clear()
        accountTextbox.send_keys(userAccount_)
        passwordTextbox.clear()
        passwordTextbox.send_keys(userPassword_)
        passwordTextbox.send_keys(Keys.RETURN)
        time.sleep(4) #waiting for login

def windowConfig():
    '''resize window and locate gameCanvas'''
    #1156,648 +17,87
    driver_.set_window_size(1173, 735)
    js="var aaa = document.documentElement.scrollTop=70"  
    driver_.execute_script(js)  
    #time.sleep(1) #waiting for resize window
    # locate: iframe game_frame frm1
    driver_.switch_to.frame("game_frame")
    driver_.switch_to.frame("frm1")
    global canvas_
    canvas_ = driver_.find_element_by_id("GameCanvas")
    # TODO: if canvas not found
    global canvasWidth_
    global canvasHeight_
    canvasWidth_ = math.ceil(canvas_.size["width"])
    canvasHeight_ = math.ceil(canvas_.size["height"])

# vision ----------------------------------------------------

def updateFrame():
    global driver_
    global frame_
    global canvasX_,canvasY_,canvasWidth_,canvasHeight_
    scr_png = driver_.get_screenshot_as_png()
    # cv method
    nparr = np.frombuffer(scr_png, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    # canvas crop
    img = img[canvasY_:canvasY_+canvasHeight_,
                canvasX_:canvasX_+canvasWidth_]
    frame_ = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    return img #return color img

# action ----------------------------------------------------

def tap(x ,y):
    global driver_
    global canvas_
    webdriver.ActionChains(driver_).move_to_element_with_offset(canvas_, x , y).click().perform()
    # check lib/selenium/webdriver/common/interactions/pointer_actions  
    # default_move_duration = 34
    time.sleep(0.15 * random.random())

def scroll(x ,y,offsetX,offsetY):
    global driver_
    global canvas_
    webdriver.ActionChains(driver_).move_to_element_with_offset(canvas_, x , y).click_and_hold().pause(0.1).move_to_element_with_offset(canvas_,x+offsetX,y+offsetY).release().perform()
    # check lib/selenium/webdriver/common/interactions/pointer_actions  
    # default_move_duration = 34
    time.sleep(0.15 * random.random())

def tapIfFind(templateName):
    global template_
    template = findTemplate(templateName)
    res = cv2.matchTemplate(frame_,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x,y = max_loc

    threshold = 0.9
    # print(f"{templateName}:{round(res[y,x],2)}")
    if max_val > threshold:
        print(f'tap {templateName} : {x},{y} ({max_val})')
        tap(x,y)

def TryFind(templateName):
    global template_
    template = findTemplate(templateName)
    res = cv2.matchTemplate(frame_,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x,y = max_loc

    threshold = 0.9
    # print(f"{templateName}:{round(res[y,x],2)}")
    if max_val > threshold:
        print(f'find {templateName} : {x},{y} ({max_val})')
        return True

# script ----------------------------------------------------
template_ = {}
def loadTemplate(templateName):
    template_.setdefault(templateName,cv2.imread(rf".\image\{templateName}.png",0))

def findTemplate(templateName):
    if templateName in template_:
        return template_[templateName]
    else:
        loadTemplate(templateName)
        return template_[templateName]

def templateInit():None
    # # login
    # loadTemplate('loginGear')
    # loadTemplate('InfoPageCantClose')

def main():
    global driver_,frame_
    # connect browser (init)
    chromeConfig()
    gameLogin()
    windowConfig()
    templateInit()

    # main script

debuggerAddress_ = '127.0.0.1:9223' #yuk
# debuggerAddress_ = '127.0.0.1:9224' #hat
main()
#---------------------------------------------------------------

def eventGacha():
    if 0:None
    elif tapIfFind('eventGacha'):None
    elif TryFind('eventGachaConfirm'):
        tap(651,487)
        time.sleep(5)
        tap(565,598)
        time.sleep(1)
        tap(565,486)

# test scrip
while 1:
    frame = updateFrame()
    if 0:None

    # change day windows
    elif TryFind('changeDay') or TryFind('errorRestart'):
        chromeConfig()
        windowConfig()

    # mainQuest2-5
    elif tapIfFind('questNormalUnselect'):None
    elif tapIfFind('autorunConfirm'):None
    elif tapIfFind('autorun'):None
    elif TryFind('mainQuest2-5N'):
        tap(1000,532)
    elif tapIfFind('mainQuestStage2'):None
    elif TryFind('mainQuestStage'):
        tap(253,515)
    elif tapIfFind('mainquest'):None
    elif tapIfFind('quest'):None

    # recover stamina
    elif TryFind('recoverStaminaMenu'):
        print('chain tap start: recoverStamina')
        time.sleep(0.5)
        scroll(1021,455,0,-300)
        time.sleep(2)
        tap(279,448)
        time.sleep(2)
        tap(698,367)
        time.sleep(2)
        tap(650,525)
        time.sleep(2)
        tap(567,477)
        time.sleep(2)
        tap(566,538)
        time.sleep(2)
        tap(903,602)
        time.sleep(2)
        tap(656,484)
        print('chain tap end : recoverStamina')
    elif TryFind('battleOutofStamina2'):
        tap(647,482)
    # battle
    elif tapIfFind('battleContinue'):None
    elif tapIfFind('battleLoseAndContinue'):None

    
    # login
    elif TryFind('loginGear'):
        tap(533,540)
    elif tapIfFind('InfoPageCanClose'):None
    elif tapIfFind('InfoPageSkip'):None
    elif TryFind('InfoPageCantClose'):  #高誤判
        tap(701,594)

    # other
    # elif tapIfFind('StorySkipConfirm'):None

    # eventGacha()


    time.sleep(0.5)


