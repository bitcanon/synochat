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
