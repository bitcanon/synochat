import json
from requests import post

from requests.compat import quote

from synochat.exceptions import *


'''
This is the documentation that has been used to implement this module.
It can also help you setting up the integration within the Chat client.
Source: https://kb.synology.com/en-us/DSM/tutorial/How_to_configure_webhooks_and_slash_commands_in_Chat_Integration#x_anchor_id5
'''

class IncomingWebhook(object):
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

	def __init__(self, name, optional):
		""" Initiate the object. """
		self.__name = name
		self.__value = None
		self.__optional = optional
		self.__detected = False

	def __str__(self):
		""" Define how the print() method should print the object. """
		object_type = str(type(self))
		return object_type + ": " + str(self.as_dict())

	def __repr__(self):
		""" Define how the object is represented when output to console. """

		class_name          = type(self).__name__
		name                = f"name = '{self.name}'"
		value               = f"value = '{self.value}'"
		optional            = f"optional = {self.optional}"
		detected            = f"detected = {self.detected}"

		return f"{class_name}({name}, {value}, {optional}, {detected})"

	def as_dict(self):
		""" Return the object properties in a dictionary. """
		return {
			'name': self.name,
			'value': self.value,
			'optional': self.optional,
			'detected': self.detected,
		}

	def isPresent(self):
		""" More user-friendly/readable version of 'detected'. """
		return self.detected

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, value):
		self.__value = value

	@property
	def detected(self):
		return self.__detected

	@detected.setter
	def detected(self, detected):
		self.__detected = detected

	@property
	def name(self):
		return self.__name

	@property
	def optional(self):
		return self.__optional


class SlashCommand(object):
	""" Class definition of a slash command in Synology Chat. """

	def __init__(self, data, verbose=False):
		""" Initiate the object. """
		self.__client_token = None
		self.__server_token = data['token']
		self.__user_id 		= data['user_id']
		self.__username 	= data['username']
		self.__text 		= data['text']
		self.__parameters   = []
		self.__verbose = verbose

		if verbose:
			self.showHttpDebug()

	@property
	def text(self):
		return self.__text

	def addParameter(self, name, optional=False):
		""" Parse and add a parameter to the slash command. """
		parameter = Parameter(name, optional)
		self.parseParameter(parameter)
		self.__parameters.append(parameter)
		return parameter

	def getParameter(self, name):
		""" Get a parameter object by name. """
		for param in self.__parameters:
			if param.name == name:
				return param
		return None

	def parseParameter(self, parameter):
		""" 
		Parse the incoming text string received from the Synology Chat client.
		Example: /command param1 param2 [param3] [param4=1337]
		"""

		# Split the command into a list() and remove the '/command' item from the list
		command_parameters = self.__text.split()[1:]

		# Handle optional parameter
		if parameter.optional:

			# Try to find this parameter in command_parameters
			for command_parameter in command_parameters:
				if parameter.name in command_parameter:

					# If the parameter has a value (ex: delay=5) then
					# save the value in the parameter object,
					# if not we set the value to None.
					parameter.detected = True
					param_list = command_parameter.split('=')
					if len(param_list) == 2:
						parameter.value = param_list[1]
					else:
						parameter.value = None
		# Handle positional parameter
		else:
			try:
				index = len(self.__parameters)
				parameter.value = command_parameters[index]
				parameter.detected = True
			except IndexError:
				raise ParameterParseError()
		if self.__verbose:
			self.showParamDebug(parameter)

	def authenticate(self, token):
		""" Compare the client and server API token. """
		self.__client_token = token
		return token == self.__server_token

	def createResponse(self, text, file_url=None):
		""" Send a text message to the channel associated with the token. """
		returnDict = {'token': self.__client_token, 'text': text, 'user_id': self.__user_id, 'username': self.__username}
		return returnDict

	def invalidTokenResponse(self):
		""" Return an invalid token HTTP response. """
		response = {'success': False}
		return json.dumps(response), 403

	def showHttpDebug(self):
		""" Show debug information. """
		print('----------------------')
		print('Incoming HTTP request:')
		print('----------------------')
		print(f" Client Token    : {self.__client_token}")
		print(f" Server Token    : {self.__server_token}")
		print(f" User ID         : {self.__user_id}")
		print(f" Username        : {self.__username}")
		print(f" Text            : {self.__text}")
		print('----------------------')

	def showParamDebug(self, parameter):
		index = len(self.__parameters)
		print(f"Parsing parameter {index}: '{parameter.name}'...")
		print(f" - value    = {parameter.value}")
		print(f" - optional = {parameter.optional}")
		print(f" - detected = {parameter.detected}")

class OutgoingWebhook(object):
	""" Class definition for an Outgoing Webhook. """

	""" Example of an Outgoing Webhook received from Synology Chat.
	('token', 'f69oQY4l5v7UVzKqmVfw1MQgFGZmxwODg1sndKIqsz8grAqYnKyerCRISQa1MiJj'), 
	('channel_id', '34'), 
	('channel_type', '1'), 
	('channel_name', 'Labb'), 
	('user_id', '4'), 
	('username', 'mikael'), 
	('post_id', '146028888128'), 
	('thread_id', '0'), 
	('timestamp', '1646827836131'), 
	('text', 'Tjena'), 
	('trigger_word', 'Tjena')
	"""

	def __init__(self, data, token, verbose=False):
		""" Initiate the object. """
		self.__client_token = token
		self.__server_token = data['token']
		self.__channel_id 	= data['channel_id']
		self.__channel_type = data['channel_type']
		self.__channel_name = data['channel_name']
		self.__user_id 		= data['user_id']
		self.__username 	= data['username']
		self.__post_id 		= data['post_id']
		self.__thread_id 	= data['thread_id']
		self.__timestamp 	= data['timestamp']
		self.__text 		= data['text']
		self.__trigger_word = data['trigger_word']
		self.__verbose 		= verbose

		#if verbose:
			#self.showHttpDebug()

	def __str__(self):
		""" Define how the print() method should print the object. """
		object_type = str(type(self))
		return object_type + ": " + str(self.as_dict())

	def __repr__(self):
		""" Define how the object is represented when output to console. """

		class_name     	= type(self).__name__
		client_token   	= f"client_token = '{self.client_token}'"
		server_token   	= f"server_token = '{self.server_token}'"
		channel_id     	= f"channel_id = {self.channel_id}"
		channel_type   	= f"channel_type = {self.channel_type}"
		channel_name   	= f"channel_name = '{self.channel_name}'"
		user_id        	= f"user_id = {self.user_id}"
		username       	= f"username = '{self.username}'"
		post_id        	= f"post_id = {self.post_id}"
		thread_id      	= f"thread_id = {self.thread_id}"
		timestamp      	= f"timestamp = {self.timestamp}"
		text           	= f"text = '{self.text}'"
		trigger_word  	= f"trigger_word = '{self.trigger_word}'"
		verbose 		= f"verbose = {self.verbose}"

		return f"{class_name}({client_token}, {server_token}, {channel_id}, {channel_type}, {channel_name}, {user_id}, {username}, {post_id}, {thread_id}, {timestamp}, {text}, {trigger_word}, {verbose}, )"

	def as_dict(self):
		""" Return the object properties in a dictionary. """
		return {
			'client_token': self.client_token,
			'server_token': self.server_token,
			'channel_id': self.channel_id,
			'channel_type': self.channel_type,
			'channel_name': self.channel_name,
			'user_id': self.user_id,
			'username': self.username,
			'post_id': self.post_id,
			'thread_id': self.thread_id,
			'timestamp': self.timestamp,
			'text': self.text,
			'trigger_word': self.trigger_word,
			'verbose': self.verbose,
		}

	def authenticate(self, token):
		""" Compare the client and server API token. """
		self.__client_token = token
		return token == self.__server_token

	def createResponse(self, text):
		""" Send a text message to the channel associated with the token. """
		payload_data = {
			'token': self.__client_token,
			'text': text,
			'user_id': self.__user_id,
			'username': self.__username,
		}

		return json.dumps(payload_data)

	@property
	def client_token(self):
		return self.__client_token

	@property
	def server_token(self):
		return self.__server_token

	@property
	def channel_id(self):
		return self.__channel_id

	@property
	def channel_type(self):
		return self.__channel_type

	@property
	def channel_name(self):
		return self.__channel_name

	@property
	def user_id(self):
		return self.__user_id

	@property
	def username(self):
		return self.__username

	@property
	def post_id(self):
		return self.__post_id

	@property
	def thread_id(self):
		return self.__thread_id

	@property
	def timestamp(self):
		return self.__timestamp

	@property
	def text(self):
		return self.__text

	@property
	def trigger_word(self):
		return self.__trigger_word

	@property
	def verbose(self):
		return self.__verbose
