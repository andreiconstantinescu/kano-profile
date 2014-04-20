#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
#from gi.repository import Gtk

from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir

import kano_profile_gui.swag.environment_table as environ_tab

img_width = 50


def activate(_win, _box):
    #_label.set_text('Swags')

    badges = {k: v for k, v in calculate_badges().iteritems() if k.startswith('swag_')}
    if not badges:
        return

    #num_categories = len(badges.keys())
    #max_items = max([len(v) for k, v in badges.iteritems()])

    ## Zsolt's code

    """    table = Gtk.Table(num_categories, max_items, False)
    _box.add(table)

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, item in enumerate(items):
            print i, j, group, item, items[item]

            img = Gtk.Image()
            if items[item]:
                img_path = get_image(item, group, img_width)
                img.set_from_file(img_path)
            else:
                img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

            table.attach(img, j, j + 1, i, i + 1)"""

    ##### My code ####

    environments = environ_tab.Table()
    _box.add(environments.table)

