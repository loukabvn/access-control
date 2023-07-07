#!/usr/bin/python3

import usersession
from requests.auth import HTTPProxyAuth


class ProxyAuthLogin(usersession.AbstractUserSession):
    """
    Define a login helper for Apache Proxy authentication method.
    """

    DEFAULT_VALID_STATUS_CODE = 200

    def __init__(self, host, any_restricted_path, https=True, **kwargs):
        """
        An instance of ProxyAuthLogin is the same as AbstractUserSession except that
        the login_path can be any path of the application with HTTP Proxy restricted access.
        """
        super().__init__(host, any_restricted_path, https, **kwargs)
    
    def send_login_request(self, user, pwd, **kwargs):
        """
        Send a get request to any restricted path in the application with Proxy authentication
        """
        self.user, self.pwd = (user, pwd)
        return self.get(self.login_path, auth=HTTPProxyAuth(self.user, self.pwd), *kwargs)

    def parse_login_response(self, response):
        """
        Check if Proxy authentication succeed. Upon a valid login, set the authentication method
        of the session with the auth parameter.
        """
        if response.status_code == self.DEFAULT_VALID_STATUS_CODE:
            self.session.auth = HTTPProxyAuth(self.user, self.pwd)
            self.is_logged = True
        else:
            self.user, self.pwd = (None, None)
