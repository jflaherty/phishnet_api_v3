# This file is part of phishnet-api-v3.
# https://github.com/jflaherty/phishnet-api-v3

# Licensed under the GPL v3 license:
# http://www.opensource.org/licenses/GPL v3-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

from datetime import date
from phishnet_api_v3.exceptions import ParamValidationError


def validate(*args, **kwargs):
    function = kwargs['function']
    endpoint = kwargs['endpoint']
    params = kwargs['params']
    for field in params:
        if field == 'monthname':
            _validate_monthname(function, params[field])
        if field == 'year':
            _validate_year(function, params[field])
        if field == 'month':
            _validate_month(function, params[field])
        if field == 'day':
            _validate_day(function, params[field])
        if field in ['showdate', 'showdate_gt', 'showdate_gte', 'showdate_lt',
                     'showdate_lte', 'posted_on', 'posted_after', 'posted_before']:
            _validate_date(function, field, params[field])
        if field in ['showid', 'uid', 'tourid', 'venueid', 'limit', 'collectionid', 'songid', 'limit']:
            _validate_number(function, field, params[field])
        if field in ['contains', 'showids']:
            _validate_showids(function, field, params[field])


def _validate_monthname(function, monthname):
    legal_month_names = ['january', 'february', 'march', 'april', 'may',
                         'june', 'july', 'august', 'september', 'october', 'november', 'december']
    if not monthname in legal_month_names:
        raise ParamValidationError(
            'Invalid monthname parameter: {} for {}'.format(monthname, function))


def _validate_year(function, year):
    current_year = date.today().year
    if function == "get_blogs":
        start_year = 2009
    else:
        start_year = 1983
    if not start_year <= year <= current_year:
        raise ParamValidationError(
            'Invalid year parameter (must be >= {} and <= {}) for {}: {}'.format(start_year, current_year, function, year))


def _validate_month(function, month):
    if not 1 <= month <= 12:
        raise ParamValidationError(
            'Invalid month parameter (must be >= 1 and <= 12) for {}: {}'.format(function, month))


def _validate_day(function, day):
    if not 1 <= day <= 31:
        raise ParamValidationError(
            'Invalid day parameter (must be >= 1 and <= 31) for {}: {}'.format(function, day))


def _validate_date(function, field, d):
    try:
        d = date.fromisoformat(str(d))
    except ValueError:
        raise ParamValidationError(
            '{} string {} could not be parsed into a valid date for {}. Use YYYY-MM-DD format.'.format(field, d, function))


def _validate_number(function, field, n):
    try:
        val = int(n)
    except ValueError:
        raise ParamValidationError(
            '{} string {} is not a valid number for {}. use a positive integer.'.format(field, n, function))


def _validate_showids(function, field, contains):
    contains_list = contains.split(',')
    for showid in contains_list:
        try:
            _validate_number(function, field, showid)
        except ParamValidationError:
            raise ParamValidationError(
                '{} parameter {} does not contain a comma separated list of showids {}.'.format(field, contains, function))
