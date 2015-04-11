"""
Functions shared between GUI dialogs
"""

import re

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QInputDialog, QLineEdit
from PyQt5.QtGui import QPixmap, QImage

from PIL.ImageQt import ImageQt

import assets
from config import Config


def find_color(text):
    match = re.search("\^(\w+);", text)
    if match is not None:
        return match.groups()[0]

def replace_color(name, text):
    span_template = '<span style="color: %s">'
    return text.replace("^%s;" % name,
                        span_template % name)

def text_to_html(text):
    """Convert Starbound text to colored HTML."""
    colored = text
    match = find_color(colored)
    if match is None:
        return text
    while match is not None:
        colored = replace_color(match, colored)
        match = find_color(colored)
    return colored + ("</span>" * colored.count("<span"))

def setup_color_menu(parent, widget):
    def color_dialog():
        color = QInputDialog.getItem(parent, "Select Color",
                                     "Colors", assets.colors)
        widget.insert(assets.string_color(color[0]))
    widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    action = QAction("Insert Color...", widget)
    action.triggered.connect(color_dialog)
    widget.addAction(action)

def inv_icon(item_name, item_data, assets):
    """Return a QPixmap object of the inventory icon of a given item (if possible)."""
    missing = QPixmap.fromImage(QImage.fromData(assets.items().missing_icon())).scaled(32, 32)
    icon_file = assets.items().get_item_icon(item_name)

    if icon_file is None:
        try:
            image_file = assets.items().get_item_image(item_name)
            image_file = assets.images().color_image(image_file, item_data)
            return QPixmap.fromImage(ImageQt(image_file)).scaledToHeight(64)
        except (TypeError, AttributeError):
            return missing

    icon_file = assets.images().color_image(icon_file, item_data)
    try:
        return QPixmap.fromImage(ImageQt(icon_file)).scaled(32, 32)
    except AttributeError:
        return missing

def preview_icon(race, gender):
    """Return an icon image for player race/gender previews."""
    assets_db_file = Config().read("assets_db")
    starbound_folder = Config().read("starbound_folder")
    db = assets.Assets(assets_db_file, starbound_folder)
    icon_file = db.species().get_preview_image(race, gender)
    if icon_file is None:
        return QPixmap.fromImage(QImage.fromData(db.missing_icon())).scaledToHeight(48)
    else:
        return QPixmap.fromImage(QImage.fromData(icon_file)).scaledToHeight(48)

def empty_slot():
    """Return an empty bag slot widget."""
    return ItemWidget(None)

# TODO: a decision needs to be made here whether to continue with the custom
#       widget item or an entirely new custom table view. if the features below
#       are easy enough to add then we'll just stick with the current method
# TODO: swap items instead of overwriting
#       apparently this is done by reimplementing the drag functions
class ItemWidget(QTableWidgetItem):
    """Custom table wiget item with icon support and extra item variables."""
    def __init__(self, item, assets=None):
        if item is None or assets is None or "name" not in item:
            # empty slot
            self.item = None
            QTableWidgetItem.__init__(self)
            return

        self.assets = assets
        self.item = item

        QTableWidgetItem.__init__(self, self.item["name"])
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        name = self.item["name"]
        try:
            asset_name = assets.items().get_item(name)[3]
            if asset_name != "":
                name = asset_name
        except TypeError:
            pass

        self.setToolTip(name + " (" + str(self.item["count"]) + ")")

        icon = inv_icon(self.item["name"], self.item["parameters"], assets)
        try:
            self.setIcon(QtGui.QIcon(icon))
        except TypeError:
            pass

        if type(icon) is QPixmap:
            self.setText("")
