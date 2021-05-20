from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

import cv2

import numpy as np
import time
import array
import math
import random
import sys

# base(driver) --------------------------------------------------

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
    global driver_
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

def gameRestart():
    global driver_
    driver_.refresh()
    time.sleep(5)
    chromeConfig()
    windowConfig()
    time.sleep(5)

def printWithTime(msg):
    curTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'{curTime}| {msg}')

# loop control -------------------------------------------------

frameDelayDefault_ = 1.0
frameDelayStep_ = 0.2
frameDelayLimit_ = 30.0
frameDelay_ = frameDelayDefault_

frameDelayHasBeenChanged_ = True

def setCurrnetFrameDelay(sec:float):
    global frameDelayHasBeenChanged_
    global frameDelay_
    frameDelay_ = sec
    frameDelayHasBeenChanged_ = True # do not reset frameDelay at this time

def frameEnd():
    global frameDelayHasBeenChanged_
    global frameDelay_,frameDelayStep_,frameDelayLimit_,frameDelayDefault_
    global hasAction_
    if not frameDelayHasBeenChanged_:
        if hasAction_: 
            setCurrnetFrameDelay(frameDelayDefault_)
        else:
            setCurrnetFrameDelay(min(frameDelay_ + frameDelayStep_ , frameDelayLimit_))

    if frameDelay_ > 0:
        time.sleep(frameDelay_)
        # print(f'{frameDelay_}')

# vision ----------------------------------------------------

def updateFrame():
    global driver_
    global frame_
    global canvasX_,canvasY_,canvasWidth_,canvasHeight_
    
    img = None
    try:
        scr_png = driver_.get_screenshot_as_png()
        # cv method
        nparr = np.frombuffer(scr_png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        # canvas crop
        img = img[canvasY_:canvasY_+canvasHeight_,
                    canvasX_:canvasX_+canvasWidth_]
        frame_ = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    except:
        print('webdriver error: updateFrame')
        main()
        pass

    return img #return color img

template_ = {}
def loadTemplate(templateName):
    template_.setdefault(templateName,cv2.imread(rf".\template\{templateName}.png",0))

def findTemplate(templateName):
    if templateName in template_:
        return template_[templateName]
    else:
        loadTemplate(templateName)
        return template_[templateName]

def templateInit():None  # auto load when call findTemplate()
    # # login
    # loadTemplate('loginGear')
    # loadTemplate('InfoPageCantClose')

# TODO vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
templateDisableTimer_ = {}
def templateTimer(templateName,timeInv):
    return False
# return true if template is enable
def isTemplateEnable(templateName):
    if templateName in templateDisableTimer_:
        return templateDisableTimer_[templateName] <= 0
    else:
        templateDisableTimer_.setdefault(templateName,0)
        return True
# TODO ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def match(templateName):
    global template_
    template = findTemplate(templateName)
    res = cv2.matchTemplate(frame_,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val,max_loc

def debugShowImage(res):
    cv2.imshow('',res)
    cv2.waitKey()

# action ----------------------------------------------------

hasAction_ = False # if has tap in the frame, reset frame delay

def actionDealy():
    curDelay = 0.1 + 0.1 * random.random()
    time.sleep(curDelay)
    # offsetCurrnetFrameDelay(-curDelay)

def tap(x ,y):
    global driver_,canvas_
    global hasAction_
    try:
        webdriver.ActionChains(driver_).move_to_element_with_offset(canvas_, x , y).click().perform()
    except:
        print('webdriver error: tap')
        time.sleep(3)
        main()
        pass
    
    # check lib/selenium/webdriver/common/interactions/pointer_actions  
    # default_move_duration = 34
    actionDealy()
    hasAction_ = True
    printWithTime(f'tap {x},{y}')

def scroll(x ,y,offsetX,offsetY):
    global driver_,canvas_
    global hasAction_
    try:
        webdriver.ActionChains(driver_).move_to_element_with_offset(canvas_, x , y).click_and_hold().pause(0.1).move_to_element_with_offset(canvas_,x+offsetX,y+offsetY).release().perform()
    except:
        print('webdriver error: scroll')
        time.sleep(3)
        main()
        pass
    
    # check lib/selenium/webdriver/common/interactions/pointer_actions  
    # default_move_duration = 34
    actionDealy()
    hasAction_ = True
    printWithTime(f'scroll {x},{y} offset {offsetX},{offsetY}')

def tapIfFind(templateName):
    max_val,max_loc = match(templateName)
    x,y = max_loc

    threshold = 0.97
    # print(f"{templateName}:{round(res[y,x],2)}")
    if max_val > threshold:
        printWithTime(f'find {templateName} : {x},{y} ({max_val})')
        tap(x,y)
        return True
    return False

def TryFind(templateName):
    max_val,max_loc = match(templateName)
    x,y = max_loc

    threshold = 0.97
    # print(f"{templateName}:{round(res[y,x],2)}")
    if max_val > threshold:
        printWithTime(f'find {templateName} : {x},{y} ({max_val})')
        return True
    return False

def doNotFindTimer(templateName,timeMs):
    return 0

# script ----------------------------------------------------

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
        # time.sleep(5)
        # tap(565,598)
        # time.sleep(1)
        # tap(565,486)
    elif tapIfFind('eventGacha_onemore'):None
    else:
        return False
    return True
def raidboss():
    if 0:None
    elif tapIfFind('raid_sanka_autorun'):None
    elif tapIfFind('raid_sanka_vh2'):None
    # elif tapIfFind('raid_sanka_vh3'):None
    elif TryFind('raid_sanka_isFriendPage'):
        tap(829,540)
        time.sleep(2)
    elif TryFind('raid_sanka_searchfaildcount0') and not TryFind('battleOutofStamina2') :
        tap(902,602)
        # TODO : disableTemplateTimer('raid_sanka_searchfaildcount0',10000)
        time.sleep(2)
    # elif tapIfFind('raid_sanka_vh1'):None
    elif tapIfFind('raid_sanka_friend'):None
    elif tapIfFind('raid_sanka'):None
    elif tapIfFind('raid_sanka_confirm'):None
    else:
        return False
    return True
def altar():
    if 0:None
    elif TryFind('altarNextQuest'):
        tap(932,553)
        time.sleep(2)
        tap(656,485)
        time.sleep(2)
    else:
        return False
    return True

f_hasbeenDisconnect_ = False
# test scrip
print('Stript Loop Start --')
while 1:
    # TODO frame start
    frame = updateFrame()
    hasAction_ = False
    frameDelayHasBeenChanged_ = False

    # -------------------------------
    if 0:None
    elif eventGacha():None
    # elif altar():None
    elif raidboss():None

    # change day window
    elif TryFind('changeDay') or TryFind('errorRestart'):
        gameRestart()
        f_hasbeenDisconnect_ = True
    
    # mainQuest2-5
    elif tapIfFind('questNormalUnselect'):None
    elif tapIfFind('autorunConfirm'):None
    elif tapIfFind('autorun'):None
    elif TryFind('mainQuest2-5N'):
        tap(1000,532)
    elif tapIfFind('mainQuestStage2'):None
    elif TryFind('mainQuestStage'):
        tap(253,515)
        setCurrnetFrameDelay(0.2)
    elif tapIfFind('mainquest'):None
    elif tapIfFind('quest'):None

    # recover stamina
    elif TryFind('recoverStaminaMenu'):
        print('chain tap start: recoverStamina')
        time.sleep(2)
        scroll(1021,455,0,-300)
        time.sleep(2)
        tap(279,448)
        time.sleep(2)
        tap(698,367)
        time.sleep(2)
        tap(650,525)
        time.sleep(2.5)
        tap(567,477)
        time.sleep(2)
        tap(566,538)
        time.sleep(2)
        tap(903,602)
        time.sleep(2)
        tap(656,484)
        time.sleep(0.5)
        print('chain tap end : recoverStamina')
    elif TryFind('battleOutofStamina2'):
        tap(647,482)
    # battle
    elif tapIfFind('battleContinue'):
        f_hasbeenDisconnect_ = True
    elif tapIfFind('battleLoseAndContinue'):None
    elif f_hasbeenDisconnect_ and tapIfFind('battleEndNextBtn'):
        f_hasbeenDisconnect_ = False
    

    # login
    elif TryFind('loginGear'):
        tap(533,540)
    elif tapIfFind('InfoPageCanClose'):None
    elif tapIfFind('InfoPageCanClose2'):None #for 10day login bound 1
    elif tapIfFind('InfoPageCanClose3'):None #for 10day login bound 2
    elif tapIfFind('InfoPageSkip'):None
    elif TryFind('InfoPageCantClose'):
        tap(701,594)
    elif tapIfFind('login_round1'):None
    elif tapIfFind('login_round2'):None


    # other
    # elif tapIfFind('StorySkipConfirm'):None

    

    frameEnd() # ----------------

       



