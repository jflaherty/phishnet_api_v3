#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>
#
# This version 3 of phish.net API client is heavily borrowed from and inspired by
# phishnetpy (https://github.com/jameserrico/phishnetpy) which was written for
# version 2 of the API.

from datetime import date
import urllib
from types import SimpleNamespace as Namespace
import requests
import hashlib
import calendar
import json
import logging

from pwd import *
from phishnet_api_v3.decorators import *
from phishnet_api_v3.exceptions import *


class PhishNetAPI(object):
    DEFAULT_VERSION = 'v3'
    DEFAULT_RETRY = 3

    def __init__(self, apikey, base_url='https://api.phish.net/',
                 version=DEFAULT_VERSION, verify_ssl_certificate=True, timeout=60, log_level='WARNING'):
        """
        :param apikey: Your application's pre-assigned API key. This parameter is required for all public API
            methods.
        :param base_url: The base URL to invoke API calls from.  Defaults the the standard phish.net API base.
        :param version: A string with the API version. This client targets version v3. If you do not pass this variable
            it will default to the current version of the API, which may yield unexpected results. The current version
            is 'v3'.
        :param verify_ssl_certificate: Typically this should be set to true, but remains as an optional parameter, in
            case there are ever future issues with the Phish.net SSL sertificate.  Setting this to False will allow
            requests to be made even if the SSL certificate is invalid.
        :param timeout: The maximum time (in seconds) that the API client should wait for a response before considering
            it to be a failure and moving on.  You may set this to None to disable this behavior altogether.
        :param log_level: one of the following logger.level levels - DEBUG, INFO, WARNING, ERROR, CRITICAL
        """

        self.apikey = apikey
        self.version = version
        self.format = format
        if not base_url.endswith('/'):
            self.base_url = base_url + '/' + self.version + '/'
        else:
            self.base_url = base_url + self.version + '/'

        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)
        logging.basicConfig(level=numeric_level)

        self.verify_ssl_certificate = verify_ssl_certificate
        self.timeout = timeout
        self.session = requests.session()
        self.uid = None
        self.authkey = None
        self.appid = None

    def authorize(self, uid, private_salt):
        """
        Authorize the current instance to be able to make privileged API calls on behalf of a selected user.
        In order to use this method, The phish.net registered user must have gone to
        https://phish.net/authorize?appid=X&uid=Y to authorize themselves with your app and allow you to get
        thier authkey via the authority/get endpoint.

        :param uid: The uid to authorize on behalf of.
        :param private_salt: The private_salt associated with the apikey.
        """
        self.authkey = self.get_authkey(uid, private_salt)
        self.uid = uid

    def get_authkey(self, uid, private_salt):
        """
        This method will handle negotiation of the authorization for a user.
        :param uid: The uid to fetch the authkey on behalf of.
        :param private_salt: The private_salt associated with the apikey.
        :returns the authkey associated with the uid you will run authorized 
            api calls on.
        """
        if self.uid == uid and self.authkey:
            return self.authkey
        else:
            return self._authority_get(uid, private_salt)

    def _authority_get(self, uid, private_salt):
        """
        Retrieves the authkey of a user who has already been authorized for your application.
        :param uid: The uid of the registered phish.net user you want to authorize
        :param private salt: The private salt associated with the apikey (see https://api.phish.net/keys)
        :return: The 19 digit hexadecimal authorization key for the user id passed in. On failure, or if the
            app is not authorized, the method will return 0.
        """
        self.uid = uid
        md5_str = private_salt + self.apikey + str(self.uid)
        unique_hash = hashlib.md5(md5_str.encode()).hexdigest()
        print('unique_hash: ' + unique_hash)
        params = {
            'apikey': self.apikey,
            'uid': uid,
            'unique_hash': unique_hash
        }
        endpoint = "authority/get"
        response = self.post(function='_authority_get',
                             endpoint=endpoint, params=params)
        self.appid = response['response']['data']['appid']
        print(response['response']['data'])
        return response['response']['data']['authkey']

    def get_recent_blogs(self):
        """
        Get a list of recently posted entries to the phish.net blog (last 15 entries).
        :return: json response object of recent blog entries - see tests/data/recent_blogs.json
        """
        return self.post(function='get_recent_blogs', endpoint='blog/get')

    def get_blogs(self, **kwargs):
        """
        Find all blogs that match the params below (maximum of 15 results)
        :param **kwargs. Made up of at least one of the the following keys:
            month: The month of the year as as integer
            day: The day of the month as as integer
            year: The year as as integer
            monthname: month of the year (i.e. January)
            username: The username of the author
            author: the uid of the author
        :return: json response object of blogs that match the query(see get_recent_blogs())
        """
        params = kwargs.keys()
        legal_params = ['month', 'day', 'year', 'monthname', 'username', 'uid']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise ParamValidationError(
                'Invalid query params for blog/get, {}'.format(kwargs))

        return self.post(function='get_blogs', endpoint='blog/get', params=kwargs)

    def get_all_artists(self):
        """
        The artists/all endpoint returns an array of artists whose setlists are tracked
        in the Phish.net setlist database, along with the associated artistid.
        :return: json response object of all artists - see tests/data/all_artists.json
        """
        return self.post(function='get_all_artists', endpoint='artists/all')

    def get_show_attendees(self, **kwargs):
        """
        Find all attendees for a specific show
        :param **kwargs: Made up of at least one of the the following keys:
            showid: the id for a specific show
            showdate: The date for a specific show
        :return: json response object of attendees for a specific show.
            - see tests/data/show_attendees.json
        """
        params = kwargs.keys()
        legal_params = ['showid', 'showdate']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError("show_id or show_date required")

        return self.post(function='V', endpoint='attendance/get', params=kwargs)

    @check_authkey
    def update_show_attendance(self, showid, update):
        """
        update your attendance to a specific show (add or remove) via the
        /attendance/add and /attendance/remove endpoints.
        :param show_id: the show id associated with the show you want to update
        :param update: either 'add' or 'remove'.
        :return: json response object with confirmation of attendance update
            - see tests/data/add_attendance.json and remove_attendance.json
        """
        params = {'authkey': self.authkey, 'showid': showid, 'uid': self.uid}
        if update == 'add':
            return self.post(function='update_show_attendance', endpoint='attendance/add', params=params)
        elif update == 'remove':
            return self.post(function='update_show_attendance',  endpoint='attendance/remove', params=params)
        else:
            raise PhishNetAPIError(
                'update_show_attendance param not valid: {}'.format(update))

    def query_collections(self, **kwargs):
        """
        Query user collections from the /collections/query endpoint.
        :params **kwargs comprised of the following keys: collectionid, uid, contains.
            contains is a comma separated string of showid's
        :returns: json response object with a list of collections.
        """
        return self.post(function='query_collections', endpoint='collections/query', params=kwargs)

    def get_collection(self, collectionid):
        """
        Get the details of a collection from the /collections/get endpoint.
        :param collection_id: the collectionid associated with the collection.
        :returns: json object of a collection detail. - see tests/data/get_collection.json
        """
        return self.post(function='get_collection', endpoint='collections/get', params={'collectionid': collectionid})

    def get_all_jamcharts(self):
        """
        Get an array of songs that have jamcharts, song, songid, name, link, and number
        from the /jamcharts/all endpoint.
        :return: json response object of all jamcharts - see tests/data/all_jamcharts.json
        """
        return self.post(function='get_all_jamcharts', endpoint='jamcharts/all')

    def get_jamchart(self, songid):
        """
        Get the details of a jamchart from the /jamcharts/get endpoint.
        :param song_id: the songid associated with the jamchart.
        :returns: json object of a jamchart detail. - see tests/data/get_jamchart.json
        """
        return self.post(function='get_jamchart', endpoint='jamcharts/get', params={'songid': songid})

    def get_all_people(self):
        """
        Get a list of personid, name, type, and a link to all shows in which a person is featured.
        :returns: json object of all people - see tests/data/all_people.json
        """
        return self.post(function='get_all_people', endpoint='people/all')

    def get_all_people_types(self):
        """
        Get a dict of all people types
        :returns: json object of all people types - see tests/data/all_people_types.json
        """
        return self.post(function='get_all_people_types', endpoint='people/get')

    def get_people_by_show(self, showid):
        """
        Get list of performers at a show from the /people/byshow endpoint.
        :param show_id: the showid associated with the show.
        :returns: json object of a list of performers for a show.
            - see tests/data/people_by_show.json
        """
        return self.post(function='get_people_by_show', endpoint='jamcharts/get', params={'songid': showid})

    def get_appearances(self, personid, year=None):
        """
        Get list of appearances for a particular performer from the /people/appearances endpoint.
        :param person_id: the personid associated with the appearances.
        :param year: optional parameter to narrow the list by year (>=1983)
        :returns: json object of a list of appearances for a performer.
            - see tests/data/get_appearances.json
        """
        params = {'personid': personid}
        if year is not None:
            params['year'] = year

        return self.post(function='get_appearances', endpoint='people/appearances', params=params)

    def get_relationships(self, uid):
        """
        Returns an array of friends & fans from the /relationships/get endpoint.
        :param uid: the uid associated with the relationship.
        :returns: json object of a user's relationships. - see tests/data/get_relationships.json
        """
        return self.post(function='get_relationships', endpoint='relationships/get', params={'uid': uid})

    def query_reviews(self, **kwargs):
        """
        Query user reviews from the /reviews/query endpoint.
        :params **kwargs comprised of the following keys: showid, uid,
            posted_on, posted_after, posted_before.
        :returns: json response object with a list of reviews.
        """
        params = kwargs.keys()
        legal_params = ['showid', 'uid',
                        'posted_on', 'posted_after', 'posted_before']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError(
                'Invalid query params for reviews/query, {}'.format(kwargs))

        return self.post(function='query_reviews', endpoint='reviews/query', params=kwargs)

    def get_latest_setlist(self):
        """
        Get an array with the most recent Phish setlist
        :returns: json object of the latest setlist - see tests/data/latest_setlist.json
        """
        return self.post(function='get_latest_setlist', endpoint='setlists/latest')

    def get_setlist(self, showid=None, showdate=None):
        """
        Get an array with the Phish setlist that matches the showid or showdate.
        If both parameters are passed in, showid takes precedence. If no params are
        passed in then it returns the latest setlist.
        :returns: json object of matching setlist - see tests/data/latest_setlist.json
        """
        if showid is not None:
            return self.post(function='get_setlist', endpoint='setlists/get', params={'showid': showid})
        elif showdate is not None:
            return self.post(function='get_setlist', endpoint='setlists/get', params={'showdate': showdate})
        else:
            return self.get_latest_setlist()

    def get_recent_setlists(self):
        """
        Get an array with the 10 most recent Phish setlists
        :returns: json object of the 10 most recent setlist - see tests/data/recent_setlists.json
        """
        return self.post(function='get_recent_setlists', endpoint='setlists/recent')

    def get_tiph_setlist(self):
        """
        Get an array with a random setlist from today's date (MM/DD) in Phish history
        :returns: json object of the setlist - see tests/data/tiph_setlist.json
        """
        return self.post(function='get_tiph_setlist', endpoint='setlists/tiph')

    def get_random_setlist(self):
        """
        Get an array with a random setlist in Phish history
        :returns: json object of the setlist - see tests/data/tiph_setlist.json
        """
        return self.post(function='get_random_setlist', endpoint='setlist/random')

    def get_in_progress_setlist(self):
        """
        Get the Most Recent Setlist, Including in Progress.
        :returns: json object of the setlist - see tests/data/tiph_setlist.json
        """
        return self.post(function='get_in_progress_setlist', endpoint='setlists/progress')

    def get_show_links(self, showid):
        """
        Get links associated with a show, including LivePhish links, Phish.net recaps, photos, and more.
        :returns: json object of show links - see tests/data/get_show_links.json
        """
        return self.post(function='get_show_links', endpoint='shows/links', params={'showid': showid})

    def get_upcoming_shows(self):
        """
        Get an array of upcoming shows.
        :returns: json object of upcoming shows - see tests/data/get_upcoming_shows.json
        """
        return self.post(function='get_upcoming_shows', endpoint='shows/upcoming')

    def query_shows(self, **kwargs):
        """
        Query the show list via one or more parameters. If no paramters are fed, 
        returns error_code 3. Please note that you cannot send an argument of 
        "showdate" or "date" to this endpoint. If you know the showdate for which 
        you want details, please use get_setlist()
        """
        params = kwargs.keys()
        legal_params = ['showids', 'year', 'month', 'day', 'venueid',
                        'tourid', 'country', 'city', 'state', 'limit', 'order'
                        'showdate_gt', 'showdate_gte', 'showdate_lt', 'showdate_lte',
                        'showyear_gt', 'showyear_gte', 'showyear_lt', 'showyear_lte']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError(
                'Invalid query params for reviews/query, {}'.format(kwargs))

        for field in ['country', 'city', 'state']:
            if field in params:
                kwargs[field] = urllib.urlencode(kwargs[field])

        return self.post(function='query_shows', endpoint='shows/query', params=kwargs)

    @check_authkey
    def get_user_details(self):
        """
        Returns an array of publically available details about a user. Requires
        an authkey from an authorized user of your application. See authorize().
        :return: json response object with confirmation of attendance update
            - see tests/data/get_user.json
        """
        params = {'authkey': self.authkey, 'uid': self.uid}
        return self.post(function='get_user_details', endpoint='user/get', params=params)

    def get_all_venues(self):
        """
        Returns an array of venues. 
        :return: json response object with all venues - see tests/data/all_venues.json.
        """
        return self.post(function='get_all_venues', endpoint='venues/all')

    def get_venue(self, venueid):
        """
        returns an array of values, including geographical location about a single venue and, 
        if its an alias, the current name.
        :return: json response object with the details abount a venue -- see tests/data/get_venue.json
        """
        return self.post(function='get_venue', endpoint='venues/get', params={'venueid': venueid})

    @validate_params
    def post(self, function, endpoint, params=None, retry=DEFAULT_RETRY):
        """
        Get an item from the Phish.net API.
        :param endpoint: The REST endpoint to call. The endpoint is appended to the base URL.  
        :param retry: An integer describing how many times the request may be retried.
        :param params: A dictionary of HTTP POST data.
        """
        response = self._query('POST', endpoint, params, retry)
        # response_obj = json.loads(
        #    response.text, object_hook=lambda d: Namespace(**d))
        if(response.json()['error_code'] > 0):
            raise PhishNetAPIError(
                'phish.net API error: {}'.format(endpoint, response.json()['error_code'], response.json()['error_message']))

        return response.json()

    def _query(self, method, endpoint, params=None, retry=DEFAULT_RETRY):
        """
        :param method: HTTP method to query the API.  Typically for Phish.net only GET or POST. POST recommended.
        :param endpoint: The path to call.  The path is appended to the base URL.  
        :param data: A dictionary of HTTP GET parameters (for GET requests) or POST data (for POST requests).
        :param retry: An integer describing how many times the request may be retried.
        """
        url = self.base_url + endpoint
        params = {} if params is None else params
        try:
            return self._make_rest_call(method, url, params)
        except PhishNetAPIError:
            if retry:
                return self._query(method, endpoint, params, retry - 1)
            else:
                raise NumberRetriesExceeded(
                    "exceeded maximum retry count: {}".format(retry))

    @check_apikey
    def _make_rest_call(self, method, url, data):
        try:
            if method == 'GET':
                response = self.session.get(
                    url, params=data, allow_redirects=True,
                    verify=self.verify_ssl_certificate, timeout=self.timeout)

            elif method == 'POST':
                response = self.session.post(
                    url, data=data, verify=self.verify_ssl_certificate, timeout=self.timeout)
            else:
                raise NotImplementedError(
                    "Phish.net API only supports HTTP GET or POST.")

            if not response:
                raise PhishNetAPIError(
                    'Unable to retrieve HTTP response from: {}'.format(url))

            if not response.ok or not response.status_code == 200:
                raise PhishNetAPIError(
                    'Phish.net API error occurred: {}'.format(
                        response.status_code, response.reason, url, data))

        except requests.RequestException as exception:
            raise HTTPError(exception)

        return response
