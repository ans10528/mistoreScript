from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

import cv2

import numpy as np
import time
import array
import math

GameUri = "http://pc-play.games.dmm.co.jp/play/MistTrainGirlsX/"
UserAccount = '' #akt72... // asJ. // bf4.t
UserPassword = ''

Driver = 0
Canvas = 0
DebuggerAddress = '127.0.0.1:9222'

#Canvas Crop (board4,scroll86)
CanvasShiftX = 2
CanvasShiftY = 6
CanvasWidth = 1136
CanvasHeight = 640

Frame = 0

def chromeConfig():
    global Driver
    global DebuggerAddress

    # use current browser
    originChrome = webdriver.ChromeOptions()
    originChrome.debugger_address=DebuggerAddress
    Driver = webdriver.Chrome(options=originChrome)

def isGameSite():
    return Driver.current_url != GameUri

def gameLogin():
    '''Login DMM service'''
    global Driver
    if isGameSite():
        Driver.get(GameUri)
    
    #login
    global UserAccount
    global UserPassword

    if isGameSite():
        time.sleep(3)
        accountTextbox = Driver.find_element_by_id("login_id")
        passwordTextbox = Driver.find_element_by_id("password")
        accountTextbox.clear()
        accountTextbox.send_keys(UserAccount)
        passwordTextbox.clear()
        passwordTextbox.send_keys(UserPassword)
        passwordTextbox.send_keys(Keys.RETURN)
        time.sleep(4) #waiting for login

def windowConfig():
    '''resize window and locate gameCanvas'''
    #1156,648 +17,87
    Driver.set_window_size(1173, 735)
    js="var aaa = document.documentElement.scrollTop=70"  
    Driver.execute_script(js)  
    #time.sleep(1) #waiting for resize window
    # locate: iframe game_frame frm1
    Driver.switch_to.frame("game_frame")
    Driver.switch_to.frame("frm1")
    global Canvas
    Canvas = Driver.find_element_by_id("GameCanvas")
    # TODO: if canvas not found
    global CanvasWidth
    global CanvasHeight
    CanvasWidth = math.ceil(Canvas.size["width"])
    CanvasHeight = math.ceil(Canvas.size["height"])

def getFrame() -> bytes:
    global Driver
    global CanvasShiftX,CanvasShiftY,CanvasWidth,CanvasHeight
    scr_png = Driver.get_screenshot_as_png()

    # cv method
    nparr = np.frombuffer(scr_png, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    # canvas crop
    img = img[CanvasShiftY:CanvasShiftY+CanvasHeight,
                CanvasShiftX:CanvasShiftX+CanvasWidth]

    return img

def tap(x ,y):
    global Driver
    global Canvas
    webdriver.ActionChains(Driver).move_to_element_with_offset(Canvas, x, y).click().perform()
    time.sleep(0.33)

#---------------------------------------------------------------

def main():
    global Driver,Frame

    #connect browser (init)
    chromeConfig()
    gameLogin()
    windowConfig()
    
    #test frame
    if 0:
        testFrameCv = getFrame()
        cv2.imwrite(r'.\curFrameCvPng.png',testFrameCv)
        cv2.namedWindow('My Image', cv2.WINDOW_GUI_EXPANDED | cv2.WINDOW_AUTOSIZE)
        cv2.imshow('My Image', testFrameCv)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    Frame = getFrame()
    #main scrip





    #tap(100,500)

#---------------------------------------------------------------
main()
time.sleep(999999) #loop