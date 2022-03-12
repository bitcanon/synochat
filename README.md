# About SynoChat
**SynoChat** is a Python package which allows for easy integration with the Synology Chat API in just a few lines of code.
According to the [documentation](https://kb.synology.com/sv-se/DSM/help/Chat/chat_integration?version=7) _(which is sadly a bit sparse)_, Synology Chat has support for both incoming and outgoing webhooks, slash commands and bots.

## Package support
This package currently supports:
* **Incoming webhooks:** Send messages to a chat channel in Synology Chat from the `synochat` library.
* **Outgoing webhooks:** Send messages from Synology Chat to the `synochat` library.
* **Slash commands:** Send commands with parameters from Synology Chat to the `synochat` library.

## Installation
It is recommended to install this package inside a virtual environment as with most Python packages. Use `pip` to install the package.

### Create virtual environment
```bash
$ virtualenv venv
$ source venv/bin/activate
```
### Install package
```
$ pip install synochat
```

## Setting up integration
Before we start coding we must setup the integration in the Synology Chat client.

Do this by opening the Synology Chat client, either in the web application or the native desktop application, and go to **User Profile** > **Integration** and follow the instructions. Click [here](https://kb.synology.com/en-us/DSM/tutorial/How_to_configure_webhooks_and_slash_commands_in_Chat_Integration) for more help.

Take note of the Webhook-URL in the integration settings dialog. You need to extract two components from this link:
* Hostname (chat.example.com)
* Token (64 characters at the end of the line)

**Important!** Do not include **%22** surrounding the token in the URL. The token should be *exactly 64 characters*.


# Incoming webhooks
Using an *incoming webhook* we can post messages into a channel in Synology Chat. Besides sending just simple text to a channel we can also attach links and file uploads (which are available via HTTP).

## Code
Use this simple code example to send a message to the chat channel associated with this token.
```python
from synochat.webhooks import IncomingWebhook

token = "w6Jw1Z6EpEONtabCfcTk6YObsaaj958fGzWOTQe0s33pl42RVLmkRUJBWoCgSfoz"
webhook = IncomingWebhook('chat.example.com', token)

webhook.send('This text is sent to Synology Chat.')
```

### Add a link
We can easily add a link to the message with the `<` and `>` characters.
```python
webhook.send('Send text with a link embedded <https://www.synology.com>')
```

Define the *link text* by appending `|text` to the link tag.
```python
webhook.send('Check out <https://www.synology.com/en-us/dsm/feature/chat|Synology Chat>!')
```
This is how it might look in the Synology Chat client:

<img src="/img/incoming-webhook-with-link.png" width="480">

### Add an image
Add an image file to the message by passing a URL in the `file_url` parameter.
```python
webhook.send('Send text with a photo attached.', file_url='https://www.synology.com/img/company/branding/synology_logo.jpg')
```

### Add a file
Or upload a file of any type by passing a URL to the file in the `file_url` parameter.
```python
webhook.send('Send text with a file attached.', file_url='http://ipv4.download.thinkbroadband.com/5MB.zip'')
```

### Advanced
If you access your Synology DiskStation on a different port than the default for this library (HTTPS/443) or if you don't have a valid SSL certificate on you NAS (which you should), you can tweak these settings like this:
```python
webhook = IncomingWebhook('192.168.0.2', token, port=5001, verify_ssl=False)
```
Note that this will still use HTTPS (https://...) in the request to the Synology Chat server. If running HTTP on port 5001, change to HTTP (http://...) like so:
```python
webhook.use_https = False
```
It is also possible to change these settings via class properties:
```python
webhook.hostname = "nas.yourdomain.com"
webhook.port = "443"
webhook.use_https = True
webhook.verify_ssl = True
webhook.token = "..."
```
Make sure to set them before calling the `send()` method.

### Exceptions
The `send()` method will raise an exception if the request to the Synology Chat server fails for some reason.

Check out the examples or the exception files for more information.

# Outgoing webhooks
Outgoing webhooks listen for trigger words in Chat messages. When a trigger word is noticed, a call is made to the webhook associated with the trigger word.
Consider the following example:

<img src="/img/outgoing-webhook-settings.png" width="480">

When the word `Ping` *(case sensitive)* is noticed in a chat message, a call is made to http://192.168.0.2:5001/echo

## Code
To setup the listening part of this functionality we can use the Flask framework, which is a lightweight web framework for Python.

```python
from flask import Flask, request

from synochat.webhooks import OutgoingWebhook

app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def echo():
	token = 'f69oQY4l5v7UVzKqmVfw1MQgFGZmxwODg1sndKIqsz8grAqYnKyerCRISQa1MiJj'
	webhook = OutgoingWebhook(request.form, token, verbose=True)

	if not webhook.authenticate(token):
		return webhook.createResponse('Outgoing Webhook authentication failed: Token mismatch.')

	print(webhook)

	return webhook.createResponse('Pong')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug = True)
```

The code is self explanatory. To debug the request you can use the `print(webhook)` method:
```bash
<class 'synochat.webhooks.OutgoingWebhook'>: {'client_token': 'f69oQY4l5v7UVzKqmVfw1MQgFGZmxwODg1sndKIqsz8grAqYnKyerCRISQa1MiJj', 'server_token': 'f69oQY4l5v7UVzKqmVfw1MQgFGZmxwODg1sndKIqsz8grAqYnKyerCRISQa1MiJj', 'channel_id': '34', 'channel_type': '1', 'channel_name': 'Labb', 'user_id': '4', 'username': 'mikael', 'post_id': '146028888230', 'thread_id': '0', 'timestamp': '1647060330657', 'text': 'Ping', 'trigger_word': 'Ping', 'verbose': True}
```

### Class properties
To access the data from the outgoing webhook, use the **class properties** *(which are read-only)*:
```python
webhook.client_token
webhook.server_token
webhook.channel_id
webhook.channel_type
webhook.channel_name
webhook.user_id
webhook.username
webhook.post_id
webhook.thread_id
webhook.timestamp
webhook.text
webhook.trigger_word
webhook.verbose
```

### Add a link
Like with an *incoming webhook* we can easily add a link to the response message with the `<` and `>` characters.
```python
webhook.createResponse('Send text with a link embedded <https://www.synology.com>')
```

Define the *link text* by appending `|text` to the link tag.
```python
webhook.createResponse('Check out <https://www.synology.com/en-us/dsm/feature/chat|Synology Chat>!')
```

### Add an image
Add an image file to the message by passing a URL in the `file_url` parameter.
```python
webhook.createResponse('Send text with a photo attached.', file_url='https://www.synology.com/img/company/branding/synology_logo.jpg')
```

### Add a file
Or upload a file of any type by passing a URL to the file in the `file_url` parameter.
```python
webhook.createResponse('Send text with a file attached.', file_url='http://ipv4.download.thinkbroadband.com/5MB.zip'')
```

# Slash commands
With **slash commands** we can trigger outgoing webhooks by typing `/` in the text field of the Synology Chat client. In contrast to *outgoing webhooks* the response from the slash command is only visible to the user who triggered the command.

## Parameters
A **slash command** can also accept parameters, both *positional* and *optional*.

### Positional parameters
Positional parameters *must* appear in the correct order for them to be parsed correctly.

Example:
```bash
/ping 1.1.1.1 count=4 time
```
In the example above we have a slash command named `/ping`.
* `1.1.1.1` is the first positional parameter. The `name` is defined in the code, for example **ip**.

**Important!** Positional parameters **must** be placed in the **first** part of the slash command *(before optional parameter)*.

Example:
```bash
/command positionalParam1 positionalParam2 optionalParam1 optionalParam2
```

Define a parameter as **positional** by calling the `addParameter()` method, which creates a positional parameter by default. 
```python
ip = command.addParameter('ip')
```

### Optional parameters
Optional parameters can appear in *any order* as long as they appear after the positional parameters.

Example:
```bash
/ping 1.1.1.1 count=4 time
```
In the example above we have a slash command named `/ping`.
* `count=4` is the first *optional parameter*. The `name` is **count** and the `value` is **4**.
* `time` is the seconds *optional parameter*. The `name` is **time** and the `value` is **None**.

**Important!** Optional parameters **must** be placed in the **last** part of the slash command *(after positional parameters)*.

Define a parameter as **optional** by calling the `addParameter()` method with `optional=True`.
```python
count = command.addParameter('count', optional=True)
time  = command.addParameter('time', optional=True)
```

## Settings
Go to the Integration settings of the Synology Chat client to setup a **slash command**:

<img src="/img/slash-command-settings.png" width="480">

It is now time for the implementation of this example.

## Code
In order for us to setup the receiving end of the slash command we can use Flask here as well.

```python
from flask import Flask, request

from synochat.webhooks import SlashCommand
from synochat.exceptions import *

app = Flask(__name__)

@app.route('/slash', methods=['POST'])
def slash():
	token   = 'LnTEXv9xKBwJtmIiXttGvpKaccEDHVJU5No4XX6oTnt7BQnPxbDwsWey1Pb9g9V2'
	command = SlashCommand(request.form)

	if not command.authenticate(token):
		return command.createResponse('Invalid token.')

	# Check if the command parameters are valid
	try:
		action  = command.addParameter('action')
		code    = command.addParameter('code',  optional=False)
		delay   = command.addParameter('delay', optional=True)
		silent  = command.addParameter('silent', optional=True)
	except ParameterParseError:
		return command.createResponse('Slash command failed because one or more parameters are missing.')

	# Handle the first (positional) parameter
	if action.isPresent():
		print(action)
	else:
		print(f"Parameter 'action' not detected in the command.")

	# Handle the second (positional) parameter
	if code.isPresent():
		print(code)
	else:
		print(f"Parameter 'code' not detected in the command.")

	# Handle the third (optional) parameter
	if delay.isPresent():
		print(delay)
	else:
		print(f"Parameter 'delay' not detected in the command.")

	# Handle the third (optional) parameter
	if silent.isPresent():
		print(silent)
	else:
		print(f"Parameter 'silent' not detected in the command.")

	return command.createResponse('Slash command received.')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug = True)
```

Now try to call this command in Synology Chat:

<img src="/img/slash-command-send.png" width="600">

The `addParameter()` method is in charge of adding an object of the `Parameter` class as well as to populate the object with the data received from the Synology Chat client.

The `isPresent()` method is used to check if the parameter was included in the slash command. This method is mostly usable for optional parameters.

We can output the properties of a `Parameter` by using the `print()` method. This should be the output if running the above code example:

```python
<class 'synochat.webhooks.Parameter'>: {'name': 'action', 'value': 'add',  'optional': False, 'detected': True}
<class 'synochat.webhooks.Parameter'>: {'name': 'code',   'value': '1234', 'optional': False, 'detected': True}
<class 'synochat.webhooks.Parameter'>: {'name': 'delay',  'value': '5',    'optional': True,  'detected': True}
<class 'synochat.webhooks.Parameter'>: {'name': 'silent', 'value': None,   'optional': True,  'detected': True}
```

### Class properties
To access the raw data from the *slash command*, use the **class property** *(which are read-only)*:
```python
command.text
```

To access the data from a *parameter*, use these **class properties** *(which are read-only)*.
```python
parameter.name
parameter.value
parameter.optional
parameter.detected
```

# Final word
This should be enough to get started using integrations with Synology Chat.

Good luck! 😁