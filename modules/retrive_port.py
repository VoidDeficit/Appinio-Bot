import os
path = "C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"

def adbPort():
    adb_port = ""
    if os.path.exists(path):
        with open(path, "r") as file:
            for line in file:
                if "bst.instance.Nougat64.status.adb_port=" in line:
                    adb_port = line.split("=")[1].replace("\"", "").strip()
                    return adb_port
    else:
        #print("File not found")
        adb_port = "none"
        return adb_port