% BROKEN-ACCESS-CONTROL(1) broken-access-control 1.0
% Louka
% 09 Jun 2023

# NAME
broken-access-control - script to test access control during a pentest

# SYNOPSIS
broken-access-control [-h] [-c CONFIG] [--login-path LOGIN_PATH] [--id-field ID_FIELD]
                      [--pwd-field PWD_FIELD] [--login-code LOGIN_CODE | --login-text LOGIN_TEXT] [--csrf]
                      [--csrf-class CSRF_CLASS] [--csrf-name CSRF_NAME] [-o OUT] [-w WAIT]
                      [--limit-users LIMIT_USERS] [--limit-urls LIMIT_URLS] [-m MAX_RETRIES] [-p] [-v] [-j]
                      [--disable-unauth] [--disable-https]
                      [host] [users] [urls]

# DESCRIPTION
With a given list of users and URLs and a host server, test all accesses and store result as a table or in JSON format. Arguments can be specified from the command line or from a configuration file (see: CONFIGURATION FILE).\

The script will first send a GET request to all the URLs in the given file without any authentication (unless **disable-unauth** is set). Then it will try to login to the application with the given parameters (**login-path**, **id-field**, **pwd-field**, **login-code**, **login-text**). To authenticate the script send a POST request to the page given in **login-path**. The payload is created with the **id-field** and **pwd-field** parameters and with the values parsed from the CSV file containing the users credentials (**users** parameters).\
It's possible to use a CSRF mechanism to connect as a classic user do. You must enable CSRF using with **csrf** parameter and then, you can give the type of HTML tag which contains the CSRF token with **csrf-class** and their name with **csrf-name**.\

**Example:**
With default parameters (see: OPTIONS), the following request will be send for logging in:
```
POST /login HTTP/1.1
[... Headers ...]

email=user1&password=password1
```

# OPTIONS
Options:
  -h, --help            show help message and exit

Load arguments from configuration file:
  -c CONFIG, --config CONFIG
                        configuration file to load arguments from, JSON format, override command line arguments
                        (default: None)

Required arguments without configuration file:
  host                  specify the target host (default: None)
  users                 file containing the list of users (default: None)
  urls                  file containing the list of URLs (default: None)

Login helper arguments:
  --login-path LOGIN_PATH
                        path to the login page of the application (default: /login)
  --id-field ID_FIELD   name of the id field in the request for login (default: email)
  --pwd-field PWD_FIELD
                        name of the password field in the request for login (default: password)
  --login-code LOGIN_CODE
                        status code upon a valid login request (default: 200)
  --login-text LOGIN_TEXT
                        text in the page upon a valid upon login request (default: None)
  --csrf                name of the field in the POST request for login (default: False)
  --csrf-class CSRF_CLASS
                        class of the CSRF token element in the login page (default: input)
  --csrf-name CSRF_NAME
                        name of the CSRF token element in the login page (default: csrf)

Optional arguments:
  -o OUT, --out OUT     store the output in this file (default: None)
  -w WAIT, --wait WAIT  waiting time to limit requests rate, in seconds (default: 1)
  --limit-users LIMIT_USERS
                        set the limit of users to test (default: None)
  --limit-urls LIMIT_URLS
                        set the limit of URLs to test (default: None)
  -m MAX_RETRIES, --max-retries MAX_RETRIES
                        max retries attempts if request failed (default: 3)
  -p, --proxy           enable use of proxy, for the moment: 127.0.0.1:8080 (default: False)
  -v, --verbose         see debug messages (default: False)
  -j, --json            save results in JSON format (default: False)
  --disable-unauth      disable unauthenticated tests (default: False)
  --disable-https       disable HTTPS (default: False)

# USERS FILE
The file containing the users credentials must fit the following format:\

role;username;password
user;johndoe;Password#123
administrator;admin;P@ssw0rd456

# CONFIGURATION FILE
Parameters can be load from a configuration file. Here is an example of this file :
```
{
  "host": "example.domain.fr",
  "users": "user.csv",
  "urls": "url.txt",
  "login_path": "/login",
  "id_field": "email",
  "pwd_field": "password",
  "login_code": 200,
  "login_text": null,
  "csrf": false,
  "csrf_class": "input",
  "csrf_name": "csrf",
  "out": null,
  "wait": 1,
  "limit_users": null,
  "limit_urls": null,
  "max_retries": 3,
  "proxy": false,
  "verbose": false,
  "json": false,
  "disable_unauth": false,
  "disable_https": false
}
```

# TO DO
- Add possibility of test control access with POST requests with parameters
- Possibility of adding headers to the requests
