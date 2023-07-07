#!/usr/bin/python3

import usersession

class ClassicPostLogin(usersession.AbstractUserSession):
    """
    Send username and password in a POST request in application/x-www-form-urlencoded or
    application/json form (by default application/x-www-form-urlencoded, it can be change by
    setting json_body parameter to True at initialization) with given username and password
    fields. Detect a valid login upon a given status code in response. Authentication token
    is stored in cookies, so there is no need to define a custom auth class.
    """

    def __init__(self, host, login_path, user_field, pwd_field, valid_status_code, **kwargs):
        super().__init__(host, login_path, **kwargs)
        self.user_field = user_field
        self.pwd_field  = pwd_field
        self.valid_status_code = valid_status_code

    def send_login_request(self, user, pwd, **kwargs):
        payload = {
            self.user_field : user,
            self.pwd_field  : pwd
        }
        # Send post request in session
        return self.post(self.login_path, payload, **kwargs)

    def parse_login_response(self, response):
        if resp.status_code == self.valid_status_code:
            self.is_logged = True
