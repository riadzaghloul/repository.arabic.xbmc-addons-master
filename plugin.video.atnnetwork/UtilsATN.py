import cookielib
import hashlib
import json
import sys
import urllib2

class UtilsATN:

    # ATN Feeds
    urls = {}
    urls['login_querystring'] = "email={email}&password={password}"
    urls['get_packages'] = "http://api.arabtvnet.tv/get_packages?{loginTicket}"
    urls['get_channel'] = "http://api.arabtvnet.tv/channel?{loginTicket}&package={packageNo}&channel={channelID}"
    urls['get_channels'] = "http://api.arabtvnet.tv/channels?package={packageNo}"

    def __init__(self):
        self.settings = sys.modules["__main__"].settings
        self.language = sys.modules["__main__"].language
        self.plugin = sys.modules["__main__"].plugin

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

    def loginTicket(self):
        username = self.settings.getSetting('username')
        password = self.settings.getSetting('password')
        md5Password = hashlib.md5(password).hexdigest()

        return self.urls['login_querystring'].format(email=username, password=md5Password)

    def hasValidLogin(self):
        return self.settings.getSetting('validLogin') == "True"

    def getData(self, url):
        response = self.opener.open(url)
        data = response.read()
        self.opener.close()

        return json.loads(data)

    def getATNSubscriptionPackages(self):
        url = self.urls['get_packages'].format(loginTicket=self.loginTicket())
        return self.getData(url)

    def login(self):
        atnPackageData = self.getATNSubscriptionPackages()

        success = False

        # User has 1 or more ATN package subscriptions
        if len(atnPackageData) > 0:
            success = atnPackageData[0]['Expiry'] is not None

        # Mark that the user has a successful login credential
        self.settings.setSetting('validLogin', str(success))

        return success

    def getAllChannels(self, packageNo):
        url = self.urls['get_channels'].format(packageNo=packageNo)
        return self.getData(url)

    def getChannelStreamUrl(self, channelID, packageNo):
        # Call get_channel service to fetch http cdn URL
        url = self.urls['get_channel'].format(loginTicket=self.loginTicket(), packageNo=packageNo, channelID=channelID)
        channelData = self.getData(url)

        return channelData["Message"]
