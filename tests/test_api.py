#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

import json

# local imports
from phishnet_api_v3.api_client import PhishNetAPI


class TestPhishnetAPI:

    def test_authorize(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/authority.json') as f:
            authority_json = json.load(f)
        requests_mock.post(api.base_url + "authority/get", json=authority_json)
        api.authorize(15, '123456789abcdefghij')
        assert api.uid == 15
        assert api.auth_key == "B6386A2485D94C73DAA"
        assert api.app_id == 12345

    def test_get_recent_blogs(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/recent_blogs.json') as f:
            recent_blogs_json = json.load(f)
        requests_mock.post(api.base_url + "blog/get", json=recent_blogs_json)
        recent_blogs_response = api.get_recent_blogs()
        assert recent_blogs_response['response']['count'] == 3
        assert len(recent_blogs_response['response']['data']) == 3
