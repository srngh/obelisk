# ob_rename_item_popover.py
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

from gi.repository import GObject, Gtk

from .ob_tree_node import ObTreeNode


class ObRenameItemDialog(Gtk.Dialog):
    __gtype_name__ = 'ObRenameItemDialog'
    __gsignals__ = {
        'renamed': (GObject.SignalFlags.RUN_FIRST, None, (ObTreeNode, str,))
    }

    def __init__(self, parent_window, node, **kwargs):

        super().__init__(title='Rename', transient_for=parent_window, modal=True)
        self.node = node

        box = self.get_content_area()
        box.set_spacing(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)

        input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.entry.set_text(node.name)
        input_box.append(self.entry)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        self.cancel_button = Gtk.Button(label='Cancel')
        self.cancel_button.add_css_class('destructive-action')
        self.cancel_button.connect('clicked', self.on_cancel_activated)
        button_box.append(self.cancel_button)

        self.rename_button = Gtk.Button(label='Confirm')
        self.rename_button.add_css_class('suggested-action')
        self.rename_button.connect('clicked', self.on_rename_activated)
        button_box.append(self.rename_button)

        input_box.append(button_box)
        box.append(input_box)
        self.set_child(box)

    def on_rename_activated(self, widget):
        new_name = self.entry.get_text().strip()
        try:
            if new_name != self.node.name and new_name != '':
                self.emit('renamed', self.node, new_name)
                self.close()
        finally:
            self.close()

    def on_cancel_activated(self, widget):
        self.close()

