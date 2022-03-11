# About SynoChat
**SynoChat** is a Python package which allows for easy integration with the Synology Chat API in just a few lines of code.
According to the [documentation](https://kb.synology.com/sv-se/DSM/help/Chat/chat_integration?version=7) _(which is sadly a bit sparse)_, Synology Chat has support for both incoming and outgoing webhooks, slash commands and bots.

## Package support
This package currently supports:
* Incoming webhooks
* Outgoing webhooks
* Slash commands

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

# Incoming webhooks
Using an *incoming webhook* we can post messages into a channel in Synology Chat. Besides sending just simple text to a channel we can also attach links and file uploads (which are available via HTTP).

## Setting up integration
Before we start coding we must setup the incoming webhook integration in the Synology Chat client.

Do this by opening the Synology Chat client, either in the web application or the native desktop application, and go to **User Profile** > **Integration** and follow the instructions. Click [here](https://kb.synology.com/en-us/DSM/tutorial/How_to_configure_webhooks_and_slash_commands_in_Chat_Integration) for more help.

Take note of the Webhook-URL in the integration settings dialog. You need to extract two components from this link:
* Hostname (chat.example.com)
* Token (64 characters at the end of the line)

**Important!** Do not include **%22** surrounding the token in the URL. The token should be *exactly 64 characters*.

