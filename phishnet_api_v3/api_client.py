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
from types import SimpleNamespace as Namespace
import arrow
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

    def __init__(self, api_key, base_url='https://api.phish.net/',
                 version=DEFAULT_VERSION, verify_ssl_certificate=True, timeout=60, log_level='WARNING'):
        """
        :param api_key: Your application's pre-assigned API key. This parameter is required for all public API
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

        self.api_key = api_key
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
        self.auth_key = None
        self.app_id = None

    def authorize(self, uid, private_salt):
        """
        Authorize the current instance to be able to make privileged API calls on behalf of a selected user. 
        In order to use this method, The phish.net registered user must have gone to 
        https://phish.net/authorize?appid=X&uid=Y to authorize themselves with your app and allow you to get 
        thier auth_key via the authority/get endpoint.

        :param uid: The uid to authorize on behalf of.
        :param private_salt: The private_salt associated with the api_key.
        """
        self.auth_key = self.get_auth_key(uid, private_salt)
        self.uid = uid

    def get_auth_key(self, uid, private_salt):
        """
        This method will handle negotiation of the authorization for a user.  
        :param uid: The uid to fetch the auth_key on behalf of.
        :param private_salt: The private_salt associated with the api_key.
        :returns the auth_key associated with the uid you will run api calls on.
        """
        if self.uid == uid and self.auth_key:
            return self.auth_key
        else:
            return self._authority_get(uid, private_salt)

    def _authority_get(self, uid, private_salt):
        """
        Retrieves the auth_key of a user who has already been authorized for your application.
        :param uid: The uid of the registered phish.net user you want to authorize
        :param private salt: The private salt associated with the api_key (see https://api.phish.net/keys)
        :return: The 19 digit hexadecimal authorization key for the user id passed in. On failure, or if the
            app is not authorized, the method will return 0.
        """
        self.uid = uid
        md5_str = private_salt + self.api_key + str(self.uid)
        unique_hash = hashlib.md5(md5_str.encode()).hexdigest()
        print('unique_hash: ' + unique_hash)
        params = {
            'api_key': self.api_key,
            'uid': uid,
            'unique_hash': unique_hash
        }
        endpoint = "authority/get"
        response = self.post(endpoint=endpoint, params=params)
        self.app_id = response['response']['data']['appid']
        print(response['response']['data'])
        return response['response']['data']['authkey']

    def get_recent_blogs(self):
        """
        Get a list of recently posted entries to the phish.net blog (last 15 entries).
        :return: json response object of recent blog entries - see tests/data/recent_blogs.json
        """
        return self.post(endpoint='blog/get')

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
        legal_params = ['month', 'day', 'year', 'username', 'uid']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError(
                'Invalid query params for blog/get, {}'.format(kwargs))

        if 'monthname' in kwargs:
            legal_month_names = ['january', 'february', 'march', 'april', 'may',
                                 'june', 'july', 'august', 'september', 'october', 'november', 'december']
            if not kwargs['monthname'] in legal_month_names:
                raise PhishNetAPIError(
                    'Invalid monthname: {}'.format(kwargs['monthname']))
        if 'year' in kwargs:
            current_year = date.today().year
            if not 2009 <= kwargs['year'] <= current_year:
                raise ValueError(
                    'Invalid year parameter (>=2009 and <= {}) for people/appearances: {}'.format(current_year, kwargs['year']))

        return self.post(endpoint='blog/get', params=kwargs)

    def get_all_artists(self):
        """
        The artists/all endpoint returns an array of artists whose setlists are tracked 
        in the Phish.net setlist database, along with the associated artistid.
        :return: json response object of all artists - see tests/data/all_artists.json
        """
        return self.post(endpoint='artists/all')

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

        if kwargs['showdate']:
            kwargs['showdate'] = self.parse_date(kwargs['showdate'])

        return self.post(endpoint='attendance/get', params=kwargs)

    @check_auth_key
    def update_show_attendance(self, show_id, update):
        """
        update your attendance to a specific show (add or remove) via the
        /attendance/add and /attendance/remove endpoints.
        :param show_id: the show id associated with the show you want to update
        :param update: either 'add' or 'remove'.
        :return: json response object with confirmation of attendance update 
            - see tests/data/add_attendance.json and remove_attendance.json
        """
        params = {'authkey': self.auth_key, 'showid': show_id, 'uid': self.uid}
        if update == 'add':
            return self.post(endpoint='attendance/add', params=params)
        elif update == 'remove':
            return self.post(endpoint='attendance/remove', params=params)
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
        params = kwargs.keys()
        legal_params = ['collectionid', 'uid', 'contains']

        if not len(params) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError(
                'Invalid query params for collections/query, {}'.format(kwargs))

        return self.post(endpoint='collections/query', params=kwargs)

    def get_collection(self, collection_id):
        """
        Get the details of a collection from the /collections/get endpoint.
        :param collection_id: the collectionid associated with the collection.
        :returns: json object of a collection detail. - see tests/data/get_collection.json
        """
        return self.post(endpoint='collections/get', params={'collectionid': collection_id})

    def get_all_jamcharts(self):
        """
        Get an array of songs that have jamcharts, song, songid, name, link, and number
        from the /jamcharts/all endpoint.
        :return: json response object of all jamcharts - see tests/data/all_jamcharts.json
        """
        return self.post(endpoint='jamcharts/all')

    def get_jamchart(self, song_id):
        """
        Get the details of a jamchart from the /jamcharts/get endpoint.
        :param song_id: the songid associated with the jamchart.
        :returns: json object of a jamchart detail. - see tests/data/get_jamchart.json
        """
        return self.post(endpoint='jamcharts/get', params={'songid': song_id})

    def get_all_people(self):
        """
        Get a list of personid, name, type, and a link to all shows in which a person is featured.
        :returns: json object of all people - see tests/data/all_people.json
        """
        return self.post(endpoint='people/all')

    def get_all_people_types(self):
        """
        Get a dict of all people types
        :returns: json object of all people types - see tests/data/all_people_types.json
        """
        return self.post(endpoint='people/get')

    def get_people_by_show(self, show_id):
        """
        Get list of performers at a show from the /people/byshow endpoint.
        :param show_id: the showid associated with the show.
        :returns: json object of a list of performers for a show. 
            - see tests/data/people_by_show.json
        """
        return self.post(endpoint='jamcharts/get', params={'songid': show_id})

    def get_appearances(self, person_id, year=None):
        """
        Get list of appearances for a particular performer from the /people/appearances endpoint.
        :param person_id: the personid associated with the appearances.
        :param year: optional parameter to narrow the list by year (>=1983)
        :returns: json object of a list of appearances for a performer. 
            - see tests/data/get_appearances.json
        """
        params = {'personid': person_id}
        if year is not None:
            current_year = date.today().year
            if 1983 <= year <= current_year:
                params['year'] = year
            else:
                raise ValueError(
                    'Invalid year parameter (>=1983 <= {}) for people/appearances: {}'.format(current_year, year))

        return self.post(endpoint='people/appearances', params=params)

    def get_relationships(self, uid):
        """
        Returns an array of friends & fans from the /relationships/get endpoint.
        :param uid: the uid associated with the relationship.
        :returns: json object of a user's relationships. - see tests/data/get_relationships.json
        """
        return self.post(endpoint='relationships/get', params={'uid': uid})

    def post(self, endpoint, params={}, retry=DEFAULT_RETRY):
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

    def _query(self, method, endpoint, params={}, retry=DEFAULT_RETRY):
        """
        :param method: HTTP method to query the API.  Typically for Phish.net only GET or POST. POST recommended.
        :param endpoint: The path to call.  The path is appended to the base URL.  
        :param data: A dictionary of HTTP GET parameters (for GET requests) or POST data (for POST requests).
        :param retry: An integer describing how many times the request may be retried.
        """
        url = self.base_url + endpoint
        try:
            return self._make_rest_call(method, url, params)
        except PhishNetAPIError:
            if retry:
                return self._query(method, endpoint, params, retry - 1)
            else:
                raise NumberRetriesExceeded(
                    "exceeded maximum retry count: {}".format(retry))

    @check_api_key
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

    @staticmethod
    def parse_date(d):
        if isinstance(d, date):
            return str(d)
        else:
            try:
                d = arrow.get(d).date()
            except arrow.parser.ParserError:
                raise ValueError(
                    'Showdate {} could not be parsed into a date. Use YYYY-MM-DD format.'.format(d))
            return str(d)
