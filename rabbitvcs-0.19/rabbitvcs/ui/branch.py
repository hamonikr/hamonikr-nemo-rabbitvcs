from __future__ import absolute_import
from rabbitvcs import gettext
import rabbitvcs.vcs.status
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

from rabbitvcs.util import helper

import gi

gi.require_version("Gtk", "3.0")
sa = helper.SanitizeArgv()
sa.restore()


_ = gettext.gettext


class SVNBranch(InterfaceView):
    """
    Provides a UI interface to copy/branch/tag items in the repository or
    working copy.

    Pass a single path to the class when initializing

    """

    SETTINGS = rabbitvcs.util.settings.SettingsManager()

    SWITCH_AFTER = SETTINGS.get("general", "switch_after_branch")

    def __init__(self, path, revision=None):
        InterfaceView.__init__(self, "branch", "Branch")

        self.vcs = rabbitvcs.vcs.VCS()
        self.svn = self.vcs.svn()

        self.path = path
        self.revision = revision

        status = self.vcs.status(self.path)

        repo_paths = helper.get_repository_paths()
        self.from_urls = rabbitvcs.ui.widget.ComboBox(
            self.get_widget("from_urls"), repo_paths
        )
        self.to_urls = rabbitvcs.ui.widget.ComboBox(
            self.get_widget("to_urls"), helper.get_repository_paths()
        )

        repository_url = self.svn.get_repo_url(path)
        self.from_urls.set_child_text(repository_url)
        self.to_urls.set_child_text(repository_url)

        self.message = rabbitvcs.ui.widget.TextView(self.get_widget("message"))
        self.get_widget("toggle_switch_after_branch").set_active(self.SWITCH_AFTER)

        self.revision_selector = rabbitvcs.ui.widget.RevisionSelector(
            self.get_widget("revision_container"),
            self.svn,
            revision=revision,
            url_combobox=self.from_urls,
            expand=True,
        )

        if self.revision is None and status.has_modified():
            self.revision_selector.set_kind_working()

    def on_ok_clicked(self, widget):
        src = self.from_urls.get_active_text()
        dest = self.to_urls.get_active_text()

        if dest == "":
            rabbitvcs.ui.dialog.MessageBox(_("You must supply a destination path."))
            return

        revision = self.revision_selector.get_revision_object()
        self.hide()
        self.action = rabbitvcs.ui.action.SVNAction(
            self.svn, register_gtk_quit=self.gtk_quit_is_set()
        )
        self.action.set_log_message(self.message.get_text())

        self.action.append(helper.save_log_message, self.message.get_text())

        self.action.append(self.action.set_header, _("Branch/tag"))
        self.action.append(self.action.set_status, _("Running Branch/tag Command..."))
        self.action.append(self.svn.copy, src, dest, revision)
        self.action.append(self.action.set_status, _("Completed Branch/tag"))
        if self.SWITCH_AFTER:
            self.action.append(self.action.set_status, _("Running Switch Command..."))
            self.action.append(helper.save_repository_path, dest)
            self.action.append(
                self.svn.switch, self.path, helper.quote_url(dest), revision=revision
            )
            self.action.append(self.action.set_status, _("Completed Switch"))

        self.action.append(self.action.finish)
        self.action.schedule()

    def on_previous_messages_clicked(self, widget, data=None):
        dialog = rabbitvcs.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(S(message).display())

    def on_repo_browser_clicked(self, widget, data=None):
        from rabbitvcs.ui.browser import SVNBrowserDialog

        SVNBrowserDialog(
            self.from_urls.get_active_text(), callback=self.on_repo_browser_closed
        )

    def on_repo_browser_closed(self, new_url):
        self.from_urls.set_child_text(new_url)

    def on_toggle_switch_after_branch_toggled(self, widget, *args):
        self.SWITCH_AFTER = widget.get_active()

        # Save this preference for future commits.
        if self.SETTINGS.get("general", "switch_after_branch") != self.SWITCH_AFTER:
            self.SETTINGS.set("general", "switch_after_branch", self.SWITCH_AFTER)
            self.SETTINGS.write()


classes_map = {rabbitvcs.vcs.VCS_SVN: SVNBranch}


def branch_factory(vcs, path, revision=None):
    if not vcs:
        guess = rabbitvcs.vcs.guess(path)
        vcs = guess["vcs"]

    return classes_map[vcs](path, revision)


if __name__ == "__main__":
    from rabbitvcs.ui import main, REVISION_OPT, VCS_OPT

    (options, args) = main(
        [REVISION_OPT, VCS_OPT], usage="Usage: rabbitvcs branch [url_or_path]"
    )

    window = branch_factory(options.vcs, args[0], options.revision)
    window.register_gtk_quit()
    Gtk.main()
