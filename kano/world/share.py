#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from .connection import request_wrapper, content_type_json
from .functions import get_glob_session


def list_shares(app_name=None, page=0, featured=False):
    payload = {
        'app_name': app_name,
        'page': page,
        'featured': int(featured),
        'limit': 10
    }

    success, text, data = request_wrapper('get', '/share', headers=content_type_json, params=payload)
    if not success:
        return success, text, None

    if 'entries' in data and data['entries']:
        return True, None, data

    return False, 'Something wrong with getting workspaces!', None


def upload_share():
    glob_session = get_glob_session()
    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.upload_share('readme.xml', 'title2', 'app_name3')
