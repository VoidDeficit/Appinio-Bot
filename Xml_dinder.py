#coding=utf-8

import tempfile
import os
import re
import time
import xml.etree.cElementTree as ET

class Element(object):
    """
    Positioning through elements requires Android 4.0 or higher
    """
    def __init__(self):
        """
        Initialize, obtain the system temporary file storage directory, and define the matching number pattern
        """
        self.tempFile = tempfile.gettempdir()
        self.pattern = re.compile(r"\d+")

    def __uidump(self):
        """
        Get the current Activity control tree
        """
        os.popen("adb shell uiautomator dump/data/local/tmp/uidump.xml")
        os.popen("adb pull/data/local/tmp/uidump.xml "+ self.tempFile)

    def __element(self, attrib, name):
        """
        A single element with the same attribute, returns a single coordinate tuple
        """
        self.__uidump()
        tree = ET.ElementTree(file=self.tempFile + "\\uidump.xml")
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])

                return Xpoint, Ypoint


    def __elements(self, attrib, name):
        """
        Multiple elements with the same attribute, return a list of coordinate tuples
        """
        list = []
        self.__uidump()
        tree = ET.ElementTree(file=self.tempFile + "\\uidump.xml")
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2])-int(coord[0]))/2.0 + int(coord[0])
                Ypoint = (int(coord[3])-int(coord[1]))/2.0 + int(coord[1])
                list.append((Xpoint, Ypoint))
        return list

    def findElementByName(self, name):
        """
        Target by element name
        usage: findElementByName(u"Settings")
        """
        return self.__element("text", name)

    def findElementsByName(self, name):
        return self.__elements("text", name)

    def findElementByClass(self, className):
        """
        Locate by element class name
        usage: findElementByClass("android.widget.TextView")
        """
        return self.__element("class", className)

    def findElementsByClass(self, className):
        return self.__elements("class", className)

    def findElementById(self, id):
        """
        Locate by the resource-id of the element
        usage: findElementsById("com.android.deskclock:id/imageview")
        """
        return self.__element("resource-id",id)

    def findElementsById(self, id):
        return self.__elements("resource-id",id)

class Event(object):
    def __init__(self):
        os.popen("adb wait-for-device ")

    def touch(self, dx, dy):
        """
        Touch event
        usage: touch(500, 500)
        """
        os.popen("adb shell input tap "+ str(dx) +" "+ str(dy))
        time.sleep(0.5)

def test():
    element = Element()
    evevt = Event()

    e1 = element.findElementByName(u"1号店")
    evevt.touch(e1[0], e1[1])
    time.sleep(1)

    e2 = element.findElementByName(u"Mobile phone recharge")
    evevt.touch(e2[0], e2[1])