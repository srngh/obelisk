# ob_rename_item_dialog.py
#
# Copyright 2026 simhof
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, GObject, Gtk

from .ob_tree_node import ObTreeNode

@Gtk.Template(resource_path='/io/github/srngh/obelisk/gtk/ob_rename_item_dialog.ui')
class ObRenameItemDialog(Adw.Dialog):
    __gtype_name__ = 'ObRenameItemDialog'
    __gsignals__ = {
        'renamed': (GObject.SignalFlags.RUN_FIRST, None, (ObTreeNode, str,))
    }

    rename_entry = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    confirm_button = Gtk.Template.Child()

    def __init__(self, node, **kwargs):

        super().__init__(title='Rename')
        self.node = node

        self.rename_entry.set_text(node.name)
        self.cancel_button.connect('clicked', self.on_cancel_activated)
        self.confirm_button.connect('clicked', self.on_rename_activated)


    def on_rename_activated(self, widget):
        """
        Callback for confirm button.

        :param widget: The widget calling this method
        :type widget: Gtk.Button
        """
        new_name = self.rename_entry.get_text().strip()
        try:
            if new_name != self.node.name and new_name != '':
                self.emit('renamed', self.node, new_name)
                self.close()
        finally:
            self.close()

    def on_cancel_activated(self, widget):
        self.close()


