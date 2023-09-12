from __future__ import absolute_import
from rabbitvcs import gettext
from rabbitvcs.ui.updateto import GitUpdateToRevision
import rabbitvcs.vcs
from rabbitvcs.util.strings import S
import rabbitvcs.ui.action
import rabbitvcs.ui.dialog
import rabbitvcs.ui.widget
from rabbitvcs.ui import InterfaceView
from gi.repository import Gtk, GObject, Gdk

#
# This is an extension to the Nautilus file manager to allow better
# integration with the Subversion source control system.
#
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2010 by Adam Plumb <adamplumb@gmail.com>
#
# RabbitVCS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# RabbitVCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RabbitVCS;  If not, see <http://www.gnu.org/licenses/>.
#

import os.path

from rabbitvcs.util import helper

import gi

gi.require_version("Gtk", "3.0")
sa = helper.SanitizeArgv()
sa.restore()

_ = gettext.gettext


class Checkout(InterfaceView):
    """
    Provides an interface to check out a working copy.

    Pass it the destination path.

    """

    def __init__(self, path=None, url=None, revision=None):
        InterfaceView.__init__(self, "checkout", "Checkout")

        self.path = path
        self.vcs = rabbitvcs.vcs.VCS()

        self.repositories = rabbitvcs.ui.widget.ComboBox(
            self.get_widget("repositories"), helper.get_repository_paths()
        )

        # We must set a signal handler for the Gtk.Entry inside the combobox
        # Because glade will not retain that information
        self.repositories.set_child_signal(
            "key-release-event", self.on_repositories_key_released
        )

        self.destination = helper.get_user_path()
        if path is not None:
            self.destination = path
            self.get_widget("destination").set_text(S(path).display())

        if url is not None:
            self.repositories.set_child_text(url)

        self.complete = False

    #
    # UI Signal Callback Methods
    #

    def _parse_path(self, path):
        if path.startswith("file://"):
            path = helper.unquote(path)
            path = path[7:]
        return path

    def _get_path(self):
        path = self._parse_path(self.get_widget("destination").get_text())
        return os.path.normpath(path)

    def on_file_chooser_clicked(self, widget, data=None):
        chooser = rabbitvcs.ui.dialog.FolderChooser()
        path = chooser.run()
        if path is not None:
            self.get_widget("destination").set_text(S(path).display())

    def on_repositories_key_released(self, widget, event, *args):
        if Gdk.keyval_name(event.keyval) == "Return":
            if self.complete:
                self.on_ok_clicked(widget)

    def on_destination_changed(self, widget, data=None):
        self.check_form()

    def on_destination_key_released(self, widget, event, *args):
        if Gdk.keyval_name(event.keyval) == "Return":
            if self.complete:
                self.on_ok_clicked(widget)

    def on_repo_chooser_clicked(self, widget, data=None):
        from rabbitvcs.ui.browser import SVNBrowserDialog

        SVNBrowserDialog(
            self.repositories.get_active_text(), callback=self.on_repo_chooser_closed
        )

    def on_repo_chooser_closed(self, new_url):
        self.repositories.set_child_text(new_url)
        self.check_form()

    def check_form(self):
        self.complete = True
        if self.repositories.get_active_text() == "":
            self.complete = False
        if self.get_widget("destination").get_text() == "":
            self.complete = False

        self.get_widget("ok").set_sensitive(self.complete)


class SVNCheckout(Checkout):
    def __init__(self, path=None, url=None, revision=None):
        Checkout.__init__(self, path, url, revision)
        self.get_widget("Checkout").set_title(_("Checkout - %s") % path)

        self.svn = self.vcs.svn()

        self.revision_selector = rabbitvcs.ui.widget.RevisionSelector(
            self.get_widget("revision_container"),
            self.svn,
            revision=revision,
            url_combobox=self.repositories,
            expand=True,
        )

        self.get_widget("options_box").show()
        self.get_widget("revision_selector_box").show()

        self.check_form()

    def on_ok_clicked(self, widget):
        url = self.repositories.get_active_text()
        path = self._get_path()
        omit_externals = self.get_widget("omit_externals").get_active()
        recursive = self.get_widget("recursive").get_active()

        if not url or not path:
            rabbitvcs.ui.dialog.MessageBox(
                _("The repository URL and destination path are both required fields.")
            )
            return

        revision = self.revision_selector.get_revision_object()

        self.hide()
        self.action = rabbitvcs.ui.action.SVNAction(
            self.svn, register_gtk_quit=self.gtk_quit_is_set()
        )
        self.action.append(self.action.set_header, _("Checkout"))
        self.action.append(self.action.set_status, _("Running Checkout Command..."))
        self.action.append(helper.save_repository_path, url)
        self.action.append(
            self.svn.checkout,
            helper.quote_url(url),
            path,
            recurse=recursive,
            revision=revision,
            ignore_externals=omit_externals,
        )
        self.action.append(self.action.set_status, _("Completed Checkout"))
        self.action.append(self.action.finish)
        self.action.schedule()

    def on_repositories_changed(self, widget, data=None):
        # Do not use quoting for this bit
        url = self.repositories.get_active_text()
        tmp = url.replace("//", "/").split("/")[1:]
        append = ""
        prev = ""
        while len(tmp):
            prev = append
            append = tmp.pop()
            if append not in ("trunk", "branches", "tags"):
                break

            if append in ("http:", "https:", "file:", "svn:", "svn+ssh:"):
                append = ""
                break

        self.get_widget("destination").set_text(
            S(os.path.join(self.destination, append)).display()
        )

        self.check_form()


class GitCheckout(GitUpdateToRevision):
    def __init__(self, path, url, revision):
        GitUpdateToRevision.__init__(self, path, revision)
        self.get_widget("Update").set_title(_("Checkout - %s") % path)
        self.get_widget("options_box").hide()


class GitCheckoutQuiet(object):
    def __init__(self, path):
        self.vcs = rabbitvcs.vcs.VCS()
        self.git = self.vcs.git(path)
        self.action = rabbitvcs.ui.action.GitAction(self.git, run_in_thread=False)

        self.action.append(self.git.checkout, [path])
        self.action.schedule()


classes_map = {rabbitvcs.vcs.VCS_SVN: SVNCheckout, rabbitvcs.vcs.VCS_GIT: GitCheckout}


def checkout_factory(vcs, path=None, url=None, revision=None, quiet=False):
    if not vcs:
        guess = rabbitvcs.vcs.guess(path)
        vcs = guess["vcs"]

    if vcs == rabbitvcs.vcs.VCS_DUMMY:
        return SVNCheckout(path, url, revision)
    elif vcs == rabbitvcs.vcs.VCS_GIT:
        if quiet:
            return GitCheckoutQuiet(path)
        else:
            return GitCheckout(path, url, revision)

    return classes_map[vcs](path, url, revision)


if __name__ == "__main__":
    from rabbitvcs.ui import main, REVISION_OPT, VCS_OPT, QUIET_OPT

    (options, args) = main(
        [REVISION_OPT, VCS_OPT, QUIET_OPT],
        usage="Usage: rabbitvcs checkout --vcs=[git|svn] [url] [path]",
    )

    # If two arguments are passed:
    #   The first argument is expected to be a url
    #   The second argument is expected to be a path
    # If one argument is passed:
    #   If the argument exists, it is a path
    #   Otherwise, it is a url
    path = url = None
    if len(args) == 2:
        path = args[0]
        url = args[1]
    elif len(args) == 1:
        if os.path.exists(args[0]):
            path = args[0]
        else:
            url = args[0]

    if options.quiet:
        window = checkout_factory(
            options.vcs,
            path=path,
            url=url,
            revision=options.revision,
            quiet=options.quiet,
        )
    else:
        window = checkout_factory(
            options.vcs,
            path=path,
            url=url,
            revision=options.revision,
            quiet=options.quiet,
        )
        window.register_gtk_quit()
        Gtk.main()
