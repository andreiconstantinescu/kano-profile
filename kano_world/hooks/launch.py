#!/usr/bin/env python

# launch.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# args is an array of arguments that were passed through the URL
# e.g., kano:launch:make-art, it will be ["make-art"]

import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.utils import run_cmd


def run(args):
    try:
        appName = args[0]

        if (appName == 'make-art'):
            appName = 'kano-draw'

        if (appName == 'make-snake'):
            appName = 'kano-launcher \"rxvt -title \\\"Make Snake\\\" -e python /usr/share/make-snake'

        if (appName == 'terminal-quest'):
            appName = 'linux-story-gui'

    except Exception:
        return

    return appName


def launch(appName):

    run_cmd(appName)
