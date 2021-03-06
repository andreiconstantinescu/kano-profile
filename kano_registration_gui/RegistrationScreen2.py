#!/usr/bin/env python

# RegistrationScreen2.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import datetime
from gi.repository import Gtk, Gdk

from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano_registration_gui.GetData import GetData2, cache_data
from kano_world.functions import register as register_
from kano_profile.profile import save_profile_variable
from kano_profile.tracker import save_hardware_info, save_kano_version
from kano_profile.paths import bin_dir
from kano.network import is_internet
from kano.logging import logger
from kano.utils import run_bg
from kano_profile.tracker import track_data


# Get emails and show the terms and conditions
class RegistrationScreen2(Gtk.Box):

    def __init__(self, win, age):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)

        self.page_control = self.win.create_page_control(2, _("Back").upper(),
                                                         _("Continue").upper())
        self.page_control.disable_next()
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.register_handler)
        self.page_control.connect("back-button-clicked", self.prev_page)

        title = Heading(_('Kano World'), _('Sign up with your email'))
        self.pack_start(title.container, False, False, 0)

        # Pass age into the Data screen - decide whether to ask for
        # Guardian's email
        self.data_screen = GetData2(age)
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)
        self.add(self.data_screen)

        self.show_all()

    def prev_page(self, widget):
        from kano_registration_gui.RegistrationScreen1 import RegistrationScreen1

        self.data_screen.cache_emails()
        self.data_screen.cache_marketing_choice()
        self.win.remove_main_widget()
        RegistrationScreen1(self.win)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()

    def get_email_data(self):
        # Add the info about the emails to the self.win.data parameter
        self.win.data.update(self.data_screen.get_email_entry_data())

    def register_handler(self, widget=None, arg=None):
        if not is_internet():
            internet_present = self.try_to_connect_to_internet()

            if not internet_present:
                quit_dialog = KanoDialog(
                    _("The package was returned to sender"),
                    _("I just tried to send your profile to Kano HQ, \n" \
                      "but it looks like I don't have any Internet! ") + \
                    "\n" + \
                    _("You can keep playing and I'll keep your \n" \
                      "profile safe in my brain until you connect.")
                )
                quit_dialog.run()

                Gtk.main_quit()
                return

        self.register_user_with_gui()

    def register_user_with_gui(self):
        self.data_screen.cache_emails()
        self.data_screen.cache_marketing_choice()

        self.page_control.disable_buttons()
        self.data_screen.disable_all()
        self.get_email_data()

        # Make cursor into a spinner
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)

        # This means no threads are needed.
        while Gtk.events_pending():
            Gtk.main_iteration()

        # Try and register the account on the server
        email = self.win.data["email"]
        secondary_email = self.win.data["secondary_email"]
        username = self.win.data["username"]
        password = self.win.data["password"]
        date_year = self.win.data["year"]
        date_month = self.win.data["month"]
        date_day = self.win.data["day"]
        marketing_enabled = self.win.data["marketing_enabled"]

        logger.info('trying to register user with data {} {} {} {} {} {} {} {}'
                    .format(
                        email, secondary_email, username, password, date_year,
                        date_month, date_day, marketing_enabled
                    )
                    )

        success, text = register_(email, username, password,
                                  date_year, date_month, date_day,
                                  secondary_email=secondary_email,
                                  marketing_enabled=marketing_enabled)

        # This should no longer be needed, since this is checked in the first screen.
        # However there is a small chance someone could take the username
        # while the user is in the process of registering
        if not success:
            if text.strip() == "Cannot register, problem: Username already registered":

                logger.info('username invalid - getting second username')
                self.collect_new_username()
                return

            else:
                logger.info('problem with registration: {}'.format(text))
                return_value = "FAIL"
                self.create_dialog(
                    title=_("Houston, we have a problem"),
                    description=str(text)
                )
                track_data('world-registration-failed', {'reason': text})

        else:
            logger.info('registration successful')

            bday_date = str(datetime.date(date_year, date_month, date_day))
            save_profile_variable('birthdate', bday_date)

            # saving hardware info and initial Kano version
            save_hardware_info()
            save_kano_version()

            # running kano-sync after registration
            logger.info('running kano-sync after successful registration')
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

            return_value = "SUCCEED"
            self.create_dialog(
                title=_("Profile activated!"),
                description=_("Now you can share stuff, build your character, "
                              "and connect with friends.")
            )

        self.page_control.enable_buttons()
        self.data_screen.enable_all()
        self.win.get_window().set_cursor(None)

        # Close the app if it was successful
        if return_value == "SUCCEED":
            Gtk.main_quit()

    def create_dialog(self, title, description):
        kdialog = KanoDialog(
            title,
            description,
            parent_window=self.win
        )
        rv = kdialog.run()
        return rv

    def collect_new_username(self):
        username_entry = Gtk.Entry()

        kdialog = KanoDialog(
            title_text=_("Oops, that username has already been taken!"),
            description_text=_("Try picking another one."),
            button_dict=[
                {
                    "label": _("OK").upper()
                },
                {
                    "label": ("Cancel").upper(),
                    "return_value": "CANCEL",
                    "color": "red"
                }
            ],
            widget=username_entry,
            has_entry=True,
            parent_window=self.win
        )
        rv = kdialog.run()
        if rv == "CANCEL":
            # let dialog close, do nothing
            self.page_control.enable_buttons()
            self.data_screen.enable_all()
            self.win.get_window().set_cursor(None)
        else:
            # rv will be the entry contents
            self.win.data["username"] = rv

            # Store this in kano profile straight away
            cache_data("username", rv)
            self.register_handler()

    def try_to_connect_to_internet(self, attempt_no=1):
        """
        Attempt to connect to the internet
        :param attempt_no: Number of connection attempts already tried
        :returns: If the attempt resulted in an Internet connection
        """

        if attempt_no == 1:
            title = _("You don't have internet!")
            description = _("Connect to WiFi and try again.")
        else:
            title = _("Still not connected...")
            description = _("Seems like you're having trouble connecting.") + \
                "\n" + _("Try again later at another point")

        connect_choice = self.connect_dialog(title, description)

        if connect_choice == 'connect':
            self.win.blur()

            while Gtk.events_pending():
                Gtk.main_iteration()

            logger.debug("Launching WiFi GUI, attempt #{}".format(attempt_no))
            os.system("sudo /usr/bin/kano-wifi-gui")
            logger.debug("Finished connection attempt #{}".format(attempt_no))

            if is_internet():
                return True

            if attempt_no >= 2:
                return False

            return self.try_to_connect_to_internet(attempt_no + 1)
        else:
            return False

    def connect_dialog(self, title, description):
        button_dict = [
            {
                "label": _("Later").upper(),
                "color": "red",
                "return_value": "later"
            },
            {
                "label": _("Connect to WiFi").upper(),
                "color": "green",
                "return_value": "connect"
            }
        ]
        kdialog = KanoDialog(title, description, button_dict,
                             parent_window=self.win)
        rv = kdialog.run()
        return rv
