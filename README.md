# phishnet_api_v3

phishnet_api_v3 is a Python client for v3 of the [Phish.net API](http://api.phish.net).  It works with either Python 3 and supports all of the endpoints provided by api.phish.net/v3.

# Installation

You guessed it...

```
pip install phishnet_api_v3
```

# Getting Started

Version 3 of the API is a complete rewrite. Access to all endpoints require an apikey. To get one go to https://api.phish.net/keys/ to request one. You can have up to 5 unique apikeys for your applications.

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

Attempting to call protected methods without calling authorize(<<uid>>) first will raise `phishnet_api_v3.exceptions.PhishNetAPIError`. If you have your private_salt in .env then authorize() will be called for you. Once you authorize a user then authkey is available in the object for future use. If you change the uid then authorize() will be rerun to get the new authkey. Below is an example of trying to get the authkey of a user who has not authorized your application for his uid:

``` python
>>> from phishnet_api_v3.api_client import PhishNetAPI
>>> api = PhishNetAPI()
>>> api.authorize(1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/fty/git/phishnet_api_v3/phishnet_api_v3/api_client.py", line 89, in authorize
    self.authkey = self.get_authkey(uid)
  File "/home/fty/git/phishnet_api_v3/phishnet_api_v3/api_client.py", line 103, in get_authkey
    return self._authority_get(uid)
  File "/home/fty/git/phishnet_api_v3/phishnet_api_v3/api_client.py", line 122, in _authority_get
    response = self.post(function='_authority_get',
  File "/home/fty/git/phishnet_api_v3/phishnet_api_v3/decorators.py", line 37, in wrapper
    return f(*args, **kwargs)
  File "/home/fty/git/phishnet_api_v3/phishnet_api_v3/api_client.py", line 422, in post
    raise PhishNetAPIError(
phishnet_api_v3.exceptions.PhishNetAPIError: phish.net API error: authority/get, 3, Invalid authorization key, this application is not writable
```

## API Methods

Starting with v3 of the phish.net API, all methods are considered "protected" API methods
and require an API key. You can have this as a OS environment variable via your OS mechanisms or via the .env file or you can pass the API key into the constuctor.  

``` python
>>> from phishnet_api_v3 import PhishNetAPI
>>> my_api_key = "<MY API KEY>" # Private API key from http://api.phish.net/keys/
>>> api = PhishNetAPI(my_api_key)
>>> api.get_user_details(80)
{'error_code': 0, 'error_message': None, 'response': {'count': 1, 'data': {'80': {'uid': 80, 'username': 'wsppan', 'realname': 'Jay Flaherty', 'joined': '2009-09-29', 'member_since': '10 years ago', 'avatar': 'https://smedia.pnet-static.com/avatars/default_avatar.png', 'link': 'http://phish.net/user/wsppan', 'isconfirmed': 'Yes', 'bio': 'My name is Jay and I am a Phishaholic', 'website': 'http://'}}}}

### get_recent_blogs
```python
PhishNetAPI.get_recent_blogs(self)
```

Get a list of recently posted entries to the phish.net blog (last 15 entries).
:return: json response object of recent blog entries - see tests/data/recent_blogs.json

### get_blogs
```python
PhishNetAPI.get_blogs(self, **kwargs)
```

Find all blogs that match the params below (maximum of 15 results)
:param **kwargs. Made up of at least one of the the following keys:
    month: The month of the year as as integer
    day: The day of the month as as integer
    year: The year as as integer
    monthname: month of the year (i.e. January)
    username: The username of the author
    author: the uid of the author
:return: json response object of blogs that match the query(see get_recent_blogs())

### get_artists
```python
PhishNetAPI.get_artists(self)
```

The artists/all endpoint returns an array of artists whose setlists are tracked
in the Phish.net setlist database, along with the associated artistid.
:return: json response object of all artists - see tests/data/all_artists.json

### get_show_attendees
```python
PhishNetAPI.get_show_attendees(self, **kwargs)
```

Find all attendees for a specific show
:param **kwargs: Made up of at least one of the the following keys:
    showid: the id for a specific show
    showdate: The date for a specific show
:return: json response object of attendees for a specific show.
    - see tests/data/show_attendees.json

### query_collections
```python
PhishNetAPI.query_collections(self, **kwargs)
```

Query user collections from the /collections/query endpoint.
:params **kwargs comprised of the following keys: collectionid, uid, contains.
    contains is a comma separated string of showid's
:returns: json response object with a list of collections.

### get_collection
```python
PhishNetAPI.get_collection(self, collectionid)
```

Get the details of a collection from the /collections/get endpoint.
:param collection_id: the collectionid associated with the collection.
:returns: json object of a collection detail. - see tests/data/get_collection.json

### get_all_jamcharts
```python
PhishNetAPI.get_all_jamcharts(self)
```

Get an array of songs that have jamcharts, song, songid, name, link, and number
from the /jamcharts/all endpoint.
:return: json response object of all jamcharts - see tests/data/all_jamcharts.json

### get_jamchart
```python
PhishNetAPI.get_jamchart(self, songid)
```

Get the details of a jamchart from the /jamcharts/get endpoint.
:param song_id: the songid associated with the jamchart.
:returns: json object of a jamchart detail. - see tests/data/get_jamchart.json

### get_all_people
```python
PhishNetAPI.get_all_people(self)
```

Get a list of personid, name, type, and a link to all shows in which a person is featured
from the people/all endpoint.
:returns: json object of all people - see tests/data/all_people.json

### get_all_people_types
```python
PhishNetAPI.get_all_people_types(self)
```

Get a dict of all people types from the people/get endpoint.
:returns: json object of all people types - see tests/data/all_people_types.json

### get_people_by_show
```python
PhishNetAPI.get_people_by_show(self, showid)
```

Get list of performers at a show from the /people/byshow endpoint.
:param show_id: the showid associated with the show.
:returns: json object of a list of performers for a show.
    - see tests/data/people_by_show.json

### get_appearances
```python
PhishNetAPI.get_appearances(self, personid, year=None)
```

Get list of appearances for a particular performer from the /people/appearances endpoint.
:param person_id: the personid associated with the appearances.
:param year: optional parameter to narrow the list by year (>=1983)
:returns: json object of a list of appearances for a performer.
    - see tests/data/get_appearances.json

### get_relationships
```python
PhishNetAPI.get_relationships(self, uid)
```

Returns an array of friends & fans from the /relationships/get endpoint.
:param uid: the uid associated with the relationship.
:returns: json object of a user's relationships. - see tests/data/get_relationships.json

### query_reviews
```python
PhishNetAPI.query_reviews(self, **kwargs)
```

Query user reviews from the /reviews/query endpoint.
:params **kwargs comprised of the following keys: showid, uid,
    posted_on, posted_after, posted_before.
:returns: json response object with a list of reviews.

### get_latest_setlist
```python
PhishNetAPI.get_latest_setlist(self)
```

Get an array with the most recent Phish setlist
:returns: json object of the latest setlist - see tests/data/latest_setlist.json

### get_setlist
```python
PhishNetAPI.get_setlist(self, showid=None, showdate=None)
```

Get an array with the Phish setlist that matches the showid or showdate.
If both parameters are passed in, showid takes precedence. If no params are
passed in then it returns the latest setlist.
:returns: json object of matching setlist - see tests/data/latest_setlist.json

### get_recent_setlists
```python
PhishNetAPI.get_recent_setlists(self)
```

Get an array with the 10 most recent Phish setlists
:returns: json object of the 10 most recent setlist - see tests/data/recent_setlists.json

### get_tiph_setlist
```python
PhishNetAPI.get_tiph_setlist(self)
```

Get an array with a random setlist from today's date (MM/DD) in Phish history
:returns: json object of the setlist - see tests/data/tiph_setlist.json

### get_random_setlist
```python
PhishNetAPI.get_random_setlist(self)
```

Get an array with a random setlist in Phish history
:returns: json object of the setlist - see tests/data/tiph_setlist.json

### get_in_progress_setlist
```python
PhishNetAPI.get_in_progress_setlist(self)
```

Get the Most Recent Setlist, Including in Progress.
:returns: json object of the setlist - see tests/data/tiph_setlist.json

### get_show_links
```python
PhishNetAPI.get_show_links(self, showid)
```

Get links associated with a show, including LivePhish links, Phish.net recaps, photos, and more.
:returns: json object of show links - see tests/data/get_show_links.json

### get_upcoming_shows
```python
PhishNetAPI.get_upcoming_shows(self)
```

Get an array of upcoming shows.
:returns: json object of upcoming shows - see tests/data/get_upcoming_shows.json

### query_shows
```python
PhishNetAPI.query_shows(self, **kwargs)
```

Query the show list via one or more parameters. If no paramters are fed,
returns error_code 3. Please note that you cannot send an argument of
"showdate" or "date" to this endpoint. If you know the showdate for which
you want details, please use get_setlist()

### get_user_details
```python
PhishNetAPI.get_user_details(self, uid)
```

Returns an array of publically available details about a user. Requires
an authkey from an authorized user of your application. See authorize().
:return: json response object with details for a registered phish.net user.

### get_all_venues
```python
PhishNetAPI.get_all_venues(self)
```

Returns an array of venues.
:return: json response object with all venues - see tests/data/all_venues.json.

### get_venue
```python
PhishNetAPI.get_venue(self, venueid)
```

returns an array of values, including geographical location about a single venue and,
if its an alias, the current name.
:return: json response object with the details abount a venue -- see tests/data/get_venue.json


### Methods requiring user authorization

Some protected methods additionally require an authkey to take actions on behalf of specific users.  This includes adding and removing a show to "My Shows". In order to make authorized API calls on 
behalf of a user, the user needs to be registered with phish.net and they need to go to 
https://phish.net/authorize?appid=<<your appid>>&uid=<<their UID>>. Your appid is available from 
https://api.phish.net/keys/

Once those attributes have been set, you can make user-authorized API calls.  For example, lets add, and then remove [11/30/1997](http://phish.net/setlists/?d=1997-11-30) to userid 80's list of shows.

``` python
>>> from phishnet_api_v3.api_client import PhishNetAPI
>>> api = PhishNetAPI()
>>> api.authorize(80)
>>> response = api.query_shows(year=1997, month=11, day=30)
>>> response['response']['data']['showid']
>>> response['response']['data'][0]['showid']
1252691618
>>> api.update_show_attendance(api.uid, showid=1252691618, update='add')
{"error_code": 0, "error_message": "Successfully added 1997-11-30", "response": {"count": 4, "data": {"action": "add", "showdate": "1997-11-30", "showid": 1252691618, "shows_seen": "140"}}}
>>> api.update_show_attendance(api.uid, showid=1252691618, update='remove')
{"error_code": 0, "error_message": "Successfully removed 1997-11-30", "response": {"count": 4, "data": {"action": "remove", "showdate": "1997-11-30", "showid": 1252691618, "shows_seen": "139"}}}
```

### authorize
```python
PhishNetAPI.authorize(self, uid, private_salt=None)
```

Authorize the current instance to be able to make privileged API calls on behalf of a selected user.
In order to use this method, The phish.net registered user must have gone to
https://phish.net/authorize?appid=X&uid=Y to authorize themselves with your app and allow you to get
thier authkey via the authority/get endpoint.

:param uid: The uid to authorize on behalf of.
:param private_salt: The private_salt associated with the apikey. If None, will check
environment variable (set either via the OS environment or .env file.)

