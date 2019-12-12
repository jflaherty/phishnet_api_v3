#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>


class AuthError(Exception):
    pass


class HTTPError(Exception):
    pass


class PhishNetAPIError(Exception):
    pass


class NumberRetriesExceeded(Exception):
    pass


class ParamValidationError(Exception):
    pass
