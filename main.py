#!/usr/bin/python3

import sys
import argparse
import logging

from json import load, dumps
from source.accesscontrol import AccessControl

def main():
    # Parsing command line
    parser = argparse.ArgumentParser(
        prog='accesscontrol',
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
    options.add_argument("-t", "--timeout", type=int, help="timeout for each HTTP request", default=5)
    options.add_argument("-m", "--max-retries", type=int, help="max retries attempts if request failed", default=3)
    options.add_argument("-p", "--proxy",    action="store_true", help="enable use of proxy, for the moment: 127.0.0.1:8080")
    options.add_argument("-v", "--verbose",  action="store_true", help="see info and warning messages")
    options.add_argument("-d", "--debug",    action="store_true", help="see debug messages")
    options.add_argument("-j", "--json",     action="store_true", help="save results in JSON format")
    options.add_argument("--allow-redirect", action="store_true", help="follow requests redirection")
    options.add_argument("--disable-unauth", action="store_true", help="disable unauthenticated tests")
    options.add_argument("--disable-https",  action="store_true", help="disable HTTPS")
    # If no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    # Parse arguments
    args = parser.parse_args()
    argsDict = vars(args)
    # Set verbosity level
    # context.log_level = "debug" if argsDict["debug"] else ("info" if argsDict["verbose"] else "warning")
    log_level = logging.DEBUG if argsDict["debug"] else (logging.INFO if argsDict["verbose"] else logging.WARNING)
    logging.basicConfig(level=log_level)
    log = logging.getLogger("Launcher")
    # Check args
    if args.config is not None:
        try:
            configArgs = load(open(args.config))
            argsDict.update(configArgs)
        except:
            log.error("Configuration file loading failed")
    # Show args dict if debugging is enable
    log.debug(f"Arguments: {dumps(argsDict)}")
    # Check required arguments
    if args.config or (args.host and args.users and args.urls):
        # Init and run the test
        AccessControl(argsDict).run()
    else:
        log.error("Arguments host, users, and urls are required if no configuration file are provided")
        sys.exit(1)


if __name__ == "__main__":
    main()
