# access-control

Tool for testing potentials broken access control vulnerabilities in web apps, useful during pentests.

Connection to the app is fully parametrable, arguments can be passed in command line or in a configuration file (see: [template-config.json](./examples/template-config.json)).

You can use a proxy if needed to see all the requests sent by the tool and inspect precisely the response. By default it's `127.0.0.1:8080` (BurpSuite default proxy).

## Usage

Example :
```
$ python3 main.py "target.site.com" users.csv urls.txt --login-path "/login.php" --login-code 302 -v --json
[*] Host: target.site.com
[*] Load users file: users.csv
[*] Load target URLs file: urls.txt
[!] WARNING: ensure /logout or equivalent is not in URLs or at the end of the list
[*] Testing 4 URLs for user: admin@target.site.com
[*] Testing 4 URLs for user: john.doe@gmail.com
{
  "/": {
    "Unauth. user": 200,
    "Administrator": 200,
    "User": 200
  },
  "/login.php": {
    "Unauth. user": 200,
    "Administrator": 200,
    "User": 200
  },
  "/.htaccess": {
    "Unauth. user": 404,
    "Administrator": 404,
    "User": 404
  },
  "/backend": {
    "Unauth. user": 404,
    "Administrator": 200,
    "User": 403
  }
}
[*] Done
```

## Options

Available options:
```
usage:  accesscontrol [-h] [-c CONFIG] [--login-path LOGIN_PATH] [--id-field ID_FIELD] [--pwd-field PWD_FIELD]
                      [--login-code LOGIN_CODE | --login-text LOGIN_TEXT] [--csrf] [--csrf-class CSRF_CLASS] [--csrf-name CSRF_NAME]
                      [-o OUT] [-w WAIT] [--limit-users LIMIT_USERS] [--limit-urls LIMIT_URLS] [-t TIMEOUT] [-m MAX_RETRIES] [-p] [-v] [-d] [-j]
                      [--allow-redirect] [--disable-unauth] [--disable-https]
                      [host] [users] [urls]
```

For more informations, see the `man` page:
```
man docs/accesscontrol.1
```

You can add it to your man pages with:
```
gzip docs/accesscontrol.1
sudo mv docs/accesscontrol.1.gz /usr/share/man/man1/
```
