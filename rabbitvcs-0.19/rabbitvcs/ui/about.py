from __future__ import absolute_import
from six.moves import map
from rabbitvcs import gettext
import configobj
import pysvn
import rabbitvcs.ui.widget
from rabbitvcs.ui import InterfaceView
import rabbitvcs
from gi.repository import Gtk, GObject, GdkPixbuf
import gi
from rabbitvcs.util import helper
import re
import string
import os.path

#
# This is an extension to the Nautilus file manager to allow better
# integration with the Subversion source control system.
#
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2010 by Adam Plumb <adamplumb@gmail.com>
#
license = """\
RabbitVCS is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

RabbitVCS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RabbitVCS;  If not, see <http://www.gnu.org/licenses/>.  """


gi.require_version("Gtk", "3.0")
sa = helper.SanitizeArgv()
sa.restore()


_ = gettext.gettext


class About(object):
    """
    This class provides an interface to the About window.

    """

    def __init__(self):
        self.about = Gtk.AboutDialog()
        self.about.set_name(rabbitvcs.APP_NAME)

        self.about.set_program_name(rabbitvcs.APP_NAME)
        self.about.set_version(rabbitvcs.version)
        self.about.set_website("http://www.rabbitvcs.org")
        self.about.set_website_label("http://www.rabbitvcs.org")

        doc_path_root = "/usr/share/doc"
        doc_path_regex = re.compile("rabbitvcs")
        authors_path = None
        for dir in os.listdir(doc_path_root):
            if doc_path_regex.search(dir):
                # Find all the doc directories containing "rabbitvcs"
                tmp_authors_path = os.path.join(doc_path_root, dir, "AUTHORS")
                if os.path.exists(tmp_authors_path):
                    authors_path = tmp_authors_path
                    # At this point we have found a likely-looking AUTHORS
                    break

        if not authors_path:
            # Assumes the user is running RabbitVCS through an svn checkout
            # and the doc files are two directories up (from rabbitvcs/ui).
            doc_path = os.path.dirname(os.path.realpath(__file__)).split("/")
            doc_path = "/".join(doc_path[:-2])
            authors_path = os.path.join(doc_path, "AUTHORS")

        authors = open(authors_path, "r").read()

        self.about.set_authors(authors.split("\n"))

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(
            rabbitvcs.get_icon_path() + "/scalable/apps/rabbitvcs.svg"
        )
        self.about.set_logo(pixbuf)

        versions = []
        versions.append("Subversion - %s" % ".".join(list(map(str, pysvn.svn_version))))
        versions.append("Pysvn - %s" % ".".join(list(map(str, pysvn.version))))
        versions.append("ConfigObj - %s" % str(configobj.__version__))

        self.about.set_comments("\n".join(versions))

        self.about.set_license(license)

    def run(self):
        self.about.show_all()
        self.about.run()
        self.about.destroy()


if __name__ == "__main__":
    window = About()
    window.run()
