#!/usr/bin/python3

import usersession


class TemplateLogin(usersession.AbstractUserSession):
    """
    Template login class. It contains all methods that can be implemented to create a new
    login method.
    """

    def __init__(self, host, login_path, args, https=True, **kwargs):
        super().__init__(host, login_path, https, **kwargs)
        # Example code
        self.args = args

    def send_login_request(self, user, pwd, **kwargs):
        # Example code
        payload = {"user": user, "password": pwd}
        return self.post(self.login_path, payload, **kwargs)

    def parse_login_response(self, response):
        # Example code
        if "Bienvenue" in response.text:
            self.is_logged = True
        # Necessary only if a CustomAuth class is defined
        self.session.auth = self.CustomAuth(self.args)

    """
    The following class implementation isn't necessary if authentication method is based on cookies.
    """
 
    class CustomAuth(usersession.AuthBase):
        """
        Specific class implementation: the following class needs to be implemented if the
        authentication method doesn't rely on data stored with requests.sessions (e.g. cookies).
        For example if the application use Basic or a JWT authentication the __call__ function
        of a custom auth class must add the required headers.
        For more informations see: https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication
        """
        def __init__(self, arg):
            """Parameters needed for authentication needs to be stored here"""
            self.arg = arg
        
        def __call__(self, r):
            """Headers or others informations needs to be added here"""
            r.headers['Example'] = self.arg
            return r

