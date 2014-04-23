#!/usr/bin/env python

# info_text.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Info display next to image on selected screen

from gi.repository import Gtk


class Info():
    def __init__(self, width, height, heading, info, equip):

        self.heading = Gtk.Label(heading)
        self.heading.get_style_context().add_class("info_heading")
        self.heading.set_alignment(xalign=0, yalign=0)
        self.paragraph = Gtk.TextView()
        self.paragraph.set_editable(False)
        self.paragraph.get_buffer().set_text(info)
        self.paragraph.get_style_context().add_class("info_paragraph")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.pack_start(self.heading, False, False, 5)
        self.box.pack_start(self.paragraph, False, False, 30)
        self.box.set_size_request(width, height)

        self.back_button = Gtk.Button("BACK")
        self.back_button.get_style_context().add_class("green_button")
        self.back_button_box = Gtk.Box()
        self.back_button_box.add(self.back_button)
        # TODO: don't check heading, pass another variable we can check for
        # add equip button
        if equip:
            self.equip_button = Gtk.Button("EQUIP")
            self.equip_button.get_style_context().add_class("green_button")
            self.equip_button_box = Gtk.Box()
            self.equip_button_box.add(self.equip_button)
            self.box.pack_start(self.equip_button_box, False, False, 3)

        self.box.pack_start(self.back_button_box, False, False, 3)

        self.align = Gtk.Alignment(xalign=0, yalign=0)
        self.align.set_padding(20, 20, 20, 20)
        self.align.add(self.box)

        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("info_description_box")
        self.background.add(self.align)
