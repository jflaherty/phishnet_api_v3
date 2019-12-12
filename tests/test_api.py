#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

import json
import pytest

# local imports
from phishnet_api_v3.api_client import PhishNetAPI
from phishnet_api_v3 import __version__


def test_version():
    assert __version__ == '0.1.0'


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

    def test_get_blogs(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/recent_blogs.json') as f:
            get_blogs_json = json.load(f)
        requests_mock.post(api.base_url + "blog/get", json=get_blogs_json)
        get_blogs_response = api.get_blogs(year=2009)
        assert get_blogs_response['response']['count'] == 3
        assert len(get_blogs_response['response']['data']) == 3
        with pytest.raises(ValueError):
            api.get_blogs(year=2008)
            api.get_blogs(year=2020)

    def test_get_all_artists(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_artists.json') as f:
            all_artists_json = json.load(f)
        requests_mock.post(api.base_url + "artists/all", json=all_artists_json)
        all_artists_response = api.get_all_artists()
        assert all_artists_response['response']['count'] == 5
        assert len(all_artists_response['response']['data']) == 5
        assert all_artists_response['response']['data']['1']['artistid'] == 1

    def test_get_show_attendees(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/show_attendees.json') as f:
            show_attendees_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/get",
                           json=show_attendees_json)
        show_attendees_response = api.get_show_attendees(showdate='1991-07-19')
        assert show_attendees_response['response']['count'] == 53
        assert len(show_attendees_response['response']['data']) == 53
        with pytest.raises(ValueError):
            api.get_show_attendees(showdate='1991-13-19')
            api.get_show_attendees(showdate='1982-12-19')

    def test_update_show_attendance(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        api.auth_key = 'B6386A2485D94C73DAA'
        api_uid = 15
        with open('tests/data/add_attendance.json') as f:
            add_attendance_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/add",
                           json=add_attendance_json)
        update_attendance_response = api.update_show_attendance(
            1252691618, 'add')
        assert update_attendance_response['error_message'] == "Successfully added 1997-11-30"
        assert update_attendance_response['response']['data']['action'] == 'add'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618
        shows_seen = update_attendance_response['response']['data']['shows_seen']
        assert shows_seen == '63'

        with open('tests/data/remove_attendance.json') as f:
            remove_attendance_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/remove",
                           json=remove_attendance_json)
        update_attendance_response = api.update_show_attendance(
            1252691618, 'remove')
        assert update_attendance_response['error_message'] == "Successfully removed 1997-11-30"
        assert update_attendance_response['response']['data']['action'] == 'remove'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618
        assert update_attendance_response['response']['data']['shows_seen'] == str(
            int(shows_seen) - 1)

    def test_query_collections(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/query_collection.json') as f:
            query_collection_json = json.load(f)
        requests_mock.post(api.base_url + "collections/query",
                           json=query_collection_json)
        query_collections_response = api.query_collections(uid=1)
        assert query_collections_response['response']['count'] == 7
        assert len(query_collections_response['response']['data']) == 7
        assert query_collections_response['response']['data'][0]['count'] == 2

    def test_get_collection(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_collection.json') as f:
            get_collection_json = json.load(f)
        requests_mock.post(api.base_url + "collections/get",
                           json=get_collection_json)
        get_collection_response = api.get_collection(1294148902)
        assert get_collection_response['response']['data']['show_count'] == 7
        assert len(
            get_collection_response['response']['data']['shows']) == 7

    def test_get_all_jamcharts(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_jamcharts.json') as f:
            all_jamcharts_json = json.load(f)
        requests_mock.post(api.base_url + "jamcharts/all",
                           json=all_jamcharts_json)
        all_jamcharts_response = api.get_all_jamcharts()
        assert all_jamcharts_response['response']['count'] == 5
        assert len(all_jamcharts_response['response']['data']) == 5
        assert all_jamcharts_response['response']['data'][0]['songid'] == '2'

    def test_get_jamchart(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_jamchart.json') as f:
            get_jamchart_json = json.load(f)
        requests_mock.post(api.base_url + "jamcharts/get",
                           json=get_jamchart_json)
        get_jamchart_response = api.get_jamchart(7)
        assert get_jamchart_response['response']['data']['songid'] == 7
        assert len(
            get_jamchart_response['response']['data']['entries']) == 7

    def test_get_all_people(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_people.json') as f:
            all_people_json = json.load(f)
        requests_mock.post(api.base_url + "people/all",
                           json=all_people_json)
        all_people_response = api.get_all_people()
        assert all_people_response['response']['count'] == 12
        assert len(all_people_response['response']['data']) == 12
        assert all_people_response['response']['data'][0]['personid'] == 5710

    def test_get_all_people_types(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_people_types.json') as f:
            all_people_types_json = json.load(f)
        requests_mock.post(api.base_url + "people/get",
                           json=all_people_types_json)
        all_people_types_response = api.get_all_people_types()
        assert all_people_types_response['response']['count'] == 9
        assert len(all_people_types_response['response']['data'].keys()) == 9
        assert all_people_types_response['response']['data']["1"] == "The Band"

    def test_get_appearances(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_appearances.json') as f:
            get_appearances_json = json.load(f)
        requests_mock.post(api.base_url + "people/appearances",
                           json=get_appearances_json)
        get_appearances_response = api.get_appearances(79)
        assert get_appearances_response['response']['count'] == 1
        assert len(get_appearances_response['response']['data']) == 1
        assert get_appearances_response['response']['data'][0]['personid'] == 79
        with pytest.raises(ValueError):
            api.get_appearances(79, 1982)

    def test_get_relationships(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_relationships.json') as f:
            get_relationships_json = json.load(f)
        requests_mock.post(api.base_url + "relationships/get",
                           json=get_relationships_json)
        all_people_types_response = api.get_relationships(1)
        assert all_people_types_response['response']['count'] == 2
        assert len(all_people_types_response['response']['data'].keys()) == 2
        assert all_people_types_response['response']['data']["friends"].keys == 13
        assert all_people_types_response['response']['data']["fans"].keys == 13
