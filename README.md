# phishnet_api_v3

phishnet_api_v3 is a Python client for v3 of the [Phish.net API](http://api.phish.net).  It works with either Python 3 and supports all of the endpoints provided by api.phish.net/v3.

# Installation

You guessed it...

```
pip install phishnet_api_v3
```

# Getting Started

Version 3 of the API is a complete rewrite. access to all endpoints require an apikey. To get one go to https://api.phish.net/keys/ to request one. You can have up to 5 unique apikeys for your applications.

As you browse the [Phish.net API documentation](https://phishnet.api-docs.io/v3/the-phish-net-api/welcome) you will see that Version 3 also introduced a new security scheme via a unique hash generated on a client to retrieve an authorization key. Like the previous version of our API, there are API methods designated as writable that require a special per-user, per-app authorization key called an "authkey" that must match a uid and your apikey. To obtain this key,  the user you want to access one of these "writeable" endpoints on behalf of must go to https://phish.net/authorize?appid=<<appid>>&uid=<<uid>> to authorize your application. You will need to provide them your application id available at https://api.phish.net (you must be logged in to phish.net )

## Public API Methods

For API calls that do not require a authkey, you simply need to instantiate the PhishNetAPI class, and call the methods for each of the API methods. There are 2 ways to set the apikey. The easiest way is to create a .env file in the current directory you are calling this API wrapper (see .env.SAMPLE in the root directory of this project.) it should look like this:

```
export APIKEY=<<YOURAPIKEYHERE>>
export APPID=<<YOURAPPIDHERE>>
export PRIVATE_SALT=<<YOURPRIVATESALTHERE>>
```
the PRIVATE_SALT is also available from https://api.phish.net/keys/ and is used to retrieve the authkey from the /authorize/get endpoint. The other way to set the apikey is to pass it into the constructor:

``` python
>>> from phishnet_api_v3 import PhishNetAPI
>>> api = PhishNetAPI(<YOURAPIKEYHERE>)
>>> artists = api.get_artists()
>>> artists
{'error_code': 0, 'error_message': None, 'response': {'count': 5, 'data': {'1': {'artistid': 1, 'name': 'Phish', 'link': 'http://phish.net/setlists/phish'}, '2': {'artistid': 2, 'name': 'Phish', 'link': 'http://phish.net/setlists/trey'}, '6': {'artistid': 6, 'name': 'Phish', 'link': 'http://phish.net/setlists/mike'}, '7': {'artistid': 7, 'name': 'Phish', 'link': 'http://phish.net/setlists/fish'}, '9': {'artistid': 9, 'name': 'Phish', 'link': 'http://phish.net/setlists/page'}}}}
```

Attempting to call protected methods without calling authorize(<<uid>>) first will raise `phishnet_api_v3.exceptions.AuthError`. If you have your private_salt in .env then authorize() will be called for you. Once you authorize a user then authkey is available in the object for future use. If you change the uid then authorize() will need to be rerun to get the new authkey.

``` python
>>> api.get_user_details(1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./phishnet_api_v3
/phishnet_api_v3
/decorators.py", line 16, in wrapper
    raise AuthError("{} requires an auth key".format(qual_name_safe(f)))
phishnet_api_v3.exceptions.AuthError: PhishNetAPI.user_username_check requires an auth key
```

## Protected API Methods

In order to collect "protected" API methods, you must pass an API key into the constuctor.  

``` python
>>> from phishnet_api_v3 import PhishNetAPI
>>> my_api_key = "<MY API KEY>" # Private API key from http://api.phish.net/keys/
>>> phishnet = PhishNetAPI(api_key=my_api_key)
>>> phishnet.user_username_check("wilson")
{'success': '0', 'reason': 'Sorry! wilson is already taken.'}
```

### Methods requiring user authorization

Some protected methods additionally require an auth_key to take actions on behalf of specific users.  This includes submitting reviews, forum threads, or adding a show to "My Shows".

phishnet_api_v3 can make generating auth codes simpler by adding some logic on top of the ```pnet.api.*``` API methods.

The simplest way is probably by using the ```authorize``` method. In order to make this method work, you will need both the username and password of the user you are authorizing (at least the first time).

``` python
>>> from phishnet_api_v3 import PhishNetAPI
>>> my_api_key = "<MY API KEY>" # Private API key from http://api.phish.net/keys/
>>> phishnet = PhishNetAPI(api_key=my_api_key)
>>> phishnet.authorize('authorized_username', 'that_users_password')
```

If unsuccessful, the ```phishnet_api_v3.exceptions.AuthError``` will be raised. If successful, the authorized username and auth key will be stored as attributes on the instance you're working with.  

``` python
>>> phishnet.username
'authorized_username'
>>> phishnet.auth_key
'ABCD123456789012345'
```
Once those attributes have been set, you can make user-authorized API calls.  For example, lets add, and then remove [Halloween 2014](http://phish.net/setlists/?d=2014-10-31) to my shows.

``` python
>>> len(phishnet.user_myshows_get_authorized())
7
>>> phishnet.user_myshows_add('2014-10-31')
{'success': 1}
>>> len(phishnet.user_myshows_get_authorized())
8
>>> phishnet.user_myshows_remove('2014-10-31')
{'success': 1}
>>> len(phishnet.user_myshows_get_authorized())
7
```

Once authorized, you should not store the user's password (per the Phish.net terms).  