#!/usr/bin/python3

import usersession
from bs4 import BeautifulSoup

class CSRFLogin(usersession.AbstractUserSession):
    """
    Send username and password in a POST request in application/x-www-form-urlencoded or
    application/json form (by default application/x-www-form-urlencoded, it can be change by
    setting json_body parameter to True at initialization) with given username and password
    fields. It also send a GET request before to get the CSRF token of the login page to send
    it with the credentials.
    Detect a valid login upon a given status code in response. Authentication token
    is stored in cookies, so there is no need to define a custom auth class.
    """

    def __init__(self, host, login_path,
            user_field, pwd_field, valid_status_code,
            csrf_token_name, csrf_token_class='input',
            **kwargs
        ):
        super().__init__(host, login_path, **kwargs)
        self.user_field = user_field
        self.pwd_field  = pwd_field
        self.valid_status_code = valid_status_code
        self.csrf_token_class = csrf_token_class
        self.csrf_token_name = csrf_token_name

    class TokenNotFound(Exception):
        pass
    
    def _get_csrf_token(self):
        """Get the CSRF token from the login page with a GET request"""
        resp = self.get(self.login_path)
        parser = BeautifulSoup(resp.text, 'html.parser')
        token = soup.find(self.csrf_token_class, {'name': self.csrf_token_name})['value']
        return token
    
    def send_login_request(self, user, pwd, **kwargs):
        """
        Try to get the CSRF and then send the login request. If the token can't be found
        raise an error.
        """
        csrf_token = self._get_csrf_token()
        if token is None:
            raise self.TokenNotFound("CSRF token not found")
        payload = {
            self.user_field : user,
            self.pwd_field  : pwd,
            self.csrf_token_name : csrf_token
        }
        return self.post(self.login_path, payload, **kwargs)

    def parse_login_response(self, response):
        if resp.status_code == self.valid_status_code:
            self.is_logged = True
