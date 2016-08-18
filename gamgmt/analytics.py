#!/usr/bin/python

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from apiclient.errors import HttpError
from tabulate import tabulate
import argparse
import pkg_resources
import json



class Analytics(object):
	"""
	Class to communicate with Google Analytica
	"""
	service = None
	
	def __init__(self):
	
		if self.check_credentials() == True:
			self.get_service()
		else:
			raise Exception("Please set up your credentials using `gamgmt setup` ")
			
	def get_service(self):	
		"""
		Set up service that connects to Google API
		"""
		# Parse command-line arguments.
		parser = argparse.ArgumentParser(
		  formatter_class=argparse.RawDescriptionHelpFormatter,
		  parents=[tools.argparser])
		flags = parser.parse_args([])
		
		#self.set_credentials('plenary-agility-139115','502244039410-outojamddrsniehf0hetgdksh2b9tj0h.apps.googleusercontent.com','hlu5Pb6AfI41gDxwApVrpUV2')

		scope = ['https://www.googleapis.com/auth/analytics.readonly', 'https://www.googleapis.com/auth/analytics.manage.users']
		api_name = "analytics"
		api_version = "v3"
		
		client_secrets_path  = pkg_resources.resource_filename('gamgmt', "client_secrets.json")

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
		self.service = build(api_name, api_version, http=http)


	def check_credentials(self):
		secrets = pkg_resources.resource_string('gamgmt', "client_secrets.json")
		if secrets:
			return True
		else:
			return False		
		

	def execute_query(self, query):
		"""
		Try to execute the api query
		"""
		try:
			results = query.execute()
			return results
		except HttpError, e:
			print "HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
		except Exception, e:
			print "Error Type: " + str(type(e)) + "  " + str(e)
			raise
		except:
			raise
    		
	def print_table(self, data):
		"""
		Prints table of data to console
		data: list of dictionaries, value of "items" from analytics response
		"""		
		for item in data:
			table = [] 
			item.pop("selfLink", None)
			for key, value in item.items():
				if type(value) == dict:
					for b_key, b_value in value.items():
						if type(b_value) == dict:
							for c_key, c_value in b_value.items():
								table.append([key, b_key, c_key, c_value])
						else:
							table.append([key, b_key, b_value, ""])
				else:
					table.append([key, value, "", ""])
				
			print tabulate(table)
			print "\n"
			
	def get_users(self, id, property="~all", profile="~all"):
		query = self.service.management().profileUserLinks().list(
			accountId=id,
			webPropertyId=property,
			profileId=profile
		) 
		users = self.execute_query(query)
		return users
    	
	def list_accounts(self):
		"""
		Returns list of owned accounts
		"""
		query = self.service.management().accounts().list()
		accounts = self.execute_query(query)

		self.print_table(accounts.get("items"))
		return accounts

	def list_properties(self, account):
		query = self.service.management().webproperties().list(accountId=account)
		properties= self.execute_query(query)

		self.print_table(properties.get("items"))
		return properties	
		
	def list_profiles(self, account, property):
		query = self.service.management().profiles().list(accountId=account,webPropertyId=property)
		profiles = self.execute_query(query)

		self.print_table(profiles.get("items"))
		return profiles

	def list_users(self, id, property="~all", profile="~all"):
		users = self.get_users(id, property, profile)["items"]
		self.print_table(users)
			
	def add_user(self, id, email, permissions=["READ_AND_ANALYZE"]):
		query = self.service.management().accountUserLinks().insert(
				accountId=id,
				body={
					'permissions': {
						'local': permissions
					},
					'userRef': {
						'email': email
					}
				}
			)
		add = self.execute_query(query)
		print "User %s has been added" % email		
		
	def delete_user(self, id, email):
		#to delete user must find their link ID
		users = self.get_users(id)
		for user in users["items"]:
			if user["userRef"]["email"] == email:
				#user[id] comes from profileUserLinks func so must take out profile id and swap for account id for accountUserLinks func
				main = user["id"]
				separate_id = main.split(":")[1]
				link_id = id + ":" + separate_id
				break
			else:
				link_id = None
				raise Exception("Could not find user")
		query = self.service.management().accountUserLinks().delete(
				accountId=id,
				linkId=link_id
			)
		delete = self.execute_query(query)
		print "User %s has been removed" % email
		
		
		
		
		
		