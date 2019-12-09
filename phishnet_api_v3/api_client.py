#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>
#
# This version 3 of phish.net API client is heavily borrowed from and inspired by phishnetpy (https://github.com/jameserrico/phishnetpy)
# which was written for version 2 of the API.

from datetime import date
from types import SimpleNamespace as Namespace
import arrow
import requests
import hashlib
import calendar
import json
import logging

from phishnet_api_v3.exceptions import *
from phishnet_api_v3.decorators import *


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

    @check_api_key
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
        :return: API response object of recent blog entries:
            {
                "error_code": 0,
                "error_message": null,
                "response": {
                    "count": 15,
                    "data": [
                        {
                            "pubdate": "2018-11-14 9:58 am",
                            "title": "Fall Tour 2018 -- HF Pod Recap!",
                            "url": "http://phish.net/blog/1542207505/fall-tour-2018-hf-pod-recap",
                            "teaser": "<p><img  src=\"http://smedia.pnet-static.com/img/IMG_8193.jpg\" style=\"width: 500px; height: 375px;\" /></p>\r\n\r\n<p>Although it only lasted just over two weeks, this Fall Tour was a doozy. We have come to outlive our brains, maybe? We have plenty to talk about, including the Hampton Simple vs. Hampton Golden Age, the lyrical improvements of this tour, the secretive nature of the Kasvot Voxt set and Kuroda&#39;s continuing magic. </p>",
                            "author": "swittersdc",
                            "profile": "http://phish.net/user/swittersdc",
                            "category": "Text",
                            "shorturl": "http://phi.sh/b/5bec3811",
                            "attachment": ""
                        },
                        {
                            ...
                        },
                        ...
                    ]
                }
            }
        """
        return self.post(endpoint='blog/get')

    def query_blogs(self, **kwargs):
        """
        Find all blogs that match the query fields below (maximum of 15 results)
        :param **kwargs. Made up of at least one of the the following keys:
            month: The month of the year as as integer
            day: The day of the month as as integer
            year: The year as as integer
            monthname: month of the year (i.e. January)
            username: The username of the author
            author: the uid of the author
        :return: API response object (see get_recent_blogs())
        """
        params = kwargs.keys
        legal_params = ['month', 'day', 'year', 'username', 'uid']

        if not len(params.keys) > 0 and not set(params).issubset(set(legal_params)):
            raise PhishNetAPIError(
                'Invalid query params for blog/get, {}'.format(kwargs))

        if 'monthname' in kwargs:
            legal_month_names = list(calendar.month_name)
            if not kwargs['monthname'] in legal_month_names:
                raise PhishNetAPIError(
                    'Invalid monthname: {}'.format(kwargs['monthname']))
        return self.post(endpoint='blog/get', params=kwargs)

    @check_api_key
    def post(self, endpoint, params={}, retry=DEFAULT_RETRY):
        """
        Get an item from the Phish.net API.
        :param endpoint: The REST endpoint to call.  The endpoint is appended to the base URL.  
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

    @check_api_key
    def _query(self, method, endpoint, params={}, retry=DEFAULT_RETRY):
        """
        :param method: HTTP method to query the API.  Typically for Phish.net only GET or POST. POST recommended.
        :param endpoint: The path to call.  The path is appended to the base URL.  
        :param data: A dictionary of HTTP GET parameters (for GET requests) or POST data (for POST requests).
        :param retry: An integer describing how many times the request may be retried.
        """

        url = self.base_url + endpoint
        paams = params or {}
        params['apikey'] = self.api_key

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
                response = self.session.request(
                    method, url, params=data, allow_redirects=True,
                    verify=self.verify_ssl_certificate, timeout=self.timeout)

            elif method == 'POST':
                response = self.session.request(
                    method, url, params=data, verify=self.verify_ssl_certificate, timeout=self.timeout)
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
            return d
        else:
            try:
                d = arrow.get(d).date()
            except arrow.parser.ParserError:
                raise ValueError(
                    'Showdate {} could not be parsed into a date. Use YYYY-MM-DD format.'.format(d))
            return d
