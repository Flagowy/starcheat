import os
import logging

from io import BytesIO
from PIL import Image


class Techs():
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_tech(self, key):
        if key.endswith(".tech"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        name = os.path.basename(asset[0]).split(".")[0]
        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        item = self.assets.read(asset[0]+"item", asset[1])
        if item is None or "itemName" not in item:
            logging.warning("No techitem for %s in %s" % asset)
            return

        return (key, path, "tech", "", name, item["itemName"])

    def all(self):
        """Return a list of all techs."""
        c = self.assets.db.cursor()
        c.execute("select desc from assets where type = 'tech' order by desc")
        return [x[0] for x in c.fetchall()]

    def get_tech(self, name):
        q = "select key, path from assets where type = 'tech' and (name = ? or desc = ?)"
        c = self.assets.db.cursor()
        c.execute(q, (name, name))

        tech = c.fetchone()
        if tech is None:
            return

        asset = self.assets.read(tech[0], tech[1])
        info = self.assets.read(tech[0]+"item", tech[1])
        icon = self.assets.read(info["inventoryIcon"], tech[1], image=True)

        if icon is None:
            icon = self.assets.items().missing_icon()

        return info, Image.open(BytesIO(icon)).convert("RGBA"), tech[0], asset
