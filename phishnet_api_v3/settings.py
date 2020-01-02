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

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

APIKEY = os.getenv("APIKEY")
APPID = os.getenv("APPID")
PRIVATE_SALT = os.getenv("PRIVATE_SALT")
