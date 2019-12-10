#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

from phishnet_api_v3.exceptions import AuthError


def check_api_key(f):
    def wrapper(*args, **kwargs):
        if not args[0].api_key:
            raise AuthError(
                "{} requires an API key".format(f.__qualname__))
        args[3]['apikey'] = args[0].api_key
        return f(*args, **kwargs)
    return wrapper


def check_auth_key(f):
    def wrapper(*args, **kwargs):
        if not args[0].auth_key and not args[0].uid == args[1]:
            raise AuthError(
                "{} requires an auth_key for {}".format(f.__qualname__, args[1]))
        return f(*args, **kwargs)
    return wrapper
