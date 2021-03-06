#!/usr/bin/env python

# cache_functions.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from kano_profile.apps import load_app_state_variable, save_app_state_variable


def cache_data(category, value):
    if category in [
        "username",
        "email",
        "secondary_email",
        "birthday_day",
        "birthday_month",
        "birthday_year",
        "birthday_day_index",
        "birthday_month_index",
        "birthday_year_index",
        "marketing_enabled",
    ]:
        save_app_state_variable("kano-avatar-registration", category, value)


def get_cached_data(category):
    return load_app_state_variable("kano-avatar-registration", category)


def cache_birthday(day, month, year):
    cache_data("birthday_day", day)
    cache_data("birthday_month", month)
    cache_data("birthday_year", year)


def cache_emails(email, secondary_email="", email_user=False):
    cache_data("email", email)
    cache_data("secondary_email", secondary_email)
    cache_data("email_user", email_user)


def cache_all(email, secondary_email, username,
              birthday_day, birthday_month, birthday_year,
              marketing_enabled):
    cache_birthday(birthday_day, birthday_month, birthday_year)
    cache_data("email", email)
    cache_data("secondary_email", secondary_email)
    cache_data("username", username)
    cache_data("marketing_enabled", marketing_enabled)
