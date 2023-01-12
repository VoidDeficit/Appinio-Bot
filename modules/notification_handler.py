from ppadb.client import Client
import re
import time
import xml.etree.ElementTree as ET

def check_out_of_questions(root):
    """
    Überprüft, ob das Ende der Fragen erreicht wurde.
    """
    lastAction = ""
    noquestions = ""
    try:
        # Überprüfe, ob das Layout neu ist oder nicht
        try:
            none_questions = root[0][0][0][0][0][0][0][0][0][0][0][0][0][0]
        except:
            none_questions = root[0][0][0][0][0][0][0][0][0][0][0][5][0][0]

        if ("Du hast das Ende erreicht." in none_questions.attrib["content-desc"]):
            lastAction = "Out of questions"
            noquestions = True
    except:
        noquestions = False

    return lastAction, noquestions

def check_level_notification(root, x_device):
    """
    Überprüft, ob eine Benachrichtigung über ein neues Level vorliegt.
    """
    adb = Client(host='127.0.0.1', port=5037)
    device = adb.devices()[x_device]
    lastAction = ""
    nolevel = ""
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

    return lastAction, nolevel

def check_present_notification(root, x_device, center):
    """
    Überprüft, ob eine Benachrichtigung über ein neues Geschenk vorliegt.
    """
    adb = Client(host='127.0.0.1', port=5037)
    device = adb.devices()[x_device]
    lastAction = ""
    nopresent = ""
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
            lastAction = "PRESENT OPENED"

            present_button_element = root[0][0][0][0][0][0][0][0][0][3]
            #print(present_button_element.attrib["content-desc"])
            if (present_button_element.attrib["content-desc"]) == "Coins erhalten":
                bounds = present_button_element.attrib["bounds"]
                coord = bounds[:len(bounds)-1].replace("[","")
                coord = re.split(r'[,\]]+', coord)

                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {center[0]} {center[1]+center[1]/2} {center[0]} {center[1]-center[1]/2} 50") 
                nopresent = False
                lastAction = "PRESENT CLOSED"
    except:
        nopresent = False

    return lastAction, nopresent
