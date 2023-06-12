# access-control
Tool for testing access control in web apps, useful during pentests.

## Usage

Example :
```
$ broken-access-control.py "target.site.com" users.csv urls.txt --login-path "/login.php" --login-code 302 -v --json
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

For more informations, see :
```
man ./broken-access-control.1
```

You can add it to your man pages with:
```
gzip broken-access-control.1
sudo mv ./broken-access-control.1.gz /usr/share/man/man1/
```
