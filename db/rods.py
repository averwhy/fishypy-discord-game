import sqlite3, random

conn = sqlite3.connect("fpy.db")
rods1 = [
    "Balsa Wood",
    "Basswood",
    "Oak",
    "Hemlock",
    "Poplar",
    "Hickory",
    "Chestnut",
    "Spruce",
    "Larch",
    "Alder",
    "Juniper",
    "Western Larch",
    "Sycamore",
    "Douglas Fir",
    "Pine",
    "Maple",
    "Box Elder",
    "Willow",
    "Beech",
    "Sycamore",
    "Mahogany",
    "Cedar",
    "Birch",
    "Cherry",
    "Walnut",
    "Makore",
    "Oak",
    "Bamboo",
    "Rosewood",
    "Ash",
    "Cypress",
    "Mesquite",
]
rods2 = [
    "Balsa Wood",
    "Basswood",
    "Oak",
    "Hemlock",
    "Poplar",
    "Hickory",
    "Chestnut",
    "Spruce",
    "Larch",
    "Alder",
    "Juniper",
    "Western Larch",
    "Sycamore",
    "Douglas Fir",
    "Pine",
    "Maple",
    "Box Elder",
    "Willow",
    "Beech",
    "Sycamore",
    "Mahogany",
    "Cedar",
    "Birch",
    "Cherry",
    "Walnut",
    "Makore",
    "Oak",
    "Bamboo",
    "Rosewood",
    "Ash",
    "Cypress",
    "Mesquite",
    "Graphite",
    "Carbon Fiber",
    "Fiberglass",
]

categories = [
    "Stick",
    "Stick and Thread",
    "Spear",
    "Slingshot",
    "Stick and String",
    "Long Stick with String",
    "Harpoon",
]
categories2 = [
    "Basic Rod",
    "Ultra-Light Rod",
    "Fly Rod",
    "Surf Rod",
    "Spinning Rod",
    "Trolling Rod",
    "Telescoptic Rod",
    "Casting Rod",
    "Spin Caster Rod",
]
price = 0
rodnum = 0
for c in categories:
    for r in rods1:
        rodnum += 1
        price_increase = random.randint(25, 45)
        price += price_increase
        name = f"{r} {c}"
        conn.execute(
            "INSERT INTO f_rods VALUES (?, ?, ?)",
            (
                rodnum,
                name,
                price,
            ),
        )

for c2 in categories2:
    for r2 in rods2:
        rodnum += 1
        price_increase = random.randint(45, 95)
        price += price_increase
        # print(f"Rod {rodnum}. {r2} {c2} ({price} coins) Max length = {(rodnum * 3.163265306122449)}cm")
        name2 = f"{r2} {c2}"
        conn.execute(
            "INSERT INTO f_rods VALUES (?, ?, ?)",
            (
                rodnum,
                name2,
                price,
            ),
        )
conn.commit()
conn.close()
