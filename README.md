Want to work for Gamer Network? [We are hiring!](http://www.gamesindustry.biz/jobs/gamer-network)

Google Analytics Manager
========================

A simple command line tool for managing google analytics account users.

Uses Google Analytics API v3.

Install
-------

Pop it in a virtualenv for safety.

```shell
virtualenv env
env/bin/pip install -r requirements.txt
```

Generating OAuth Client ID
--------------------------

  - Register for Google Developers Console: https://console.developers.google.com/
  - Create a project
  - Go to APIs & Auth
  - Enable Google Analytics API v3.
  - Go to Credentials -> Create Credentials
    - Choose "OAuth Client ID"
    - Choose "Other"
  - Save the client ID and client Secret numbers
  - The Client ID will appear under the Credentials tab, on the right click to "download JSON"
  - Copy this file into your folder and fill in the path for the ```get_service()``` function
  
  
Usage
-----

Examples:
```python gamgmt.py accounts list``` 
- list all your accounts

```python gamgmt.py properties list```
- list all your properties

```python gamgmt.py profiles list ```
- list all your profiles

```python gamgmt.py user list 1234```
- list all the users for specified account number 1234

```python gamgmt.py user add 1234 test@test.com -perms READ_AND_ANALYZE EDIT COLLABORATE```
- add user test@test.com to account 1234 with permissions read, edit and collaborate

```python gamgmt.py user delete 1234 test@test.com```
- delete user test@test.com to account 1234
