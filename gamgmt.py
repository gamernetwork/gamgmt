#!/usr/bin/python

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from apiclient.errors import HttpError

import pprint

from config import CREDENTIALS_JSON

def get_service(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

def default_fields(fields):
    def default_fields_dec(func):
        def func_wrapper(*args, **kwargs):
            if not kwargs.has_key('fields') or not kwargs['fields']:
                kwargs['fields'] = fields
            return func(*args, **kwargs)
        return func_wrapper
    return default_fields_dec

def build_format(fields):
    fmt = [ "%%(%s)s" % field for field in fields ]
    fmt = ", ".join(fmt)
    return fmt

@default_fields(('name', 'id'))
def list_accounts(service, fields=None):
    fmt = build_format(fields)
    accounts = service.management().accounts().list().execute()
    account_data = []
    for account in accounts.get('items'):
        data = {}
        data["name"] = account["name"]
        data["id"] = account["id"]
        data["permissions"] = account["permissions"]
        account_data.append(data)

    for a in account_data:
        print(fmt % a)
    return account_data

@default_fields(('name', 'id'))
def list_properties(service, account, fields=None):
    fmt = build_format(fields)
    properties = service.management().webproperties().list(accountId=account).execute()
    property_data = []
    for property in properties.get('items'):
        data = {}
        data["name"] = property["name"]
        data["id"] = property["id"]
        data["permissions"] = property["permissions"]
        data["account_id"] = property["accountId"]
        #data["website"] = property["websiteUrl"]
        property_data.append(data)

    for p in property_data:
        print(fmt % p)
    return property_data
    
@default_fields(('name', 'id'))
def list_profiles(service, account, property, fields=None):
    fmt = build_format(fields)
    profiles = service.management().profiles().list(accountId=account,webPropertyId=property).execute()
    profiles_data = []
    for profile in profiles.get('items'):
        data = {}
        data["name"] = profile["name"]
        data["id"] = profile["id"]
        data["permissions"] = profile["permissions"]
        data["account_id"] = profile["accountId"]
        data["property_id"] = profile["webPropertyId"]
        data["website"] = profile["websiteUrl"]
        profiles_data.append(data)
            
    for p in profiles_data:
        print(fmt % p)
    return profiles_data
    
def add_user(service, id, email, permissions):
    try:
        service.management().accountUserLinks().insert(
            accountId=id,
            body={
                'permissions': {
                    'local': permissions
                },
                'userRef': {
                    'email': email
                }
            }
        ).execute()

    except HttpError, error:
        # Handle API errors.
        print ('There was an API error : %s : %s' %
                (error.resp.status, error.resp.reason))
    except Exception, e:
        print "Error Type: " + str(type(e)) + "  " + str(e)
        raise
    except:
        raise
        
def delete_user(service, id, email):
    #to delete user must find their link ID
    users = list_users(service, id)
    print "\n email : ", email
    for user in users:
        print "\n", user["userRef"]["email"] 
        if user["userRef"]["email"] == email:
            #user[id] comes from profileUserLinks func so must take out profile id and swap for account id for accountUserLinks func
            main = user["id"]
            separate_id = main.split(":")[1]
            link_id = id + ":" + separate_id
            print "\n link id: ", link_id
            break
        else:
            link_id = None
            raise Exception("Could not find user")
    try:
        service.management().accountUserLinks().delete(
            accountId=id,
            linkId=link_id
        ).execute()

    except HttpError, error:
        # Handle API errors.
        print ('There was an API error : %s : %s' %
                (error.resp.status, error.resp.reason))
    except Exception, e:
        print "Error Type: " + str(type(e)) + "  " + str(e)
        raise
    except:
        raise
    
def list_users(service, account, property="~all", profile="~all", fields=None):
    account_links = service.management().profileUserLinks().list(
        accountId=account,
        webPropertyId=property,
        profileId=profile
    ).execute()
    pprint.pprint(account_links["items"])
    return account_links["items"]

"""
    Set up command line argument parser
"""
parser = argparse.ArgumentParser(description="User management tool for Google Analytics")
parser.add_argument("--fields", help="Override fields to output", type=str, default=None)
subparsers = parser.add_subparsers()

"""
    Set up for user subcommands
"""
parser_user = subparsers.add_parser("user", description="subcommands relavant to single users")
parser_user.set_defaults(object="user")

user_subparsers = parser_user.add_subparsers()

#sub parser to list users
user_parser_list = user_subparsers.add_parser("list", description="list all the users for an id")
user_parser_list.set_defaults(action="list")
user_parser_list.add_argument("account", help="id for the relevant account", type=str)
user_parser_list.add_argument("--property", help="id for the relevant property", type=str, default="~all")
user_parser_list.add_argument("--profile", help="id for the relevant profile", type=str, default="~all")

#sub parser to add new user
user_parser_add = user_subparsers.add_parser("add", description="add a user to an account")
user_parser_add.set_defaults(action="add")
user_parser_add.add_argument("account", help="id for the relevant account", type=str)
user_parser_add.add_argument("email", help="email of the user to add", type=str)
user_parser_add.add_argument("--property", "-wp", help="id for the relevant property", type=str, default="~all")
user_parser_add.add_argument("--profile", "-p", help="id for the relevant profile", type=str, default="~all")
user_parser_add.add_argument("--permissions", "-perms", help="permissions", type=str, nargs="*", choices=["COLLABORATE", "EDIT", "READ_AND_ANALYZE", "MANAGE_USERS"], default=["READ_AND_ANALYZE"])

#sub parser to delete user 
user_parser_del = user_subparsers.add_parser("delete", description="delete a user from an account")
user_parser_del.set_defaults(action="delete")
user_parser_del.add_argument("account", help="id for the relevant account", type=str)
user_parser_del.add_argument("email", help="email of the user to delete", type=str)

"""
    Set up for accounts subcommands
"""
parser_account = subparsers.add_parser("accounts", description="subcommands relevant to accounts")
parser_account.set_defaults(object="account")

account_subparsers = parser_account.add_subparsers()

#sub parser to list accounts
account_parser_list = account_subparsers.add_parser("list", description="list accounts")
account_parser_list.set_defaults(action="list")

"""
    Set up for property subcommands
"""
parser_property = subparsers.add_parser("properties", description="subcommands relevant to properties")
parser_property.set_defaults(object="property")

property_subparsers = parser_property.add_subparsers()

#sub parser to list properties
property_parser_list = property_subparsers.add_parser("list", description="list properties")
property_parser_list.set_defaults(action="list")
property_parser_list.add_argument("--account", "-a", help="id for account to get properties for", type=str, default="~all")

"""
    Set up for profiles subcommands
"""
parser_profile = subparsers.add_parser("profiles", description="subcommands relevant to profiles")
parser_profile.set_defaults(object="profile")

profile_subparsers = parser_profile.add_subparsers()

#sub parser to list profiles
profile_parser_list = profile_subparsers.add_parser("list", description="list profiles")
profile_parser_list.set_defaults(action="list")
profile_parser_list.add_argument("--account", "-a", help="id for account to get profiles for", type=str, default="~all")
profile_parser_list.add_argument("--property", "-wp", help="id for property to get profiles for", type=str, default="~all")

args = parser.parse_args()

scope = ['https://www.googleapis.com/auth/analytics.readonly', 'https://www.googleapis.com/auth/analytics.manage.users']
# Authenticate and construct service.
service = get_service('analytics', 'v3', scope, CREDENTIALS_JSON)

if args.object == "user":
    if args.action == "list":
        list_users(service, args.account, args.property, args.profile, fields=args.fields)
    elif args.action == "add":
        add_user(service, args.account, args.email, args.permissions)
    elif args.action == "delete":
        delete_user(service, args.account, args.email)
elif args.object == "account":
    if args.action == "list":
        list_accounts(service, fields=args.fields)
elif args.object == "property":
    if args.action == "list":
        list_properties(service, args.account, fields=args.fields)        
elif args.object == "profile":
    if args.action == "list":
        list_profiles(service, args.account, args.property, fields=args.fields)
        
