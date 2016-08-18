from setuptools import setup, find_packages

setup(

	name="gamgmt",
	version="0.1",
	description="Python tool to manage Google Analytics accounts",
	url="https://github.com/gamernetwork/gamgmt",
	author="Faye Butler",
	author_email="faye.butler@gamer-network.net",
	packages=find_packages(),
	include_package_data=True,
    package_data = {
    	"":["*.json"],
    },
	install_requires=[
		"Click",
		"google-api-python-client",
		"httplib2",
		"oauth2client",
		"tabulate",
	],
	entry_points={
		"console_scripts" : [
			"gamgmt=gamgmt.commands:gamgmt",
		],
	},

)