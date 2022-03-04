import json
from requests import post

from requests.compat import quote

from synochat.exceptions import *


'''
This is the documentation that has been used to implement this module.
It can also help you setting up the integration within the Chat client.
Source: https://kb.synology.com/en-us/DSM/tutorial/How_to_configure_webhooks_and_slash_commands_in_Chat_Integration#x_anchor_id5
'''

class IncomingWebHook(object):
	""" Class definition of an incoming webhook in Synology Chat. """

	def __init__(self, hostname, token, port=443, verify_ssl=True):
		""" Initiate the object. """
		self.__hostname = hostname
		self.__port = port
		self.__use_https = True
		self.__verify_ssl = verify_ssl
		self.__api = 'SYNO.Chat.External'
		self.__method = 'incoming'
		self.__version = '2'
		self.__token = token

		# Automatically disable HTTPS on port 80 and 5000
		if port == 80 or port == 5000:
			self.__use_https = False

	def send(self, text, file_url=None):
		""" Send a text message to the channel associated with the token """
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
		}

		protocol = 'https' if self.__use_https else 'http'
		params = {
			'api': self.__api,
			'method': self.__method,
			'version': self.__version,
			'token': self.__token
		}

		# URL to the Synology Chat API endpoint
		url = f"{protocol}://{self.__hostname}:{self.__port}/webapi/entry.cgi"

		# Data dictionary to be sent to the server
		payload_data = {'text': text}

		# Check if there is a URL to include in the request
		if file_url:
			payload_data['file_url'] = file_url

		# Prepare the payload
		payload = f"payload={json.dumps(payload_data)}"

		# Query the Synology Chat API and save the response
		response = post(url, data=payload, headers=headers, params=params, verify=self.__verify_ssl)
		
		return self.checkResponse(response)

	def checkResponse(self, response):
		""" Check the response from the Synology Chat Server. """

		# Check HTTP response status codes
		status_code = response.status_code

		if status_code == 200:
			try:
				response_array = json.loads(response.text)
			except:
				print(response.text)
		else:
			print(f"Status code: {status_code}")

		# Check API response status codes
		if response_array['success']:
			print('OK')
		else:
			try:
				error_code = response_array['error']['code']
			except KeyError:
				error_code = None

			try:
				error_message = response_array['error']['errors']
			except KeyError:
				error_message = 'Unknown error.'

			print(f"Error {error_code}: {error_message}")

			if error_code == 102:
				raise InvalidApiError()
			elif error_code == 103:
				raise InvalidMethodError()
			elif error_code == 104:
				raise InvalidVersionError()
			elif error_code == 117:
				raise UnknownPayloadError()
			elif error_code == 404:
				raise InvalidTokenError()
			else:
				print(response.text)
				raise UnknownApiError()


		return True

	@property
	def hostname(self):
		return self.__hostname

	@hostname.setter
	def hostname(self, hostname):
		self.__hostname = hostname

	@property
	def port(self):
		return self.__port

	@port.setter
	def port(self, port):
		self.__port = port

	@property
	def use_https(self):
		return self.__use_https

	@use_https.setter
	def use_https(self, use_https):
		self.__use_https = use_https

	@property
	def verify_ssl(self):
		return self.__verify_ssl

	@verify_ssl.setter
	def verify_ssl(self, verify_ssl):
		self.__verify_ssl = verify_ssl

	@property
	def token(self):
		return self.__token

	@token.setter
	def token(self, token):
		self.__token = token

	@property
	def api(self):
		return self.__api

	@api.setter
	def api(self, api):
		self.__api = api

	@property
	def method(self):
		return self.__method

	@method.setter
	def method(self, method):
		self.__method = method

	@property
	def version(self):
		return self.__version

	@version.setter
	def version(self, version):
		self.__version = version
