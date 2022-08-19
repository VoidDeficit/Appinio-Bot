from ppadb.client import Client
import pytesseract
from PIL import Image
import time
import os
import xml.etree.ElementTree as ET

def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    adb = Client(host='127.0.0.1', port=5037)
    #adb.remote_connect("127.0.0.1", 62001)
    devices = adb.devices()

    if len(devices) == 0:
        print('loading')
        main()

    device = devices[0]
    device_name = str(device).split(" ")[3].replace(">","")
    print("ID:",device_name)  
    
    Android_XML = os.popen('adb exec-out uiautomator dump /dev/tty')
    output = Android_XML.read().replace("UI hierchary dumped to: /dev/tty","")
    element = ET.XML(output)
    ET.indent(element)
    final_output = ET.tostring(element, encoding='unicode')

    with open('Android_XML.xml', 'w') as f:
        f.write(final_output)

    root = ET.fromstring(output)

    print(root)

    for child in root:
        print(child.tag, child.attrib)

    for neighbor in root.iter('Ich bleibe bei ihr und Pflege sie'):
        print(neighbor.attrib)

    
    
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