from ppadb.client import Client
import re
import time
import os,glob
from os.path import exists
import xml.etree.ElementTree as ET
import subprocess
import modules.retrivePort as retrivePort
import modules.adbInfo as adbInfo

share_link = "https://appinio.page.link/"


def main(x_device):
    nolevel = False
    nopresent = False
    noquestions = False
    
    adb = Client(host='127.0.0.1', port=5037)
    
    devices = adb.devices()
    device = devices[x_device]

    device_name = str(device).split(" ")[3].replace(">","")
    #print("ID:",device_name)    
    
    #device.shell("am start -a android.intent.action.VIEW -d "+share_link+"####")
    #time.sleep(2)    
    
    center = adbInfo.get_screen_center(device)
    print("CENTER:", center)

    if exists("./dumps/"):
        files = glob.glob('./dumps/*')
        for f in files:
            os.remove(f)
    
    while(True):
        final_output = ""
        adb = Client(host='127.0.0.1', port=5037)
        
        devices = adb.devices()
        device = devices[x_device]

        nolevel = False
        nopresent = False
        noquestions = False
        lastAction = "none"

        #Check if Appinio is opened
        if not "com.appinio.appinio" in adbInfo.get_foreground_activity(device.shell("dumpsys window windows")):
            anser = input("Please open Appinio\nEnter any to continue:\n").lower()
            if anser == "y":
                main(x_device)
            else:
                main(x_device)

        device.shell("uiautomator dump")

        if not exists("./dumps/"):
            os.mkdir("./dumps/")

        device.pull("/sdcard/window_dump.xml","./dumps/"+device_name+"_window_dump.xml")

        with open("./dumps/"+device_name+'_window_dump.xml',encoding='utf-8') as f:
            final_output = f.read()

        element = ET.XML(final_output)
        ET.indent(element)
        final_output = str(ET.tostring(element, encoding='unicode'))

        with open("./dumps/"+device_name+'_window_dump.xml', 'w', encoding='utf-8') as f:
            f.write(final_output)

        root = ET.fromstring(final_output)


        #Out Of Questions
        try:
            #check if layout is new or not
            try:
                none_questions = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0]
            except:
                none_questions = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0]

            if ("Du hast das Ende erreicht." in none_questions.attrib["content-desc"]):
                #print("Out of questions")
                #device.shell(f"input swipe {center[0]} {center[1]-center[1]/2} {center[0]} {center[1]+center[1]/2} 50")
                #device.shell("am force-stop com.appinio.appinio")
                #time.sleep(1)
                #device.shell("monkey -p com.appinio.appinio -c android.intent.category.LAUNCHER 1")
                #device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
                #print("You've reached the end")
                lastAction = "Out of questions"
                time.sleep(5)
                noquestions = True
        except:
            noquestions = False

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
                lastAction = "LEVEL DIALOG CLOSED"
                nolevel = True
        except:
            nolevel = False
        
        #Present Notification
        try:
            present_element = root[0][0][0][0][0][0][0][0][0][0]
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
                    device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
                    time.sleep(1)
                    lastAction = "PRESENT OPENED"
                    nopresent = False
        except:
            nopresent = False

        if not nolevel and not nopresent and not noquestions:
            try:
                #check if layout is new or not
                try:
                    click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][3]
                    #Check if android.widget.ImageView
                    if str(click_element.attrib["class"]) == "android.widget.ImageView":
                        click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][4]
                        if str(click_element.attrib["class"]) == "android.widget.ImageView":
                            click_element = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0][5]
                except:
                    click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][3]
                    #Check if android.widget.ImageView
                    if str(click_element.attrib["class"]) == "android.widget.ImageView":
                        click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][4]
                        if str(click_element.attrib["class"]) == "android.widget.ImageView":
                            click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][5]


                bounds = click_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)
                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])
                #print("CLICK X Y:",Xpoint,Ypoint)
                lastAction = "CLICK"
                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
            except:
                device.shell(f'input tap {center[0]} {center[1]}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50")  
        
        print(f"                                       ", end='\r')
        print(f"{lastAction}", end='\r')

if __name__ == '__main__':
    
    adb_port = retrivePort.adbPort()
    output = subprocess.run(['.\\platform-tools\\adb.exe', 'connect', '127.0.0.1:' + adb_port], capture_output=True)
    if not ("already" in str(output.stdout.decode())):
        print("Connecting to Bluestacks X")
    
    devices = adbInfo.get_connected_devices()
    devices.pop(0)

    count = 0
    for x in devices:
        print ('{:<15}'.format(str(x).replace('127.0.0.1:' + adb_port, "Bluestacks X"))+" "+str(count))
        count += 1
    print("Choose:")
    main(int(input()))
