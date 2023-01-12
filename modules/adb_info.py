import subprocess
from ppadb.client import Client

def get_connected_devices():
    """
    Gibt eine Liste der verbundenen ADB-Geräte zurück.
    """
    devices = []
    output = subprocess.check_output([".\\platform-tools\\adb.exe", "devices"]).decode("utf-8")
    for line in output.split("\n"):
        if "device" in line:
            devices.append(line.split("\t")[0])
    return devices

def get_foreground_activity(x_device):
    """
    Gibt den Namen der Vordergrund-Activity eines ADB-Geräts zurück.
    """
    adb = Client(host='127.0.0.1', port=5037)
    device = adb.devices()[x_device]
    output = device.shell("dumpsys window windows")
    output_str = str(output)
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

def get_screen_center(x_device):
    """
    Gibt die Koordinaten des Mittelpunkts des Bildschirms eines ADB-Geräts zurück.
    """
    adb = Client(host='127.0.0.1', port=5037)
    device = adb.devices()[x_device]
    center = str(device.shell("wm size"))
    if ("Override" in center):
        center = center.splitlines()[1].split(" ")[2].replace("\n","").split("x")
    else:
        center = center.split(" ")[2].replace("\n","").split("x")

    center = int(center[0])/2,int(center[1])/2
    return center
