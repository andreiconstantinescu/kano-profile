#!/usr/bin/env python

# PopUpItemMenu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject
from kano_profile.badges import calculate_badges
from kano_avatar_gui.SelectMenu import SelectMenu
from kano.logging import logger
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.scrolled_window import ScrolledWindow


class PopUpItemMenu(SelectMenu):
    '''This creates the pop out menu showing each of the items.
    '''

    __gsignals__ = {
        'pop_up_item_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, category, avatar_parser):
        logger.debug("Initialising pop up menu with category {}".format(category))

        self.top_bar_height = 50

        # Size of the selected icon
        self.button_width = 42
        self.button_height = 42

        self._category = category
        self._parser = avatar_parser
        self._signal_name = 'pop_up_item_selected'
        self._border_path = self._parser.get_selected_border(self._category)

        obj_names = self._parser.get_avail_objs(self._category)
        SelectMenu.__init__(self, obj_names, self._signal_name)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Grid which the buttons are packed into
        self._grid = Gtk.Grid()

        # pack the grid into a sw of a specified height
        sw = ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.apply_styling_to_widget()
        sw.add(self._grid)
        sw.set_size_request(-1, 290)

        # Labels the category
        top_bar = self._create_top_bar()
        vbox.pack_start(top_bar, False, False, 0)
        vbox.pack_start(sw, False, False, 10)

        self._pack_items()
        self.show_all()

    def _create_top_bar(self):
        top_bar = Gtk.EventBox()
        top_bar.get_style_context().add_class("pop_up_menu_top_bar")
        label = Gtk.Label(self._category)
        label.set_alignment(0, 0.5)
        label.set_margin_left(20)
        top_bar.add(label)
        top_bar.set_size_request(-1, self.top_bar_height)
        return top_bar

    def _pack_items(self):
        '''Pack the buttons into the menu.
        '''

        # Assume the list of buttons are in self._buttons
        # Pack buttons into a grid

        # There are 2 columns and 5 rows.
        total_rows = 5

        # These are the counters to keep track of where we are
        # in the grid.
        row = 0
        column = 0

        obj_names = self._parser.get_avail_objs(self._category)
        logger.debug("PopUpMenu packing items = {}".format(obj_names))

        for name in obj_names:
            button = self._create_button(name)
            self._add_option_to_items(name, 'button', button)

            self._grid.attach(button, column, row, 1, 1)
            row += 1

            if row % total_rows == 0:
                row = 0
                column += 1

            # For now, we assume that none of the menus with
            # need more than 2 columns

        self._grid.set_margin_top(6)
        self._grid.set_margin_bottom(6)
        self._grid.set_margin_left(6)
        self._grid.set_margin_right(6)

    def _create_button(self, obj_name):
        '''This places the image onto a Gtk.Fixed so we can overlay a padlock
        on top (if the item is locked)
        This is then put onto a Gtk.Button with the appropriate CSS class.
        Returns the button.

        Hopefully this can be simplified with new assets
        '''

        # Create the container for the thumbnails
        fixed = Gtk.Fixed()

        path = self._parser.get_item_preview(obj_name)
        icon = Gtk.Image.new_from_file(path)

        # preview icon size (for all assets but the environment) is 41 by 41,
        # while the border is 42 by 42
        fixed.put(icon, 1, 1)

        button = Gtk.Button()
        button.get_style_context().add_class('pop_up_menu_item')
        button.add(fixed)
        button.connect('clicked', self._on_clicking_item, obj_name)
        button.connect('enter-notify-event', self._add_selected_appearence,
                       obj_name)
        button.connect('leave-notify-event', self._remove_selected_appearence,
                       obj_name)
        button.set_size_request(self.button_width, self.button_height)
        attach_cursor_events(button)

        # set a margin all the way around it
        button.set_margin_right(6)
        button.set_margin_left(6)
        button.set_margin_bottom(6)
        button.set_margin_top(6)

        return button

    def _add_selected_appearence(self, button, event, identifier):
        logger.debug("hit _add_selected_appearence")
        if identifier != self.get_selected():
            self._add_selected_border(button, identifier)

    def _remove_selected_appearence(self, button, event, identifier):
        if identifier != self.get_selected():
            self._remove_selected_border(button, identifier)

    def _add_selected_border(self, button, identifier):
        '''Add the border image on top of the image
        It needs to be "above" as some of the border images also
        have a white tick.
        '''
        logger.debug("_add_selected_border")
        if identifier in self._items:
            # Get the fixed containing the image
            fixed = button.get_child()

            # The border_path depends on the image.
            selected_border = Gtk.Image.new_from_file(self._border_path)

            # Put the selected border on the button
            fixed.put(selected_border, 0, 0)

            self._add_option_to_items(identifier, "selected_border",
                                      selected_border)
            fixed.show_all()

    def _remove_selected_border(self, button, identifier):
        '''If the icon in the menu has a selected border, this will remove
        the border.
        If identifier is None, all items will have the border removed
        '''
        if identifier in self._items and \
                'selected_border' in self._items[identifier]:
            fixed = button.get_children()[0]
            selected_border = self._items[identifier]["selected_border"]
            fixed.remove(selected_border)
            selected_border.hide()
            button.show_all()

    def _on_clicking_item(self, button, identifier):
        old_selected_id = self.get_selected()

        if old_selected_id:
            button = self._items[old_selected_id]['button']
            self._remove_selected_border(button, old_selected_id)

        # Since the item should already have the selected apearence from the
        # mouse hovering over it, should not bee needed to add the border again
        self._set_selected(identifier)
        self.emit(self._signal_name, identifier)

    def _only_style_selected(self, identifier):
        '''Adds the CSS class that shows the image that has been selected,
        even when the mouse is moved away.
        If identifier is None, will remove all styling
        '''

        logger.debug("Entered _only_style_selected")
        old_selected_id = self.get_selected()

        if old_selected_id:
            button = self._items[old_selected_id]['button']
            self._remove_selected_border(button, old_selected_id)

        # Since the item should already have the selected apearence from the
        # mouse hovering over it, should not bee needed to add the border again
        self._set_selected(identifier)
        self._add_selected_border(button, identifier)
        self.emit(self._signal_name, identifier)


def get_environment_dict():
    return calculate_badges()['environments']['all']


def order_environments():
    environments = get_environment_dict()
    environment_list = []

    # Put the unlocked items first
    for name, item in environments.iteritems():
        if item['achieved']:
            environment_list.append(item)

    for name, item in environments.iteritems():
        if not item['achieved']:
            environment_list.append(item)
