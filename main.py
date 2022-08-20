from asyncore import read
from ppadb.client import Client
import pytesseract
from PIL import Image
import re
import time
import os
import xml.etree.ElementTree as ET
import subprocess

#am start -a android.intent.action.VIEW -d https://appinio.page.link/MbkH

def main(x_device):
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
    #device = adb.device("emulator-5554")

    
    devices = adb.devices()
    #print(devices)

    if len(devices) == 0:
        print('loading')
        main()

    device = devices[x_device]

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
        #device = adb.device("emulator-5554")

        
        devices = adb.devices()
        #print(devices)

        if len(devices) == 0:
            print('loading')
            main()

        device = devices[x_device]

        nolevel = False
        nopresent = False

        device.shell("uiautomator dump")
        device.pull("/sdcard/window_dump.xml","./dumps/"+device_name+"_window_dump.xml")

        with open("./dumps/"+device_name+'_window_dump.xml',encoding='utf-8') as f:
            final_output = f.read()

        element = ET.XML(final_output)
        ET.indent(element)
        final_output = str(ET.tostring(element, encoding='unicode'))

        with open("./dumps/"+device_name+'_window_dump.xml', 'w', encoding='utf-8') as f:
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
                print("LEVEL DIALOG CLOSED")
                nolevel = True
        except:
            nolevel = False
        
        #Present Notification
        try:
            present_element = root[0][0][0][0][0][0][0][0][0][0]
            #print(present_element.attrib["content-desc"])
            #print(present_element.attrib["NAF"])
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
                    device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50") 
                    time.sleep(1)
                    print("PRESENT OPENED")
                    nopresent = False
        except:
            nopresent = False
        

        print("LEVEL_NOTY:",nolevel,"PRESENT_NOTY:",nopresent)
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
                print("CLICK X:",Xpoint,"CLICK Y",Ypoint)
                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50") 
            except:
                device.shell(f'input tap {middle[0]} {middle[1]}')
                device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50")  

if __name__ == '__main__':
    x2 = ""
    count = 0
    stream = os.popen('adb devices')
    output = stream.read().splitlines()
    output.pop(len(output)-1)
    output.pop(0)

    for x in output:
        x = x.replace("device","online")
        x2 = x2 + x + " " + str(count) +"\n"
        count += 1
        output = x2
    print(output)
    print("Choose:")
    main(int(input()))