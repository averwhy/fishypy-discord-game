import aiosqlite

class fish:
    def __init__(self, data):
        #(oid text, imgurl text, rarity text, id integer, legnth real, name text, fishlength real)
        self.oid = data[0]
        self.image_url = data[1]
        self.rarity = data[2]
        self.db_position = data[3]
        self.length = data[4]
        self.name = data[5]
    def calculate_rarity(self):
        raritycalc = self.length
        raritycalc2 = None
        if raritycalc > 500:
            raritycalc2 = "Mythical"
        elif raritycalc > 200:
            raritycalc2 = "Legendary"
        elif raritycalc > 90:
            raritycalc2 = "Rare"
        elif raritycalc > 40:
            raritycalc2 = "Uncommon"
        elif raritycalc > 0:
            raritycalc2 = "Common"
        return raritycalc2