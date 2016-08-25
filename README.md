Want to work for Gamer Network? [We are hiring!](http://www.gamesindustry.biz/jobs/gamer-network)

Google Analytics Manager
========================

A simple command line tool for managing google analytics account users.

Uses Google Analytics API v3.

Install
-------

Clone into a directory. 
On same level install package

```shell
virtualenv env
source env/bin/activate
pip install --editable gamgmt
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
  

Setup 
-----
 - Run an initial command:
```gamgmt account list```

 - This will run the setup function. 
 - Follow the instructions to insert your client secret, client id and project id. 

Usage
-----

Examples:

- list all your accounts
```gamgmt account list```

- list all your properties
```gamgmt property list```

-  list all your profiles
```gamgmt profile list ```

- list all the users for specified account number 1234
```gamgmt user list 1234```

- add user test@test.com to account 1234 with permissions read, edit and collaborae
```gamgmt user add 1234 test@test.com READ_AND_ANALYZE EDIT COLLABORATE```

- delete user test@test.com to account 1234
```gamgmt user delete 1234 test@test.com```
