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
				raise InvalidPayloadError()
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

class Parameter(object):
	""" Slash command parameter. """

	def __init__(self, name, valid_input, optional=False):
		""" Initiate the object. """
		self.__name = name
		self.__value = None
		self.__optional = optional
		self.__is_valid = False

		# Parse valid_input as either: 
		# 'opt1|opt2|opt3' or as ['opt1', 'opt2', 'opt3']
		if isinstance(valid_input, str):
			self.__valid_input = valid_input.split('|')
		elif isinstance(valid_input, list):
			self.__valid_input = valid_input

	def isValid(self):
		"""
		Returns True if this parameter value, which is received from the
		Synology Chat client, is present in the valid_input list
		of this parameter object.
		"""
		return self.__is_valid

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, value):
		self.__value = value

	@property
	def is_valid(self):
		return self.__is_valid

	@is_valid.setter
	def is_valid(self, is_valid):
		self.__is_valid = is_valid

	@property
	def name(self):
		return self.__name

	@property
	def valid_input(self):
		return self.__valid_input

	@property
	def optional(self):
		return self.__optional


class SlashCommand(object):
	""" Class definition of a slash command in Synology Chat. """

	def __init__(self, request, token, verbose=False):
		""" Initiate the object. """
		self.__client_token = token
		self.__server_token = request.form['token']
		self.__user_id 		= request.form['user_id']
		self.__username 	= request.form['username']
		self.__text 		= request.form['text']
		self.__request		= request
		self.__parameters   = []

		if verbose:
			self.showDebug()

	@property
	def text(self):
		return self.__text

	def addParameter(self, name, valid_input='*', optional=False):
		""" Add parameter to the slash command. """

		parameter = Parameter(name, valid_input, optional)
		self.__parameters.append(parameter)
		return parameter

	def getParameter(self, name):
		""" Get a parameter object by name. """
		for param in self.__parameters:
			if param.name == name:
				return param
		return None

	def parseParameters(self):
		""" 
		Parse the incoming text string received from the Synology Chat client.

		Example: /command opt1|opt2 param2 [param3]
		 - '/command'  - the slash command identifier.
		 - 'opt1|opt2' - the first parameter. It must be equal to either 'opt1' or 'opt2'.
		 - 'param2'    - the seconds parameter. It must be present and can contain any value.
		 - 'param3'    - the third parameter. It is optional and can contain any value.
		"""

		# Split the command into a list() and remove the '/command' item from the list
		command_parameters = self.__text.split()[1:]

		# Loop through the parameters defined in this slash command
		for index, parameter in enumerate(self.__parameters):

			if parameter.optional:
				if 0 <= index < len(command_parameters):
					parameter.value = command_parameters[index]
				else:
					parameter.value = None
			else:
				try:
					parameter.value = command_parameters[index]
				except IndexError:
					raise ParameterParseError()
			if parameter.value in parameter.valid_input or '*' in parameter.valid_input:
				parameter.is_valid = True
			#print(f"[{index}] Parsing {parameter.name}, valid_input='{parameter.valid_input}'")
			#print(f" - value = '{parameter.value}', is_valid = {parameter.is_valid}")

	def authenticate(self):
		""" Compare the client and server API token. """
		if self.__client_token != self.__server_token:
			raise InvalidTokenError()

	def createResponse(self, text, file_url=None):
		""" Send a text message to the channel associated with the token. """

		# Authenticate using the client token
		self.authenticate()

		returnDict = {'token': self.__client_token, 'text': text, 'user_id': self.__user_id, 'username': self.__username}
		return returnDict

	def invalidTokenResponse(self):
		""" Return an invalid token HTTP response. """
		response = {'success': False}
		return json.dumps(response), 403

	def showDebug(self):
		""" Show debug information. """
		print('----------------------')
		print('Incoming HTTP request:')
		print('----------------------')
		print(f" Client Token    : {self.__client_token}")
		print(f" Server Token    : {self.__server_token}")
		print(f" User ID         : {self.__user_id}")
		print(f" Username        : {self.__username}")
		print(f" Text            : {self.__text}")
		print(f" URL             : {self.__request.url}")
		print(f" User Agent      : {self.__request.user_agent}")
		print(f" Content Type    : {self.__request.content_type}")
		print(f" Remote Address  : {self.__request.remote_addr}")
		print(f" HTTP Method     : {self.__request.method}")

	def showParams(self):
		print('----------------------')
		print('Parameters:')
		print('----------------------')
		for param in self.__parameters:
			print(f"{param.name} = {param.valid_input}")
