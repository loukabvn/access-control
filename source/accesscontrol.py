#!/usr/bin/python3

from urllib.parse import urlparse
from json import dump, load, dumps
from csv import DictReader
from time import sleep

import logging
import source.usersession as us

class AccessControl():
    """
    This class implements the main access control test. It loads users and URLs from given files, login
    and execute a GET request to each URL with each given account. Then results are saved or printed to
    standard output.
    """

    # Constants
    UNAUTHENTICATED = "Unauth. user"
    # Default proxy
    DEFAULT_PROXY = {
        "http":  "127.0.0.1:8080",
        "https": "127.0.0.1:8080"
    }
    # Users CSV fields name
    desc_field = "role"
    user_field = "username"
    pwd_field  = "password"
    
    def __init__(self, args_dict: dict):
        self.__dict__.update(args_dict)
        self.proxy = self.DEFAULT_PROXY if self.proxy else None
        # Logger paramters
        log_level = loggin.DEBUG if self.debug else (logging.INFO if self.verbose else logging.WARNING)
        logging.basicConfig(level=log_level)
        self.log = logging.getLogger("AccessControl")

    def loadURLs(self) -> list:
        """Load all URLs from file and keeps only the path part of them."""
        urls_file = self.urls
        with open(urls_file, 'r') as urlf:
            # read url list, split by line and remove last element (empty)
            content = urlf.read().split('\n')[:-1]
        urls = list()
        for url in content:
            p = urlparse(url)
            urls.append(p.path + ('?' + p.query if p.query != '' else ''))
        return urls

    def loadUsers(self) -> list:
        """
        Load all users from the given CSV file.
        The format must fit the described format in the documentation
        """
        users_file = self.users
        users = list()
        with open(users_file, 'r') as userf:
            user_reader = DictReader(userf, delimiter=';')
            # load users (list of dictionnaries)
            for user in user_reader:
                users.append(user)
        return users

    def save(self, result: dict):
        """Save result dict to the given output file or print it to stdout, as JSON or table format"""
        output = sys.stdout
        # open output file
        if self.out is not None:
            try:
                output = open(self.out, 'w')
            except:
                log.warn("Can't open given output file, write to stdout")
        # Save in JSON format
        if self.json:
            dump(result, output, indent=4)
            if output == sys.stdout:
                print()
        # Save in human-readable format
        else:
            self.writeTable(result, output)
        # Close output file if opened
        if self.out is not None:
            output.close()

    def writeTable(self, data: dict, out):
        """Write the result dict as a table to the output"""
        # determine padding
        max_pad = max([len(path) for path in data.keys()])
        users = list(data.values())[0].keys()
        column_length = max([len(u) for u in users]) + 1
        # print users
        fmt_str = ("{:<%d} " % max_pad) + ("{:<%d}" % column_length) * len(users) + '\n'
        out.write(fmt_str.format("URLs", *users))
        out.write('-' * (max_pad + 1 + column_length * len(users)) + '\n')
        # print table
        for path, codes in zip(data.keys(), data.values()):
            fmt_str = ("{:<%d} " % max_pad) + ("{:<%d}" % column_length) * len(codes) + '\n'
            out.write(fmtStr.format(path, *codes.values()))
 
    # Test all access controls with a GET request to each urls for each user
    def execRequests(self, users: list, urls: list) -> dict:
        """
        Main function of the class. It will login with each user credentials and then
        send a request to all URLs to get all the status codes. The data are returns
        in a dictionnary containing all informations. If a wait duration was given, it
        will wait between each account and after login to limit the request rate.
        """
        # init result
        result = dict()
        for url in urls:
            result[url] = dict()
        # Add unauthenticated user if needed
        if not self.disable_unauth:
            users = [{
                self.desc_field: self.UNAUTHENTICATED,
                self.user_field: None,
                self.pwd_field: None
            }] + users
        # Send all requests for each users
        for user in users:
            self.log.info("Testing %d URLs for user: %s, role: %s" % (len(urls), user[self.user_field], user[self.desc_field]))
            session = us.UserSession(self.host,
                self.login_path, self.id_field, self.pwd_field,
                self.login_code, (self.login_text is not None), self.login_text,
                self.csrf, self.csrf_name, self.csrf_class,
                self.disable_https, self.allow_redirect, self.timeout, self.proxy
            )
            # Try to login
            if user[self.desc_field] is not self.UNAUTHENTICATED:
                session.login(user[self.user_field], user[self.pwd_field])
                # Test if connection suceed
                if not session.isConnected:
                    log.warn("Skipping user %s: can't log in" % user[self.user_field])
                    continue
            # Add sleep time to reduce request rate
            sleep(self.wait)
            for url in urls:
                try:
                    r = session.get(url)
                    count = 0
                    while r.status_code == 502 and count < self.max_retries:
                        self.log.debug(f"Got 502 when trying to access {url}, retrying")
                        r = session.get(url)
                        count += 1
                        sleep(self.wait)
                    result[url][user[self.desc_field]] = r.status_code
                # request timeout
                except requests.exceptions.Timeout:
                    self.log.debug(f"Request to {url} timeout")
                    result[url][user[self.desc_field]] = "Timeout"
            sleep(self.wait * 3)
        return result

       
    def run(self):
        """
        Run the main test by loading users and URLs, setting up options, sending requests
        and finally save or print the result.
        """
        # Host informations
        self.log.info(f"Host: {self.host}")
        # Proxy informations
        if self.proxy is not None:
            self.log.info("HTTP proxy is  : %s" % self.proxy['http'])
            self.log.info("HTTPS proxy is : %s" % self.proxy['https'])
        try:
            # Load users
            self.log.info(f"Load users file: {self.users}")
            users = self.loadUsers()
            # Load URLs
            self.log.info(f"Load target URLs file: {self.urls}")
            log.warn("WARNING: ensure /logout or equivalent is not in URLs or at the end of the list")
            urls  = self.loadURLs()
        except:
            self.log.error("Can't load or open users or URLs file")
            exit(1)
        # Limits the numbers of users and URLs to test if asked (debug)
        if self.limit_users is not None:
            users = users[:self.limit_users]
        if self.limit_urls is not None:
            urls = urls[:self.limit_urls]
        # Start test
        result = self.execRequests(users, urls)
        self.save(result)
        # Finished
        self.log.info("Done")

