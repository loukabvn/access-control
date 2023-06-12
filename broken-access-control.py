#!/usr/bin/python3

from urllib.parse import urlparse
from pwn import log
from json import dump, load, dumps
from csv import DictReader
from time import sleep

import sys
import argparse
import usersession as us


class BrokenAccessControl():
    # Constants
    UNAUTHENTICATED = "Unauth. user"
    # Users CSV fields name
    descField = "description"
    userField = "username"
    pwdField  = "password"

    # Constructor
    def __init__(self, argsDict):
        self.__dict__.update(argsDict)
        DEFAULT_PROXY = {
            "http":  "127.0.0.1:8080",
            "https": "127.0.0.1:8080"
        }
        self.proxy = DEFAULT_PROXY if self.proxy else None

    # Log functions
    def info(self, msg):
        if self.verbose: log.info(msg)

    def warn(self, msg):
        if self.verbose: log.warn(msg)

    def error(self, msg):
        if self.verbose: log.error(msg)

    # open and extract content of URLs file
    def loadURLs(self):
        urlsFile = self.urls
        with open(urlsFile, 'r') as urlf:
            # read url list, split by line and remove last element (empty)
            content = urlf.read().split('\n')[:-1]
        urls = list()
        for url in content:
            p = urlparse(url)
            urls.append(p.path + ('?' + p.query if p.query != '' else ''))
        return urls

    # open and extract content of CSV users file
    def loadUsers(self):
        usersFile = self.users
        users = list()
        with open(usersFile, 'r') as userf:
            userReader = DictReader(userf, delimiter=';')
            # load users (list of dictionnaries)
            for user in userReader:
                users.append(user)
        return users

    # Test all access controls with a GET request to each urls for each user
    def testAll(self, users, urls):
        # init result
        result = dict()
        for url in urls:
            result[url] = dict()
        # Unauthenticated tests
        if not self.disable_unauth:
            session = us.UserSession(self.host, disableHTTPS=self.disable_https, proxy=self.proxy)
            for url in urls:
                r = session.get(url)
                result[url][self.UNAUTHENTICATED] = r.status_code
            sleep(self.wait * 3)
        # Authenticated tests
        for user in users:
            self.info("Testing %d URLs for user: %s" % (len(urls), user[self.userField]))
            session = us.UserSession(self.host,
                self.login_path, self.id_field, self.pwd_field,
                self.login_code, (self.login_text is not None), self.login_text,
                self.csrf, self.csrf_name, self.csrf_class,
                self.disable_https, proxy=self.proxy)
            try:
                session.login(user[self.userField], user[self.pwdField])
            except:
                pass
            # Test if connection suceed
            if not session.isConnected:
                self.warn("Skipping user %s: can't log in" % user[self.userField])
                continue
            # Add sleep time to reduce request rate
            sleep(self.wait)
            if session.isConnected:
                for url in urls:
                    r = session.get(url)
                    count = 0
                    while r.status_code == 502 and count < self.max_retries:
                        r = session.get(url)
                        count += 1
                        sleep(self.wait)
                    result[url][user[self.descField]] = r.status_code
            sleep(self.wait * 3)
        return result

    # Save result as text or in JSON format
    def save(self, result):
        output = sys.stdout
        # open output file
        if self.out is not None:
            try:
                output = open(self.out, 'w')
            except:
                warn("Can't open given output file, write to stdout")
        # Save in JSON format
        if self.json:
            dump(result, output)
        # Save in human-readable format
        else:
            self.writeTable(result, output)
        # Close output file if opened
        if self.out is not None:
            output.close()

    # Write data as a formatted table in out
    def writeTable(self, data, out):
        # determine padding
        maxPad = max([len(path) for path in data.keys()])
        users = list(data.values())[0].keys()
        columnLength = max([len(u) for u in users]) + 1
        # print users
        fmtStr = ("{:<%d} " % maxPad) + ("{:<%d}" % columnLength) * len(users) + '\n'
        out.write(fmtStr.format("URLs", *users))
        out.write('-' * (maxPad + 1 + columnLength * len(users)) + '\n')
        # print table
        for path, codes in zip(data.keys(), data.values()):
            fmtStr = ("{:<%d} " % maxPad) + ("{:<%d}" % columnLength) * len(codes) + '\n'
            out.write(fmtStr.format(path, *codes.values()))
        
    # Run the broken access control test
    def run(self):
        # Host informations
        self.info(f"Host: {self.host}")
        # Proxy informations
        if self.proxy is not None:
            self.info("HTTP proxy is  : %s" % self.proxy['http'])
            self.info("HTTPS proxy is : %s" % self.proxy['https'])
        try:
            # Load users
            self.info(f"Load users file: {self.users}")
            users = self.loadUsers()
            # Load URLs
            self.info(f"Load target URLs file: {self.urls}")
            self.warn("WARNING: ensure /logout or equivalent is not in URLs or at the end of the list")
            urls  = self.loadURLs()
        except:
            self.error("Can't load or open users or URLs file")
        # Limits the numbers of users and URLs to test if asked (debug)
        if self.limit_users is not None:
            users = users[:self.limit_users]
        if self.limit_urls is not None:
            urls = urls[:self.limit_urls]
        # Start test
        result = self.testAll(users, urls)
        if len(result) > 0:
            # Save results
            self.save(result)
        else:
            self.warn("Test failed, no data returned")
        # Finished
        self.info("Done")


# Entry point
if __name__ == "__main__":
    # Parsing command line
    parser = argparse.ArgumentParser(
        prog='broken-access-control',
        description="""
            With a given list of users and URLs and a host server, test all accesses and store result as a table or in JSON format.
            Arguments can be specified from the command line or from a configuration file (see: template-config.json)
            """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Load arguments from configuration file
    cfg = parser.add_argument_group('Load arguments from configuration file')
    cfg.add_argument('-c', '--config', type=str, help="configuration file to load arguments from, JSON format, override command line arguments")
    # Required arguments
    req = parser.add_argument_group('Required arguments without configuration file')
    req.add_argument("host",  type=str, help="specify the target host", nargs='?')
    req.add_argument("users", type=str, help="file containing the list of users", nargs='?')
    req.add_argument("urls",  type=str, help="file containing the list of URLs", nargs='?')
    # Login helper arguments
    login = parser.add_argument_group('Login helper arguments')
    login.add_argument("--login-path",  type=str, help="path to the login page of the application", default="/login")
    login.add_argument("--id-field",    type=str, help="name of the id field in the request for login", default="email")
    login.add_argument("--pwd-field",   type=str, help="name of the password field in the request for login", default="password")
    loginValidation = login.add_mutually_exclusive_group()
    loginValidation.add_argument("--login-code", type=int, help="status code upon a valid login request", default=200)
    loginValidation.add_argument("--login-text", type=str, help="text in the page upon a valid upon login request")
    login.add_argument("--csrf", action="store_true", help="name of the field in the POST request for login")
    login.add_argument("--csrf-class", type=str, help="class of the CSRF token element in the login page", default="input")
    login.add_argument("--csrf-name",  type=str, help="name of the CSRF token element in the login page", default="csrf")
    # Optional arguments
    options = parser.add_argument_group('Optional arguments')
    options.add_argument("-o", "--out",   type=str, help="store the output in this file")
    options.add_argument("-w", "--wait",  type=int, help="waiting time to limit requests rate, in seconds", default=1)
    options.add_argument("--limit-users", type=int, help="set the limit of users to test")
    options.add_argument("--limit-urls",  type=int, help="set the limit of URLs to test")
    options.add_argument("-m", "--max-retries", type=int, help="max retries attempts if request failed", default=3)
    options.add_argument("-p", "--proxy",    action="store_true", help="enable use of proxy, for the moment: 127.0.0.1:8080")
    options.add_argument("-v", "--verbose",  action="store_true", help="see debug messages")
    options.add_argument("-j", "--json",     action="store_true", help="save results in JSON format")
    options.add_argument("--disable-unauth", action="store_true", help="disable unauthenticated tests")
    options.add_argument("--disable-https",  action="store_true", help="disable HTTPS")
    # Parse and call main
    args = parser.parse_args()
    argsDict = vars(args)
    if args.config is not None:
        try:
            configArgs = load(open(args.config))
            argsDict.update(configArgs)
        except:
            log.error("Configuration file loading failed")
    print(dumps(argsDict))
    # BrokenAccessControl(argsDict).run()
