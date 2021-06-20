# OCPP 1.6 Central System


 ## Table of Content

- [Introduction](#introduction)
  * [Motivations](#motivations)
  * [Brief OCPP Introduction](#brief-ocpp-introduction)
    + [OCPP Call Commands](#ocpp-call-commands)
    + [OCPP Call Result Messages](#ocpp-call-result-messages)
    + [OCPP Error Messages](#ocpp-error-messages)
- [Server Setup](#server-setup)
  * [Redis Setup](#redis-setup)
  * [Virtual Environment](#virtual-environment)
  * [Secret Key](#secret-key)
  * [Database setup](#database-setup)
- [Running the Code](#running-the-code)
- [Usage](#usage)
  * [Example 1](#example-1)
  * [Example 2](#example-2)


## Introduction


Welcome to the documentation for the OCPP 1.6J Central System. This library offers a comprehensive implementation of the ocpp 1.6 protocol along with all of the needed types and the needed callback functions for each type. This central system performs a lot of the heavy lifting when it comes to the OCPP implementation and therefore it makes the developer's job a lot easier. This library is designed to be used to a Django channels app but does not strictly require that.

### Motivations


The reason I decided to create this library is simply because there were not other libraries that offered what I was looking for when I was working with OCPP 1.6. I had been looking for a library that offers me all of the types present in the OCPP standard and one where the types are documented and clear. However, some of the libraries that offered that did not offer any other interoperability with external commands and the systems were constrained to communicating using OCPP. Obviously, in a real world setting, the Central System doesn't exist as an entity to just communicate with the chargers, but also with the company that manages them or the end-user. So, interoperability was a major focus of mine when building this. During this read me file I will note on a few things built into this library that make it very easy to use with external commands.

### Brief OCPP Introduction


It is recommended that you first go through the OCPP documentation before jumping into this code. It will give you a much clearer idea on what the standard is like, what the message types are, and what a typical OCPP command looks like. That being said, you will find ample documentation throughout this code to guide you through using this library. If you're using a modern text editor such as Visual Studio Code, you will find that type hinting will be your best friend throughout your OCPP development with this library.

When it comes to OCPP there are three main kind of commands that exist in the protocol. A `Call`, `CallResult` and `CallError`. The diagram shown below describes the relationship between `Call` and `CallResult` messages in a simple way:

![Ocpp image](https://imgur.com/6YRKEOU.png)

#### OCPP Call Commands


A `Call` command is any command sent by the Central System or the Charging Point to the other party asking for a certain action. Contrary to popular belief, `Call` commands can be sent by the Central System or the Charging point. An example of a `Call` command would be the central system sending a message with the action `RemoteStartTransaction` to the Charging Point to ask it to begin charging the EV. The basic format of a call command is as follows:

```
[<message_type_id>, <message_id>, <action>, <payload>]
```

An example of an OCPP call message would look something like the following: 

```json
[
	2,
	"8033836061",
	"RemoteStartTransaction",
	{
		"idTag": {
			"IdToken": "RandomToken"
		}
	}
]
```

Where this message would prompt the Charging Point to begin charging the EV. 

> **Note:** What you're looking at here is a low level view of what the JSON result of the command looks like. When developing using this library all you would need to do to perform the above would be calling the `RemoteStartTransaction` function from the `Call.CallHandler` class. We will discuss more about this in a later section.

#### OCPP Call Result Messages


Whenever a `Call` message is sent, the other party must respond with a `CallResult` message back confirming that they have received the original `Call` message and affirming whether they have accepted or rejected the command requested in the `Call` message. The structure of a typical `CallResult` is as follows:

```
[<message_type_id>, <message_id>, <payload>]
```

Its very important to note that the `message_id` in the `Call` and its respective `CallResult` must be the same. No other two pairs can have the same `message_id` as it uniquely links the `Call` to the `CallResult` (and possibly the `CallError` if that does happen).

Following the example given above of the Central System asking the Charging point to begin charging by sending a `RemoteStartTransaction` `Call` message. The Charging Point will respond with the following `CallResult` if it accepts the request:

```json
[
	3,
	"8033836061", 
	{
		"status": "Accepted"
	}
]
```

The Central System receiving this `CallResult` message will signify to it that the Charging Point has accepted the `RemoteStartTransaction` request and that it will perform that. In the example that we have given, there will be other calls made back and fourth until the EV actually begins charging.

#### OCPP Error Messages 


We discussed that a typical `Call` message will have a `CallResult` as the response. However, in cases where an error occurs in the the request, the `Call` will me responded to with a `CallError` message. These messages will contain information on why the command failed and perhaps a description of that as well. These messages have the following format:

```
[ <message_type_id>, <message_id>, <error_code>, <error_description>, <error_details> ]
``` 

Following the same example which we have been using. Let's say that on a given charger the `RemoteStartTransaction` routine is not implemented in code thus no way of executing this action exists. Then, the Charging Point is expected to respond back with a `CallError` like the following:

```json
[
	4,
	"8033836061",
	"NotImplemented",
	"The action `RemoteStartTransaction` has not been implemented on this charging point",
	{}
]
```

Which will communicate to the Central System the Charging Point's inability to perform the action which has been sent.

> **Note:** The the `message_id` used throughout the examples is the same. This is the case with OCPP. The `Call` and `CallResult` or `Call` and `CallError` must have the same unique `message_id` to perform valid linkage between them.

## Server Setup


This portion of the documentation describes the steps needed to setup this server. It should be noted that this is a full Django project built with the Channels library.

### Redis Setup


First, please download docker as this project requires Redis which we will run in a docker container for ease of use. If you feel comfortable using Redis outside of docker then you can by all means do that. You can change the IP address and port of Redis from the `Settings.py` file in the `ocpp` directory.

If you will be using docker for Redis then run the following command:
```shell
docker run -p 6379:6379 -d redis:5
``` 

This command will need to be run each time before running the server. 

### Virtual Environment


We now need to setup the environment in which the project will run. We first need to create a python virtual environment which we can do by using the following command:

```shell
python3 -m venv env
```

This will create a virtual environment with the name `env`. We now need to activate this virtual environment. To do that we will run the following command: 

```shell
source ./env/bin/activate
```

> **Note:** The above command used to create the virtual environment and activate it might be different if you are on a Windows machine. If this is the case please check how a virtual environment can be created and activated in Windows. All of the other steps will be the same.

With the virtual machine now activated we can now go ahead and make use of the `requirements.txt` file. We will need to install all of the packages listed in this file by running the following command:

```shell
pip3 install -r rerequirements.txt
```

### Secret Key


With the virtual environment created we can now focus on creating the secret key and storing it. Please create a cryptographic secret key for Django. Once you have your secret key run the following command:

```shell
echo "SECRET_KEY = 'YourSecretKey'" > .env
```

This command will create a file called `.env` which will store the value of the `SECRET_KEY`.

> **Note:** It's important to note that `.env` and `env` are not the same thing. `env` is a directory that contains the python virtual environment while `.env` is a file containing a number of environment variables which we aim to hide from the public. The main idea is that the `.env` file is never uploaded to github and so it can contain encryption keys or other sensitive information.

Please be very careful about your `.env` file as this file now contains your `SECRET_KEY` which is the encryption key used by the Django project. It's best to put the `.env` file in the `.gitignore` file as a safety measure so that it's never committed to github.

### Database setup


Now that we have setup both the virtual environment and the Django `SECRET_KEY` we are actually ready now to get the database up and running. To do that, run the two commands that follow:

```shell
python3 manage.py makemigrations
python3 manage.py migrate
```

Your database will now be ready assuming that no errors took place.

## Running the Code


Assuming that you have been able to run all of the above commands and faced no issues, then running this code will be quite easy. Run the two commands below to ensure that the Redis docker container is running and to then run the server

```shell
docker run -p 6379:6379 -d redis:5
python3 manage.py runserver 0.0.0.0:8000
```

Your Django server is now listening on your LAN IP and your public IP too on port 8000. 

> **Note:** The port used by Redis is not of a concern to us. We only need to specify it in the `Settings.py` file in the `ocpp` directory. Aside from that we will not be using this port number at all again.

## Usage


We have been talking about the `RemoteStartTransaction` action for a while now so let's give an example using it. All requests that the Central System can make to a Charging Point are all grouped under the `Call.CallHandler` class and more specifically under the `issue_command` function. This function is used to issue any command we want to any charger that we have. 

### Example 1


Let's say that we have a charger with the charger id of `ESP32_Charger` which we want to issue a `RemoteStartTransaction` request for. The way we can go about doing that is as follows:

```python
from ocpp_lib.call import Call
from ocpp_lib.types import RemoteStartTransaction_Req, IdToken
import asyncio

async def main():
    response = await Call.CallHandler.issue_command(
        charger_id = "ESP32_Charger",
        request = RemoteStartTransaction_Req(
            idTag = IdToken(
                IdToken = "RandomToken",
            ),
            connectorId = 1
            ),
        shouldAwait = True
    )

asyncio.run(main)
```

The above code will then issue a `RemoteStartTransaction` request to the charger with the ID `ESP32_Charger`.  A big advantage offered in this library is that the `Call.CallHandler` class can actually wait for the response of the message to come back. So, in the above example, if the `shouldAwait` flag is true, then the function will wait until the response has been received before returning back.

This is very useful if you're trying to know what the status of the message is and want to check if the message has been successfully sent or perhaps accepted.

### Example 2


Another thing that this library allows you to do is to add your own code to the library and customize if however you want. If you take a look at the contents of the `Call.Callbacks` class you will see a number of callback functions. These callback functions return a `CallResult` and as you might guess are executed once a Call is received.

Lets say that you're trying to write your own callback function that will execute once the Central System receives a `StartTransaction` request and you want it to print the `connectorId` of the Charging Point. You can go about doing that by adding the following function to the `Call.Callbacks` class

```python
def StartTransaction(message_id:str, call_payload:dict) -> StartTransaction_Conf:
	# Printing the connectorId
	print(call_payload['connectorId'])
	
	# Returning the response back
	return StartTransaction_Conf(
	    idTagInfo = IdTagInfo(
	        status = AuthorizationStatus.Accepted,
	    ),
	    transactionId = 1
	)
```

This is an example of how you can access the data present in the payloads. Now you have the freedom to perform your own data processing and conditionals. 

What I mean by the above statement is let's say that in our database we know that only connector 1 works and connector 2 does not work. By using the callback functions present here, we can add code such as the following to only allow `StartTransaction` to connector 1.

```python
def StartTransaction(message_id:str, call_payload:dict) -> StartTransaction_Conf:
	# Printing the connectorId
	connector_id = call_payload['connectorId']
	
	# Returning the response back
	return StartTransaction_Conf(
	    idTagInfo = IdTagInfo(
	        status = AuthorizationStatus.Accepted if connector_id == 1 else AuthorizationStatus.Rejected,
	    ),
	    transactionId = 1
	)
```

Thus, we have used conditionals to determine whether the transaction request should be accepted or rejected.