import sqlite3, random

conn = sqlite3.connect("fpy.db")

nets1 = ["Flax", "Cotton", "Wool", "Silk", "Nylon"]
categories = [
    "Hand Net",
    "Push Net",
    "Bottom Trawl",
    "Cast Net",
    "Drag Net",
    "Coracle Net",
    "Drift Net",
    "Gill Net",
    "Metal Net",
    "Drive-in Net",
    "Ghost Net",
    "Landing Net",
    "Lift Net",
    "Purse Seine Net",
    "Lave Net",
    "Midwater Trawl Net",
    "Fyke Net",
    "Seine Net",
    "Surrounding Net",
    "Tangle Net",
    "Trammel Net",
]

price = 0
netnum = 0
mins = 5.0
for c in categories:
    for r in nets1:
        netnum += 1
        name = f"{r} {c}"
        conn.execute(
            "INSERT INTO f_nets VALUES (?, ?, ?, ?)",
            (
                netnum,
                name,
                price,
                mins,
            ),
        )
        print(f"{netnum}. {name} ({price} coins) ({mins} mins)")
        price_increase = random.randint(450, 650)
        price += price_increase
        mins += 1
        mins = round(mins, 1)
conn.commit()
conn.close()
