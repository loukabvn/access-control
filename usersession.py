#!/usr/bin/python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

# General user session class
class UserSession:

    HTTP  = "http://"
    HTTPS = "https://"
    
    def __init__(
            self, host, loginPath="/login", idField='email', pwdField='password',
            validLoginStatusCode=200, validLoginByText=False, validLoginText=None,
            csrfToken=False, csrfTokenName="csrf", csrfTokenClass="input",
            disableHTTPS=False, proxy=None
        ):
        # Host parameters
        self.protocol = self.HTTP if disableHTTPS else self.HTTPS
        self.host = host
        # Login parameters
        self.loginPath = loginPath
        self.idField = idField
        self.pwdField = pwdField
        self.validLoginStatusCode = validLoginStatusCode
        self.validLoginByText = validLoginByText
        self.validLoginText = validLoginText
        self.csrfToken = csrfToken
        if csrfToken:
            self.csrfTokenName = csrfTokenName
            self.csrfTokenClass = csrfTokenClass
        # Session informations
        self.session = requests.Session()
        self.isConnected = False
        # Proxy paramters
        self.proxy = proxy
        if self.proxy is not None:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get(self, path):
        url = self.protocol + self.host + path
        if self.proxy is not None:
            r = self.session.get(url, proxies=self.proxy, verify=False)
        else:
            r = self.session.get(url)
        return r

    def post(self, path, payload):
        url = self.protocol + self.host + path
        if self.proxy is not None:
            r = self.session.post(url, data=payload, proxies=self.proxy, verify=False)
        else:
            r = self.session.post(url, data=payload)
        return r
    
    def getCSRFToken(self):
        resp = self.get(self.loginPath)
        soup = BeautifulSoup(resp.text, 'html.parser')
        token = soup.find(self.csrfTokenClass, {'name': self.csrfTokenName})['value']
        return token

    def login(self, idValue, pwdValue, postAddArgs: dict=None):
        # Modify this payload to fit the app requirements
        payload = {
            self.idField : idValue,
            self.pwdField: pwdValue
        }
        # Get CSRF token
        if self.csrfToken:
            # Modify name of the input to find the CSRF token
            token = self.getCSRFToken()
            payload[self.csrfTokenName] = token
        # Add additionnal payloads arguments
        if postAddArgs is not None:
            for k, v in postAddArgs.keys(), postAddArgs.values():
                payload[k] = v
        # Send post requests in session
        resp = self.post(self.loginPath, payload)
        # Login success
        if (self.validLoginByText and self.validLoginText in resp.text) or (not self.validLoginByText and resp.status_code == self.validLoginStatusCode):
            self.username = idValue
            self.isConnected = True
        else:
            self.isConnected = False
            # Reset session
            self.session.close()
            self.session = requests.Session()

