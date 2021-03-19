import sqlite3, os, random
conn = sqlite3.connect('fpy.db')

nets1 = ["Flax", "Cotton","Wool","Silk","Nylon"]
categories = ["Hand Net", "Push Net", "Bottom Trawl", "Cast Net", "Drag Net", "Coracle Net", "Drift Net", "Gill Net", "Metal Net", "Drive-in Net", "Ghost Net", "Landing Net", "Lift Net",
              "Purse Seine Net", "Lave Net", "Midwater Trawl Net", "Fyke Net", "Seine Net", "Surrounding Net", "Tangle Net", "Trammel Net"]

price = 0
netnum = 0
mins = 5
for c in categories:
    for r in nets1:
        netnum += 1
        price_increase = random.randint(50,150)
        price += price_increase
        name = f"{r} {c}"
        print(f"{netnum}. {name}")
        #conn.execute("INSERT INTO f_nets VALUES (?, ?, ?)",(netnum, name, price,))
conn.commit()
conn.close()