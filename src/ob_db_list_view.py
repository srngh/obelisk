# obelisk_tree_list_view.py
#
# Copyright 2025 simhof
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

from uuid import uuid4
from gi.repository import GLib, GObject, Gdk, Gio, Gtk


from .widgets.ob_context_menu import ObContextMenu
from .widgets.ob_edit_item_dialog import ObEditItemDialog
from .widgets.ob_rename_item_dialog import ObRenameItemDialog
from .widgets.ob_tree_expander import ObTreeExpander
from .widgets.ob_tree_node import ObTreeNode


class ObDBListView(Gtk.ListView):
    """
    ObListView Class, which presents a dynamic List of nested Items.
    A ObConfig must be passed, to retrieve the fully built Data Model to present.
    """
    __gtype_name__ = 'ObeliskDBListView'

    model = Gtk.SingleSelection()

    def __init__(self, config, parent, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.parent = parent

        # Factory to populate the ListView
        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.on_setup)
        factory.connect('bind', self.on_bind)
        factory.connect('unbind', self.on_unbind)
        self.set_factory(factory)

        # Right click
        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect('released', self.__on_button_press)
        self.add_controller(gesture)
        self.set_model(self.config.selection_model)

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

    def on_setup(self, factory, list_item):
        """
        Setup Method for Factory, this creates TreeWidgets when necessary.

        :param factory: The factory calling this method
        :type factory: Gtk.SignalListItemFactory
        :param list_item: The ListItem passed by the factory
        :type list_item: Gtk.ListItem
        """
        widget = ObTreeWidget()
        widget.image.set_visible(False)

        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect('prepare', self.on_drag_prepare, list_item)
        widget.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(ObTreeNode.__gtype__, Gdk.DragAction.MOVE)
        drop_target.connect('accept', self.on_drop_accept, list_item)
        drop_target.connect('drop', self.on_drop, list_item)
        widget.add_controller(drop_target)

        list_item.set_child(widget)

    def on_bind(self, factory, list_item):
        """
        Bind Method for Factory, this (re-)binds TreeWidgets to items.

        :param factory: The factory calling this method
        :type factory: Gtk.SignalListItemFactory
        :param list_item: The ListItem passed by the factory
        :type list_item: Gtk.ListItem
        """
        list_row = list_item.get_item()
        widget = list_item.get_child()
        node = list_row.get_item()
        widget._bound_node = node

        widget.expander.set_list_row(list_row)
        widget.update_bind()

        if node.is_folder:
            widget.image.set_visible(False)
        else:
            widget.image.set_visible(True)

        binding = node.bind_property(
            'name',
            widget.label,
            'label',
            GObject.BindingFlags.SYNC_CREATE
        )
        list_item._name_binding = binding

    def on_unbind(self, factory, list_item):
        """
        Unbind Method for Factory, this unbinds TreeWidgets from items.

        :param factory: The factory calling this method
        :type factory: Gtk.SignalListItemFactory
        :param list_item: The ListItem passed by the factory
        :type list_item: Gtk.ListItem
        """
        widget = list_item.get_child()
        if hasattr(list_item, '_name_binding') and list_item._name_binding:
            list_item._name_binding.unbind()
            list_item._name_binding = None
        widget.image.set_visible(False)

    def __on_button_press(self, gesture, npress, x, y):
        """
        Opens a Context Menu pointing to the referenced Item in the ListView.
        If a folder is clicked, its UUID will be passed to the context menu.
        If a node is clicked, the parent folders UUID will be passed to the context menu.
        If the empty part is clicked, the parent is assumed to be the root of the ListView.

        :param gesture: The released gesture invoking this function
        :type gesture: Gtk.GestureClick
        :param npress: The amount of clicks
        :type npress: int
        :param x: X coordinate of the click
        :type x: float
        :param y: Y coordinate of the click
        :type y: float
        :rtype: bool
        """
        tree_widget = self.__get_tree_widget(x, y)
        if hasattr(tree_widget, 'expander'):
            expander = tree_widget.expander
        else:
            expander = None

        # Cleanup context menus, if they haven't been properly dereferenced before
        if hasattr(self, 'context_menu'):
            self.context_menu.unparent(self.context_menu)

        if npress != 1:
            return False
        elif expander is None:
            # When clicking on any empty part of the ListView
            folder_id = '00000000-0000-0000-0000-000000000000'
            self.context_menu = ObContextMenu(folder_id)
            self.context_menu.set_parent(self.parent)
            self.context_menu.popup_at(x, y)
            return True
        else:
            # When clicking on any item or folder of the ListView
            item = expander.props.item
            folder_id = None
            if not item.is_folder:
                # Try to lookup
                folder_id = item.parent_uuid
                if folder_id is None:
                    folder_id = '00000000-0000-0000-0000-000000000000'
            elif item.is_folder:
                folder_id = item.uuid

            if folder_id is not None:
                self.context_menu = ObContextMenu(folder_id, node_uuid=item.uuid)

                # not exactly elegant, but this binds the popover to the Adw.Bin which contains the Sidebar
                # otherwise the popover is really small and comes with an annoying scrollbar
                self.context_menu.set_parent(self.parent)
                list_row = expander.get_list_row()
                self.model.set_selected(list_row.get_position())

                self.context_menu.popup_at(x, y)
                return True

    def derefence_context_menu(self):
        """
        This is a cleanup function. It removes leftover Popover Menus.
        """
        popover = self.context_menu
        popover.unparent(popover)
        del popover

    def __get_tree_widget(self, x, y):
        """
        Get the TreeExpander at X, Y coordinates.

        :param x: X coordinate
        :type x: float
        :param y: Y coordinate
        :type y: float
        :return: Clicked TreeExpander or None
        :rtype: Gtk.TreeExpander or None
        """
        pick = self.pick(x, y, Gtk.PickFlags.DEFAULT)

        if pick is None:
            return None

        if isinstance(pick, ObTreeWidget):
            return pick

        child = pick.get_first_child()
        if child and isinstance(child, ObTreeWidget):
            return child

        parent = pick.props.parent
        if parent and isinstance(parent, ObTreeWidget):
            return parent

        return None

    def _on_new_item_activate(self, action, param_array):
        """
        Callback for the list_view.new_item action.
        Folder Lookup has been performed in ObListView already.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('s'))
        :param folder_uuid: UUID of the target folder in the sidebar
        :type folder_uuid: GLib.VariantType('s')
        """
        try:
            self.derefence_context_menu()
        except AttributeError:
            pass

        if param_array is not None:
            string_list = param_array.get_strv()
            item_type = string_list[0]
            folder_uuid = string_list[1]

        if folder_uuid == '00000000-0000-0000-0000-000000000000':
            self.item_dialog = ObEditItemDialog(parent_uuid=None, node_uuid=str(uuid4()), db_handler=self.config.db_handler, dialog_mode=f'new_{item_type}')
            self.item_dialog.connect('refresh_parent', self.__refresh_parent)
            self.item_dialog.present(self)
        elif folder_uuid != '':
            self.item_dialog = ObEditItemDialog(parent_uuid=folder_uuid, node_uuid=str(uuid4()), db_handler=self.config.db_handler, dialog_mode=f'new_{item_type}')
            self.item_dialog.connect('refresh_parent', self.__refresh_parent)
            self.item_dialog.present(self)

    def __on_new_item_create(self, dialog, node, folder):
        """
        Callback for the node_submitted Signal from ObEditItemDialog.

        :param dialog: Dialog which sends the signal
        :type dialog: ObEditItemDialog
        :param node: Node returned by the Dialog
        :type node: ObTreeNode
        :param folder: Parent Folder / ListStore of the new Node
        :type folder: ObListStore
        """
        del dialog
        self.config.add_item(node, folder)

    def _on_rename_item_activate(self, action, node_uuid):
        """
        Callback for the list_view.rename_item action.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('s'))
        :param node_uuid: The UUID of the node.
        :type node_uuid: GLib.VariantType('s')
        """

        try:
            self.derefence_context_menu()
        except AttributeError:
            pass
        node = self.config.get_node_by_uuid(node_uuid.get_string())
        dialog = ObRenameItemDialog(node)

        dialog.connect('renamed', self.__on_item_renamed)

        dialog.present(self.get_root())

    def __on_item_renamed(self, dialog, node, name):
        """
        Convenience function for renaming an item from a dialog.

        :param dialog: The dialog calling this method.
        :type dialog: Gtk.Dialog
        :param node: The node to be renamed
        :type node: ObTreeNode
        :param name: New name for the node
        :type name: str
        """
        cursor = self.config.db_handler.conn.cursor()

        cursor.execute('UPDATE connections SET name = ? WHERE uuid = ?', (name, node.uuid))
        self.__refresh_parent(None, node.parent_uuid)

    def _on_remove_item_activate(self, action, node_uuid):
        """
        Callback for the list_view.delete_item action.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('s'))
        :param node_uuid: The UUID of the node.
        :type node_uuid: GLib.VariantType('s')
        """
        try:
            self.derefence_context_menu()
        except AttributeError:
            pass

        node = self.config.get_node_by_uuid(node_uuid.get_string())
        self.config.remove_item(node)
        self.__refresh_parent(None, node.parent_uuid)

    def _on_edit_item_activate(self, action, uuid_array):
        """
        Callback for the list_view.edit_item action.
        Folder Lookup has been performed in ObListView already.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('as'))
        :param uuid_array: Array containing folder_uuid and node_uuid
        :type uuid_array: GLib.VariantType('as')
        """
        try:
            self.derefence_context_menu()
        except AttributeError:
            pass

        node = None
        if uuid_array is not None:
            string_list = uuid_array.get_strv()
            folder_uuid = string_list[0]
            node_uuid = string_list[1]

        if node_uuid != '':
            node = self.config.get_node_by_uuid(node_uuid)

        # Folders are not editable for now, until inheritance of parameters is implemented
        if node is not None:
            self.item_dialog = ObEditItemDialog(parent_uuid=node.parent_uuid, node_uuid=node.uuid, db_handler=self.config.db_handler, dialog_mode='edit_node')
            self.item_dialog.connect('refresh_parent', self.__refresh_parent)
            self.item_dialog.present(self)

    def __refresh_parent(self, dialog, parent_uuid):
        """
        Callback for ObEditItemDialog.
        Refreshes a Folder, so the UI represents the state of the database.
        """
        if dialog is not None:
            del dialog

        if parent_uuid not in self.config.active_stores:
            if parent_uuid is None:
                new_data = self.config.get_children(parent_uuid=None, uuid='00000000-0000-0000-0000-000000000000')
                self.config.root_store.splice(0, self.config.root_store.get_n_items(), new_data)
            return

        store = self.config.active_stores[parent_uuid]

        new_children = self.config.get_children(parent_uuid)

        store.splice(0, store.get_n_items(), new_children)

    def _on_clone_item_activate(self, action, uuid_array):
        """
        Callback for the list_view.clone_item action.
        Folder Lookup has been performed in ObListView already.

        :param action: The action calling this method.
        :type action: Gio.SimpleAction(GLib.VariantType('as'))
        :param uuid_array: Array containing folder_uuid and node_uuid
        :type uuid_array: GLib.VariantType('as')
        """
        try:
            self.derefence_context_menu()
        except AttributeError:
            pass

        node = None
        if uuid_array is not None:
            string_list = uuid_array.get_strv()
            folder_uuid = string_list[0]
            node_uuid = string_list[1]

        if node_uuid != '':
            node = self.config.get_node_by_uuid(node_uuid)

        if node is not None:
            self.item_dialog = ObEditItemDialog(parent_uuid=node.parent_uuid, node_uuid=node.uuid, db_handler=self.config.db_handler, dialog_mode='clone_node')
            self.item_dialog.connect('refresh_parent', self.__refresh_parent)
            self.item_dialog.present(self)

    # Drag and Drop Methods
    def on_drag_prepare(self, drag_source, x, y, list_item):
        widget = list_item.get_child()
        dragged_node = widget._bound_node

        return Gdk.ContentProvider.new_for_value(dragged_node)

    def on_drop_accept(self, drop_target, drop, list_item):
        target_node = list_item.get_child()._bound_node

        if not target_node.is_folder:
            return False
        return True

    def on_drop(self, drop_target, dragged_value, x, y, list_item):
        target_node = list_item.get_child()._bound_node
        dragged_node = dragged_value
        old_parent_uuid = dragged_node.parent_uuid

        if target_node == dragged_node:
            return False

        self.config.add_item(dragged_node, target_node)
        self.__refresh_parent(dialog=None, parent_uuid=target_node.uuid)
        self.__refresh_parent(dialog=None, parent_uuid=old_parent_uuid)
        return True


class ObTreeWidget(Gtk.Box):
    __gtype_name__ = 'ObTreeWidget'

    def __init__(self):
        super().__init__(
            spacing=2
        )
        self.expander = ObTreeExpander()
        self.image = Gtk.Image.new_from_icon_name('org.gnome.Terminal-symbolic')
        self.label = Gtk.Label(halign=Gtk.Align.START)

        self.append(self.expander)
        self.append(self.image)
        self.append(self.label)

    def update_bind(self):
        item = self.expander.props.item
        item.connect('notify::n-items', self.expander.on_item_n_items_notify)

    def clear_bind(self):
        item = self.expander.props.item
        item.disconnect_by_func(self.expander.on_item_n_items_notify)


#if not node.is_folder:
#    image = Gtk.Image.new_from_icon_name('org.gnome.Terminal-symbolic')
#    image.set_icon_size(1)
#    widget.insert_child_after(image, widget.expander)
