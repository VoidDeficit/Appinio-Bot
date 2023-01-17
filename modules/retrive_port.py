import os
path = "C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"

def adbPort():
    adb_port = ""
    adb_ports = []
    if os.path.exists(path):
        with open(path, "r") as file:
            for line in file:
                if "status.adb_port=" in line:
                    adb_port = line.split("=")[1].replace("\"", "").strip()
                    adb_ports.append(adb_port)
    else:
        adb_ports.append("none")
        return adb_ports

    return adb_ports