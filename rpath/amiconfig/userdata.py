#
# Copyright (c) 2007 rPath, Inc.
#

from ConfigParser import ConfigParser, RawConfigParser

from amiconfig.errors import *

class INIFileStub:
    def __init__(self, contents, name=None):
        self.__contents = contents.split('\n')
        self.__pos = 0
        self.__sectre = RawConfigParser.SECTCRE
        self.__optre = RawConfigParser.OPTCRE
        if name:
            self.name = name
        else:
            self.name = ':memory:'

    def sanitize(self):
        list = []
        foundSection = False
        for line in self.__contents:
            if self.__sectre.match(line):
                foundSection = True
                list.append(line)
            if foundSection and self.__optre.match(line):
                list.append(line)
        self.__contents = list

    def readline(self):
        if len(self.__contents) > self.__pos:
            result = self.__contents[self.__pos]
            self.__pos += 1
            return result
        else:
            return None

    def seek(self, i):
        if type(i) == type(1) and i < len(self.__contents) and i >= 0:
            self.__pos = i

class UserData(ConfigParser):
    def __init__(self, id):
        ConfigParser.__init__(self)
        try:
            userData = id.getUserData()
        except EC2DataRetrievalError:
            userData = ''
        self.fd = INIFileStub(userData, name='EC2UserData')
        self.fd.sanitize()
        self.readfp(self.fd)

    # Returns a section as a dict.
    def getSection(self, name, lower=True):
        if lower:
            for section in self.sections():
                if name.lower() == section.lower():
                    return self._sections[name]
        elif name in self._sections:
            return self._sections[name]

        return {}
