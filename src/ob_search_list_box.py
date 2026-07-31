# obelisk_search_list_box.py
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

from gi.repository import GLib, GObject, Gdk, Gio, Gtk


from .widgets.ob_context_menu import ObContextMenu
from .widgets.ob_edit_item_dialog import ObEditItemDialog
from .widgets.ob_rename_item_dialog import ObRenameItemDialog

logger = logging.getLogger(__name__)


class ObSearchListBox(Gtk.ListBox):
    """
    ObListView Class, which presents a dynamic List of nested Items.
    An ObConfig must be passed, to retrieve the fully built Data Model to present.
    """
    __gtype_name__ = 'ObSearchListBox'

    def __init__(self, config, parent, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.parent = parent

        # Right click
        # gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        # gesture.connect('released', self.__on_button_press)
        # self.add_controller(gesture)
        # self.set_model(self.config.selection_model)

        # Callbacks for Context Menu
        self.action_group = Gio.SimpleActionGroup.new()

        for action in [
            'rename_item',
            'remove_item',
        ]:
            gaction = Gio.SimpleAction.new(action, GLib.VariantType.new('s'))
            gaction.connect('activate', getattr(self, f'_on_{action}_activate'))
            self.action_group.add_action(gaction)

        for action in [
            'new_item',
            'edit_item',
            'clone_item',
        ]:
            gaction = Gio.SimpleAction.new(action, GLib.VariantType.new('as'))
            gaction.connect('activate', getattr(self, f'_on_{action}_activate'))
            self.action_group.add_action(gaction)

        self.parent.insert_action_group('list_view', self.action_group)

    def _append(self, row):
        """
        Convenience Method.
        """
        

    def _create_result_row(self, uuid, name, is_folder):
        """
        Creates a ListBoxRow.
        """
        row = Gtk.ListBoxRow()
        box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_child(box)

        row.uuid = uuid
        row.is_folder = is_folder

        if not is_folder:
            image = Gtk.Image.new_from_icon_name('org.gnome.Terminal-symbolic')
        else:
            image = Gtk.Image.new_from_icon_name('folder-closed-symbolic')
            image.add_css_class("folder")

        box.append(image)

        label = Gtk.Label(label=name, xalign=0)

        box.append(label)
        return row

# search ObListStore

# 