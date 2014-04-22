#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the table from which you can select backgrounds and avatars.


from gi.repository import Gtk
import selection_picture as pic


class Table():
    def __init__(self, subfolder, info):
        self.width = 690
        self.height = 540

        #self.pictures = []
        #for item in info:
        #    self.pictures.append(item["name"])
        #self.info = info

        self.info = info
        self.number_of_columns = 3
        self.number_of_rows = 3

        self.buttons = []
        self.pics = []

        for x in self.info:
            picture = pic.Picture(subfolder, x)
            self.pics.append(picture)

        # Attach to table
        index = 0
        row = 0

        # Create table from number of rows and columns - preferably dynamically
        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns)

        while index < (self.number_of_rows * self.number_of_columns):
            for j in range(self.number_of_columns):
                if index < len(self.info):
                    self.table.attach(self.pics[index].button, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                else:
                    emptybox = Gtk.EventBox()
                    if index % 2 == 0:
                        emptybox.get_style_context().add_class("black")
                    else:
                        emptybox.get_style_context().add_class("white")
                    emptybox.set_size_request(230, 180)
                    self.table.attach(emptybox, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                index += 1

            row += 1

        # Read config file/ JSON and find equipped picture.  Default to first one
        self.set_equipped(self.pics[0])

    def equip(self, widget1=None, event=None, pic=None):
        self.set_equipped(pic)

    def set_equipped(self, pic=None):
        if pic is not None:
            self.equipped = pic
            pic.set_equipped(True)
            self.set_equipped_style()
            return

        for pic in self.pics:
            if pic.get_equipped():
                self.equipped = pic
                self.set_equipped_style()
                return

        self.equipped = None
        self.set_equipped_style()

    def get_equipped(self):
        return self.equipped

    def set_equipped_style(self):
        for pic in self.pics:
            pic.remove_equipped_style()
            pic.set_equipped(False)

        if self.equipped is not None:
            self.equipped.add_equipped_style()
            self.equipped.set_equipped(True)

    def hide_labels(self):
        for pic in self.pics:
            if not pic.get_equipped():
                pic.hover_box.set_visible_window(False)
                pic.hover_label.set_visible(False)
                pic.equipped_box.set_visible_window(False)
                pic.equipped_label.set_visible(False)

