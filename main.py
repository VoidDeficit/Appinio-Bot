from ppadb.client import Client
import re
import os,glob
from functools import reduce
from operator import getitem
from os.path import exists
import xml.etree.ElementTree as ET
import subprocess
import modules.retrive_port as retrive_port
import modules.adb_info as adb_info

share_link = "https://appinio.page.link/"

def get_element(root,index_list):
    for i in index_list:
        if len(root) > i:
            root = root[i]
        else:
            raise IndexError("child index out of range")
    return root

def check_end_of_questions(root):
    index_list = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0]]
    for i in index_list:
        try:
            none_questions = reduce(getitem, i, root)
            if "Du hast das Ende erreicht." in none_questions.attrib["content-desc"]:
                return True
        except (IndexError, KeyError, AttributeError):
            continue
    return False

def check_levelup_notification(root, device):
    """
    Überprüft, ob eine Benachrichtigung über ein neues Level vorliegt.
    """
    try:
        level_element = root[0][0][0][0][0][0][0][0][0][2]
        if ("Level" in level_element.attrib["content-desc"]):
            levelup_element = root[0][0][0][0][0][0][0][0][0][4]

            bounds = levelup_element.attrib["bounds"]
            coord = bounds[:len(bounds)-1].replace("[","")
            coord = re.split(r'[,\]]+', coord)

            Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
            Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

            device.shell(f'input tap {Xpoint} {Ypoint}')
            return True
    except:
        return False

def open_present(root, device, center):
    try:
        present_element = root[0][0][0][0][0][0][0][0][0][0]
        if (present_element.attrib["NAF"]) == "true":
            bounds = present_element.attrib["bounds"]
            coord = bounds[:len(bounds)-1].replace("[","")
            coord = re.split(r'[,\]]+', coord)

            Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
            Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

            device.shell(f'input tap {Xpoint} {Ypoint}')

            present_button_element = root[0][0][0][0][0][0][0][0][0][3]
            if (present_button_element.attrib["content-desc"]) == "Coins erhalten":
                bounds = present_button_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)

                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
                return True
    except:
        pass
    return False

def main(x_device):
    nolevel = False
    nopresent = False
    noquestions = False
    click = False
    lastAction = ""
    lastActionOld = ""
    repetition = 1
    
    adb = Client(host='127.0.0.1', port=5037)
    device = adb.devices()[x_device]

    device_name = str(device).split(" ")[3].replace(">","")
    #print("ID:",device_name)    
    
    #device.shell("am start -a android.intent.action.VIEW -d "+share_link+"####")
    #time.sleep(2)    
    
    center = adb_info.get_screen_center(x_device)
    #print("CENTER:", center)

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
        click = False


        #Check if Appinio is opened
        if not "com.appinio.appinio" in adb_info.get_foreground_activity(x_device):
            anser = input("Please open Appinio\nPress Enter to continue:\n").lower()
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

        noquestions = check_end_of_questions(root)
        if noquestions:
            lastAction = "OUT OF QUESTIONS"

        nolevel = check_levelup_notification(root, device)
        if nolevel:
            lastAction = "LEVEL DIALOG CLOSED"
        
        nopresent = open_present(root, device, center)    
        if nopresent:
            lastAction = "PRESENT CLOSED"

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
                    try:
                        click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][3]
                        #Check if android.widget.ImageView
                        if str(click_element.attrib["class"]) == "android.widget.ImageView":
                            click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][4]
                            if str(click_element.attrib["class"]) == "android.widget.ImageView":
                                click_element = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0][5]
                    except:
                        try:
                            click_element = root[0][0][0][0][0][0][0][0][0][0][0][4][0][0][3]
                            #Check if android.widget.ImageView
                            if str(click_element.attrib["class"]) == "android.widget.ImageView":
                                click_element = root[0][0][0][0][0][0][0][0][0][0][0][4][0][0][4]
                                if str(click_element.attrib["class"]) == "android.widget.ImageView":
                                    click_element = root[0][0][0][0][0][0][0][0][0][0][0][4][0][0][5]
                        except:
                            try:
                                click_element = root[0][0][0][0][0][0][0][0][0][0][0][3][0][0][3]
                                #Check if android.widget.ImageView
                                if str(click_element.attrib["class"]) == "android.widget.ImageView":
                                    click_element = root[0][0][0][0][0][0][0][0][0][0][0][3][0][0][4]
                                    if str(click_element.attrib["class"]) == "android.widget.ImageView":
                                        click_element = root[0][0][0][0][0][0][0][0][0][0][0][3][0][0][5]
                            except:
                                pass

                bounds = click_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)
                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])
                #print("CLICK X Y:",Xpoint,Ypoint)
                lastAction = "QUESTIONS ANSWER"
                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
            except:
                lastAction = "EVERYTHING HAS FAILED"
                device.shell(f'input tap {center[0]} {center[1]}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50")  
                    
            
        if lastAction == lastActionOld:
            repetition = repetition + 1
        else:
            repetition = 1

        print(f"                             ", end='\r')
        print(lastAction,repetition, end='\r')
        lastActionOld = lastAction


if __name__ == '__main__':
    output = ''
    adb_ports = retrive_port.adbPort()
    for adb_port in adb_ports:
        output = subprocess.run(['.\\platform-tools\\adb.exe', 'connect', '127.0.0.1:' + adb_port], capture_output=True)
        if "bad port number" in str(output.stdout.decode()):
            print("No Bluestacks X instances found")
        if not adb_port == "none" and not ("already" in str(output.stdout.decode())):
            print("Connecting to Bluestacks X")
    
    devices = adb_info.get_connected_devices()
    devices.pop(0)

    if not (devices == []):
        count = 0
        for x in devices:
            print ('{:<15}'.format(str(x))+" "+str(count))
            count += 1
        print("Choose:")
        main(int(input()))
    else:
        print("No devices found")
