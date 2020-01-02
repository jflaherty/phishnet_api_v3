#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

from phishnet_api_v3.exceptions import AuthError
from phishnet_api_v3.validators import validate


def check_apikey(f):
    def wrapper(*args, **kwargs):
        if not args[0].apikey:
            raise AuthError(
                "{} requires an API key".format(f.__qualname__))
        args[3]['apikey'] = args[0].apikey
        return f(*args, **kwargs)
    return wrapper


def check_authkey(f):
    def wrapper(*args, **kwargs):
        if not args[0].authkey and not args[0].uid == args[1]:
            args[0].authorize(args[1])
        return f(*args, **kwargs)
    return wrapper


def validate_params(f):
    def wrapper(*args, **kwargs):
        if 'params' in kwargs.keys():
            validate(*args, **kwargs)
        return f(*args, **kwargs)
    return wrapper
