#!/usr/bin/python3

import usersession
from requests.auth import HTTPBasicAuth


class BasicAuthLogin(usersession.AbstractUserSession):
    """
    Define a login helper for Apache Basic authentication method.
    """

    DEFAULT_VALID_STATUS_CODE = 200

    def __init__(self, host, any_restricted_path, https=True, **kwargs):
        """
        An instance of BasicAuthLogin is the same as AbstractUserSession except that
        the login_path can be any path of the application with HTTP Basic restricted access.
        """
        super().__init__(host, any_restricted_path, https, **kwargs)
    
    def send_login_request(self, user, pwd, **kwargs):
        """
        Send a get request to any restricted path in the application with Basic authentication
        """
        self.user, self.pwd = (user, pwd)
        return self.get(self.login_path, auth=HTTPBasicAuth(self.user, self.pwd), *kwargs)

    def parse_login_response(self, response):
        """
        Check if Basic authentication succeed. Upon a valid login, set the authentication method
        of the session with the auth parameter.
        """
        if response.status_code == self.DEFAULT_VALID_STATUS_CODE:
            self.session.auth = HTTPBasicAuth(self.user, self.pwd)
            self.is_logged = True
        else:
            self.user, self.pwd = (None, None)
