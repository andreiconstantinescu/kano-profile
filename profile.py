#!/usr/bin/env python

# kano.profile
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
import os
import grp
import json
import kano.utils as ku

__version__ = '0.1'


# kanoprofile functions


def load_profile():
    if not os.path.exists(profile_file):
        data = dict()
    else:
        try:
            data = json.loads(ku.read_file_contents(profile_file))
        except Exception:
            data = dict()

    if 'username_linux' not in data:
        data['username_linux'] = linux_user

    if 'email' not in data and get_email_from_disk():
        data['email'] = get_email_from_disk()

    if 'device_id' not in data and ku.get_device_id():
        data['device_id'] = ku.get_device_id()

    if 'mac_addr' not in data and ku.get_mac_address():
        data['mac_addr'] = ku.get_mac_address()

    return data


def save_profile(data):
    data['last_save_date'] = ku.get_date_now()
    data['last_save_version'] = __version__
    with open(profile_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def get_email_from_disk():
    kano_email_file = os.path.join(home_directory, '.useremail')
    return ku.read_file_contents(kano_email_file)


def get_app_dir(app_name):
    app_dir = os.path.join(apps_dir, app_name)
    ku.ensuredir(app_dir)
    return app_dir


def get_app_data_dir(app_name):
    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    ku.ensuredir(app_data_dir)
    return app_data_dir


def get_app_state_file(app_name):
    app_state_str = 'state.json'
    app_state_file = os.path.join(get_app_dir(app_name), app_state_str)
    return app_state_file


def load_app_state(app_name):
    app_state_file = get_app_state_file(app_name)

    if not os.path.exists(app_state_file):
        data = dict()
    else:
        try:
            data = json.loads(ku.read_file_contents(app_state_file))
        except Exception:
            data = dict()

    return data


def load_app_state_variable(app_name, variable):
    data = load_app_state(app_name)
    if variable in data:
        return data[variable]


def save_app_state(app_name, data):
    app_state_file = get_app_state_file(app_name)

    data['last_save_date'] = ku.get_date_now()
    with open(app_state_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def save_app_state_variable(app_name, variable, value):
    data = load_app_state(app_name)
    data[variable] = value
    save_app_state(app_name, data)


def calculate_xp():
    try:
        allrules = json.loads(ku.read_file_contents(rules_file))
    except Exception:
        print "Problem with opening the rules file!"
        return 0

    points = 0

    for app, groups in allrules.iteritems():
        appstate = load_app_state(app)

        if not appstate:
            continue

        for group, rules in groups.iteritems():

            # calculating points based on level
            if group == 'level':
                maxlevel = int(appstate['level'])

                for level, value in rules.iteritems():
                    level = int(level)
                    value = int(value)

                    if level <= maxlevel:
                        points += value

            # calculating points based on multipliers
            if group == 'multipliers':
                for thing, value in rules.iteritems():
                    value = float(value)
                    if thing in appstate:
                        points += value * appstate[thing]

    return points


def get_gamestate_variables(app_name):
    try:
        allrules = json.loads(ku.read_file_contents(rules_file))
    except Exception:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]


# start
if __name__ == "__main__":
    sys.exit("Should be imported as module")

# checking kanousers group
try:
    kanogrp = grp.getgrnam('kanousers')
    kanomembers = kanogrp.gr_mem
except KeyError:
    sys.exit("kanousers group doesn't exist\nrun 'groupadd kanousers' first")

# getting linux variables
linux_user = ku.get_user_environ()
home_directory = ku.get_home_by_username(linux_user)
module_file = os.path.realpath(__file__)
module_dir = os.path.dirname(module_file)

# check if run under kanouser (or sudo-ed kanouser)
if linux_user not in kanomembers:
    sys.exit("You are not member of kanousers group\nrun `usermod -a -G kanousers {}` first".format(linux_user))

# constructing paths of directories, files
kanoprofile_dir_str = '.kanoprofile'
kanoprofile_dir = os.path.join(home_directory, kanoprofile_dir_str)

profile_dir_str = 'profile'
profile_dir = os.path.join(kanoprofile_dir, profile_dir_str)

apps_dir_str = 'apps'
apps_dir = os.path.join(kanoprofile_dir, apps_dir_str)

profile_file_str = 'profile.json'
profile_file = os.path.join(profile_dir, profile_file_str)

rules_file_str = '/usr/share/kano-profile/rules.json'
rules_file = os.path.join(module_dir, rules_file_str)

# initializing profile
profile = load_profile()

if not os.path.exists(profile_file):
    ku.ensuredir(profile_dir)
    save_profile(profile)


