#!/usr/bin/python3

import usersession
from requests.auth import HTTPDigestAuth


class DigestAuthLogin(usersession.AbstractUserSession):
    """
    Define a login helper for Apache Digest authentication method.
    """

    DEFAULT_VALID_STATUS_CODE = 200

    def __init__(self, host, any_restricted_path, https=True, **kwargs):
        """
        An instance of DigestAuthLogin is the same as AbstractUserSession except that
        the login_path can be any path of the application with HTTP Digest restricted access.
        """
        super().__init__(host, any_restricted_path, https, **kwargs)
    
    def send_login_request(self, user, pwd, **kwargs):
        """
        Send a get request to any restricted path in the application with Digest authentication
        """
        self.user, self.pwd = (user, pwd)
        return self.get(self.login_path, auth=HTTPDigestAuth(self.user, self.pwd), *kwargs)

    def parse_login_response(self, response):
        """
        Check if Digest authentication succeed. Upon a valid login, set the authentication method
        of the session with the auth parameter.
        """
        if response.status_code == self.DEFAULT_VALID_STATUS_CODE:
            self.session.auth = HTTPDigestAuth(self.user, self.pwd)
            self.is_logged = True
        else:
            self.user, self.pwd = (None, None)
