import click
from analytics import Analytics
import pkg_resources
import json


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def setup(project_id, client_id, client_secret):
	""" Set up your Google API oauth2 credentials"""
	data = {
			'installed':
			{
			'client_id':client_id,
			'project_id':project_id,
			'auth_uri':'https://accounts.google.com/o/oauth2/auth',
			'token_uri':'https://accounts.google.com/o/oauth2/token',
			'auth_provider_x509_cert_url':'https://www.googleapis.com/oauth2/v1/certs',
			'client_secret':client_secret,
			'redirect_uris':['urn:ietf:wg:oauth:2.0:oob','http://localhost']
			}
		}
	
	with open(pkg_resources.resource_filename('gamgmt', "client_secrets.json"), 'w') as file:
		json.dump(data, file)
	print "Credentials have been set up!"

@click.group(context_settings=CONTEXT_SETTINGS)
def gamgmt():
	try:
		gamgmt.ga = Analytics()
	except Exception:
		if click.confirm("Do you want to set up your credentials?"):
			project_id = click.prompt("What is your project id?")	
			client_id = click.prompt("What is your client id?")
			client_secret = click.prompt("What is your client secret?")	
			setup(project_id, client_id, client_secret)
			raise click.Abort()
	pass

""" Commands for Accounts """
@gamgmt.group()
def account():
	pass
	
@account.command()
def list():
	"""List all the owned accounts"""
	gamgmt.ga.list_accounts()
	
""" Commands for Properties """
@gamgmt.group()
def property():
	pass
	
@property.command()
@click.option("--account", "-ac", default="~all", help="account id")
def list(account):
	"""List all the owned properties in total, or for specified account"""
	gamgmt.ga.list_properties(account)
	
""" Commands for Profiles """
@gamgmt.group()
def profile():
	pass
	
@profile.command()
@click.option("--account", "-ac", default="~all", help="account id")
@click.option("--property", "-wp", default="~all", help="web property id")
def list(account, property):
	"""List all the owned properties in total, for specified property or for specified account"""
	gamgmt.ga.list_profiles(account, property)

""" Commands for Users """	
@gamgmt.group()
def user():
	pass
	
@user.command()
@click.argument("account")
@click.option("--property", "-wp", default="~all", help="web property id")
@click.option("--profile", "-vp", default="~all", help="view profile id")
def list(account, property, profile):
	"""List all the users for an account, property or profile"""
	gamgmt.ga.list_users(account, property, profile)
	
@user.command()
@click.argument("account")
@click.argument("email")
#@click.option("--property", "-wp", default="~all", help="web property id")
#@click.option("--profile", "-vp", default="~all", help="view profile id")
@click.argument("perms", nargs=-1, type=click.Choice(["COLLABORATE", "EDIT", "READ_AND_ANALYZE", "MANAGE_USERS"]))
def add(account, email, perms):
	"""Add a user to a specific account"""
	gamgmt.ga.add_user(account, email, perms)
	
@user.command()
@click.argument("account")
@click.argument("email")
#@click.option("--property", "-wp", default="~all", help="web property id")
#@click.option("--profile", "-vp", default="~all", help="view profile id")
def delete(account, email):
	"""Delete a user from a specific profile"""
	gamgmt.ga.delete_user(account, email)