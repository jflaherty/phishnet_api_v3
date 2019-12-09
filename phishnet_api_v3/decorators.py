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
                "{} requires an API key".format(_qual_name_safe(f)))
        return f(*args, **kwargs)
    return wrapper


def check_authorized_user(f):
    def wrapper(*args, **kwargs):
        if not args[0].auth_key:
            raise AuthError(
                "{} requires an auth_key".format(_qual_name_safe(f)))
        return f(*args, **kwargs)
    return wrapper


def _qual_name_safe(f):
    try:
        return f.__qualname__
    except AttributeError:  # Occurs when Python <= 3.3
        from qualname import qualname
        return qualname(f)
