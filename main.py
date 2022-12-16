from ppadb.client import Client
import re
import time
import os,glob
from os.path import exists
import xml.etree.ElementTree as ET
import subprocess


def get_connected_devices():
    devices = []
    output = subprocess.check_output([".\\platform-tools\\adb.exe", "devices"]).decode("utf-8")
    for line in output.split("\n"):
        if "device" in line:
            devices.append(line.split("\t")[0])
    return devices

def get_foreground_activity(output):
    output_str = output
    lines = output_str.split("\n")
    for line in lines:
        if "mCurrentFocus" in line:
            # Der Name der Activity befindet sich zwischen den ersten zwei '/'
            line = line.split()[2].split('/')[0]
            return line
        else:
            if "imeLayeringTarget" in line:
                line = line.split()[6].split('/')[0]
                return line
    return None

def main(x_device):
    share_link = "https://appinio.page.link/"
    nolevel = False
    nopresent = False
    noquestions = False
    
    adb = Client(host='127.0.0.1', port=5037)
    
    devices = adb.devices()
    device = devices[x_device]

    device_name = str(device).split(" ")[3].replace(">","")
    #print("ID:",device_name)            

    #device.shell("am start -a android.intent.action.VIEW -d https://appinio.page.link/####")
    
    #Get the center of the screen
    middle = str(device.shell("wm size"))
    if ("Override" in middle):
        middle = middle.splitlines()[1].split(" ")[2].replace("\n","").split("x")
    else:
        middle = middle.split(" ")[2].replace("\n","").split("x")
        
    middle = int(middle[0])/2,int(middle[1])/2
    print("CENTER:",middle)

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

        #Check if Appinio is opened
        if not "com.appinio.appinio" in get_foreground_activity(device.shell("dumpsys window windows")):
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
                #device.shell(f"input swipe {middle[0]} {middle[1]-middle[1]/2} {middle[0]} {middle[1]+middle[1]/2} 50")
                #device.shell("am force-stop com.appinio.appinio")
                #time.sleep(1)
                #device.shell("monkey -p com.appinio.appinio -c android.intent.category.LAUNCHER 1")
                #device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50") 
                #print("You've reached the end")
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
                print("LEVEL DIALOG CLOSED")
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
                    device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50") 
                    time.sleep(1)
                    print("PRESENT OPENED")
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
                print("CLICK X Y:",Xpoint,Ypoint)
                device.shell(f'input tap {Xpoint} {Ypoint}')
                device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50") 
            except:
                device.shell(f'input tap {middle[0]} {middle[1]}')
                device.shell(f"input swipe {middle[0]} {middle[1]+middle[1]/2} {middle[0]} {middle[1]-middle[1]/2} 50")  

if __name__ == '__main__':
    """
    if len(devices) == 0:
        print('loading')
        main()

    if not exists("last_connections.txt"):
        print("Loading Emulators")
        cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File", ".\cmd.ps1"]  # Specify relative or absolute path to the script
        #ec = subprocess.call(cmd)
        ec = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = ec.communicate()
        #print("Powershell returned: {0:d}".format(ec))
        with open("last_connections.txt", 'w', encoding='utf-8') as f:
            f.write(str(out.decode('utf-8')))
    """
    
    devices = get_connected_devices()
    devices.pop(0)

    count = 0
    for x in devices:
        print ('{:<15}'.format(x)+" "+str(count))
        count += 1
    print("Choose:")
    main(int(input()))
