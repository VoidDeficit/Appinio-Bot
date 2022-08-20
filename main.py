from asyncore import read
from ppadb.client import Client
import pytesseract
from PIL import Image
import re
import time
import os
import xml.etree.ElementTree as ET
import subprocess


def main():
    stream= os.popen('adb start-server')
    output = stream.read()
    output

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    share_link = "https://appinio.page.link/"
    nolevel = False
    nopresent = False
    
    adb = Client(host='127.0.0.1', port=5037)
    #adb.remote_connect("127.0.0.1", 62001)

    #device = adb.device("57ab1a35")
    device = adb.device("emulator-5554")

    """
    devices = adb.devices()
    print(devices)

    if len(devices) == 0:
        print('loading')
        main()

    device = devices[1]
    """

    device_name = str(device).split(" ")[3].replace(">","")
    print("ID:",device_name)  

    middle = str(device.shell("wm size")).split(" ")[2].replace("\n","").split("x")
    middle = int(middle[0])/2,int(middle[1])/2
    print("CENTER:",middle)
    
    while(True):
        final_output = ""
        adb = Client(host='127.0.0.1', port=5037)
        #adb.remote_connect("127.0.0.1", 62001)

        #device = adb.device("57ab1a35")
        device = adb.device("emulator-5554")

        nolevel = False
        nopresent = False

        image = device.screencap()
        with open('phone.png', 'wb') as f:
            f.write(image) 

        device.shell("uiautomator dump")
        device.pull("/sdcard/window_dump.xml","window_dump.xml")

        with open('window_dump.xml',encoding='utf-8') as f:
            final_output = f.read()

        element = ET.XML(final_output)
        ET.indent(element)
        final_output = str(ET.tostring(element, encoding='unicode'))

        with open('window_dump.xml', 'w', encoding='utf-8') as f:
            f.write(final_output)

        root = ET.fromstring(final_output)
        #print(root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][3].attrib)

        #level Notification 
        try:
            level_element = root[0][0][0][0][0][0][0][0][0][2]
            if ("Level" in level_element.attrib["content-desc"]):
                print(level_element.attrib["content-desc"])
                levelup_element = root[0][0][0][0][0][0][0][0][0][4]

                bounds = levelup_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)

                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                device.shell(f'input tap {Xpoint} {Ypoint}')
                nolevel = True
        except:
            nolevel = False
        
        #Present Notification
        try:
            present_element = root[0][0][0][0][0][0][0][0][0][0]
            print(present_element.attrib["content-desc"])
            print(present_element.attrib["NAF"])
            if (present_element.attrib["NAF"]) == "true":
                bounds = present_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)

                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                device.shell(f'input tap {Xpoint} {Ypoint}')
                nopresent = True

                present_button_element = root[0][0][0][0][0][0][0][0][0][3]
                print(present_button_element.attrib["content-desc"])
                if (present_button_element.attrib["content-desc"]) == "Coins erhalten":
                    bounds = present_button_element.attrib["bounds"]
                    coord = bounds[:len(bounds)-1].replace("[","")
                    coord = re.split(r'[,\]]+', coord)

                    Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                    Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                    device.shell(f'input tap {Xpoint} {Ypoint}')
                    device.shell("input swipe 500 1000 500 300 50")
                    time.sleep(1)
                    nopresent = False
        except:
            nopresent = False
        

        print(nolevel,nopresent)
        if not nolevel and not nopresent:
            try:
                #14
                click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][3]

                #Check if android.widget.ImageView
                if str(click_element.attrib["class"]) == "android.widget.ImageView":
                    click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][4]
                    if str(click_element.attrib["class"]) == "android.widget.ImageView":
                        click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][5]

                bounds = click_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)
                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])
                print(Xpoint,Ypoint)
                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell("input swipe 500 1000 500 300 50")
            except:
                device.shell(f'input tap {middle[0]} {middle[1]}')
                device.shell("input swipe 500 1000 500 300 50")
        
    
def appinio_login(device,email,pws):
    #Clear Appinio Data
    device.shell('pm clear com.appinio.appinio')

    #Open and go to login page
    device.shell('monkey -p com.appinio.appinio -c android.intent.category.LAUNCHER 1')
    time.sleep(3)
    device.shell('input tap 448 47')
    time.sleep(0.1)
    device.shell('input tap 448 47')
    time.sleep(1)
    device.shell('input tap 60 176')

    #Input Email Password
    email = "xober18891@agrolivana.com"
    device.shell(f'input text {email}')
    device.shell('input tap 52 266')
    time.sleep(0.1)

    #Input Password
    pws = "HcU2wAqmn-K3" 
    device.shell(f"input text {pws}")
    device.shell('input tap 270 922')
    time.sleep(3.5)
    device.shell('input tap 262 479')

def open_touchmacropro(device):
    #Start TouchMacroPro Overlay
    device.shell('monkey -p com.jake.touchmacro.pro -c android.intent.category.LAUNCHER 1')
    time.sleep(1)
    device.shell('input touchscreen tap 270 500')
    time.sleep(6.5)

    #Start Macro
    #device.shell('input touchscreen tap 20 42')

def check_for_level_and_present(device,device_name):
    #Get Screen
    image = device.screencap()
    with open(device_name+'.png', 'wb') as f:
        f.write(image) 

    im = Image.open(device_name+'.png')
    width, height = im.size

    #Crop Screen Picture just to level element
    left = 224
    top = 528
    right = 315
    bottom = 556

    im1 = im.crop((left, top, right, bottom))
    im1.save(device_name+'_Level.png')

    #Crop Screen Picture just to present element
    left = 87
    top = 561
    right = 453
    bottom = 586

    im1 = im.crop((left, top, right, bottom))
    im1.save(device_name+'_Present.png')

    #Read Image for level with OCR engine
    tmp_dpa_level = str(pytesseract.image_to_string(Image.open(device_name+'_Level.png')))
    #print(tmp_dpa_level)

    #Read Image for present with OCR engine
    tmp_dpa_present = str(pytesseract.image_to_string(Image.open(device_name+'_Present.png')))
    #print(tmp_dpa_present)

    #Remove Images
    os.remove(device_name+'.png')
    os.remove(device_name+'_Level.png')
    os.remove(device_name+'_Present.png')
    
    #Close dialogs
    if ("Level") in tmp_dpa_level:
        tmp_level = tmp_dpa_level.split(" ")[1]
        print(tmp_level)
        device.shell('input tap 493 325')

    if ("Klicke auf die Truhe, um sie zu 6ffnen") in tmp_dpa_present:
        device.shell('input tap 267 450')
        time.sleep(0.1)
        device.shell('input tap 270 647')
        print("pressed")
    

if __name__ == '__main__':
    main()