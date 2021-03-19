import aiosqlite
import math, random
import typing
import discord
from cogs.utils.botchecks import FishNotFound
from datetime import datetime
import enum

#Rarities
#if the rarity is above the number in the variable, then it is that rarity
#Ex. 1.4 == extremely rare, 1.1 == very rare
EXTREMELY_RARE = 1.3
VERY_RARE = 1.05
RARE = 0.8
COMMON = 0


class fish:
    def __init__(self, bot, data):
        self.bot = bot
        if data is None:
            raise FishNotFound()
        self.oid = data[0]
        self.image_url = data[1]
        self.rarity = float(data[2])
        self.db_position = data[3]
        self.original_length = float(data[4])
        self.modified_length = self.original_length
        self.name = data[5]
    
    @staticmethod
    async def fancy_rarity(fish_rarity):
        if fish_rarity > EXTREMELY_RARE:
            return ["Extremely Rare", 0xfcff00]
        elif fish_rarity > VERY_RARE:
            return ["Very Rare", 0xff00bf]
        elif fish_rarity > RARE:
            return ["Rare" , 0x0000ff]
        else:
            return ["Common", 0x40ff00]
    
    def coins(self, rod_level):
        math = ((self.rarity * (self.original_length * 2)) * (1 + (rod_level * 0.01)))
        return round(math, 1)

class player:
    def __init__(self, bot, data, user):
        self.bot = bot
        self.id = int(data[0])
        self.name = str(data[1])
        self.guild_id = int(data[2])
        self.rod = self.rod_level = int(data[3])
        self.coins = float(data[4])
        self.as_of = datetime.utcnow() # shows how up to date the object is
        try: self.trophy_oid = str(data[5])
        except: self.trophy_oid = None
        try: self.trophy_rod_level = int(data[6])
        except: self.trophy_rod_level = None
        try: self.review_message_id = int(data[8])
        except: self.review_message_id = None
        self.hex_color = str(data[7])
        self.total_caught = int(data[9])
        if not isinstance(user, (discord.User, discord.Member)):
            raise TypeError()
        self.user = user
        self.autofishing_notif = int(data[10])
        self.net = self.net_level = int(data[11])
        
    @staticmethod
    async def create(bot, user: discord.User):
        player = await bot.usercheck(user.id)
        if player:
            return False
        #(userid integer, name text, guildid integer, rodlevel int, coins double, trophyoid text, trophyrodlvl int, hexcolor text, reviewmsgid integer)
        await bot.db.execute("INSERT INTO f_users VALUES (?, ?, 0, 1, 0, 'none', 0, 'none', 0, 0)",(user.id, user.name,))
        await bot.db.commit()
        return True

    async def update(self):
        """Updates the objects data, i'd rather do this than create a new object"""
        cur = await self.bot.db.execute("SELECT * FROM f_users WHERE userid = ?",(self.id,))
        data = await cur.fetchone()
        if data is None:
            return False
        self.bot = bot
        self.id = int(data[0])
        self.name = str(data[1])
        self.guild_id = int(data[2])
        self.rod = int(data[3])
        self.rod_level = self.rod #Alias
        self.coins = float(data[4])
        self.total_caught = int(data[9])
        self.as_of = datetime.utcnow() # shows how up to date the object is
        return True

    async def check_collection(self, oid):
        """Checks the players collection for a caught fish. Returns False if it is not in the collection, true if it is."""
        c = await self.bot.db.execute("SELECT * FROM f_collections WHERE userid = ? AND oid = ?",(self.id, oid,))
        data = await c.fetchone()
        if data is None:
            return False
        return True
    
    async def update_collection(self,oid):
        c = await self.bot.db.execute("SELECT * FROM f_collections WHERE userid = ? AND oid = ?",(self.id, oid,))
        if (await c.fetchone()) is None:   
            await self.bot.db.execute("INSERT INTO f_collections VALUES (?, ?)",(self.id,oid,))
        else: pass
        await self.bot.db.commit()
        return
    
    async def get_collection(self):
        c = await self.bot.db.execute("SELECT COUNT(*) FROM f_collections WHERE userid = ?",(self.id,))
        try: amount_caught = (await c.fetchone())[0]
        except: amount_caught = 0
        c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes")
        number_of_fish = (await c.fetchone())[0]
        return f"{amount_caught}/{number_of_fish}"
        
        
    async def check_trophy(self, caughtoid):
        caughtfish = await self.bot.get_fish(caughtoid)
        trophyfish = await self.bot.get_fish(self.trophy_oid)
        if trophyfish is None:
            #They dont have a trophy (its their first fish)
            await self.bot.db.execute("UPDATE f_users SET trophyoid = ? WHERE userid = ?",(caughtoid, self.id,))
            await self.bot.db.execute("UPDATE f_users SET trophyrodlvl = ? WHERE userid = ?",(self.rod_level, self.id,))
            await self.bot.db.commit()
            return
        if caughtfish.original_length > trophyfish.original_length:
            await self.bot.db.execute("UPDATE f_users SET trophyoid = ? WHERE userid = ?",(caughtoid, self.id,))
            await self.bot.db.execute("UPDATE f_users SET trophyrodlvl = ? WHERE userid = ?",(self.rod_level, self.id,))
            await self.bot.db.commit()
            return
        else:
            # Caught fish is shorter than trophy length
            return
    
    async def update_review(self, reviewtext):
        try:
            c = await self.bot.db.execute("SELECT * FROM f_users WHERE userid = ?",(self.id,))
            data = await c.fetchone()
            await self.bot.db.commit()
            if data: # player exists
                stored_id = int(data[7])
                reviewchannel = bot.get_channel(735206051703423036)
                if reviewchannel is None:
                    reviewchannel = await bot.fetch_channel(735206051703423036)
                if stored_id != 0: # they have a review
                    msgtoedit = await reviewchannel.fetch_message(stored_id)
                    await msgtoedit.edit(content=f"Heres a review from {str(self)} ({self.id}):```\n{reviewtext}```")
                    return ("`Success! You've edited your review.")
                else: # they dont have a review
                    thereview = await reviewchannel.send(f"Heres a review from {self.mention} ({self.id}):```\n{reviewtext}```")
                    await self.bot.db.execute("Update f_users set reviewmsgid = ? where userid = ?",(thereview.id,self.id,))
                    await self.bot.db.commit()
                        
                    return ("`Success! You can edit your review at any time using this command.`")
            else:
                return (f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
        except Exception as e:
            return (f"`{e}`")
        
    async def db_ban(self, reason):
        c = await self.bot.db.execute("SELECT * FROM f_users WHERE userid = ?",(self.id,))
        data = await c.fetchone()
        await self.bot.db.execute("INSERT INTO bannedusers VALUES (?,?,?)",(self.id,self.name,reason,))
        await self.bot.db.commit()
        return
    async def db_unban(self):
        c = await self.bot.db.execute("SELECT * FROM f_bans WHERE userid = ?",(self.id,))
        data = await c.fetchone()
        if data:
            await self.bot.db.execute("DELETE FROM bannedusers WHERE userid = ?",(self.id,))
            await self.bot.db.commit()
        if not data:
            #not in banned users, smh
            pass
        return
    
    async def update_profilecolor(self,hexstring):
        await self.bot.db.execute("UPDATE f_users SET hexcolor = ? WHERE userid = ?",(hexstring,self.id,))
        await self.bot.db.commit()
        return
    
    async def get_rod(self):
        c = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",(self.rod,))
        data = await c.fetchone()
        fish_range = self.rod * 3.163265306122449
        fish_range = round(fish_range, 1)
        return rod(self.bot, data, fish_range)

    async def get_net(self):
        c = await self.bot.db.execute("SELECT * FROM f_nets WHERE level = ?",(self.net,))
        data = await c.fetchone()
        return net(self.bot, data)

class rod:
    def __init__(self, bot, data, max_length):
        self.bot = bot
        self.level = int(data[0])
        self.name = str(data[1])
        self.cost = int(data[2])
        self.max_length = max_length
        
class net:
    def __init__(self, bot, data):
        self.bot = bot
        self.level = int(data[0])
        self.name = str(data[1])
        self.cost = int(data[2])
        self.minutes = int(data[3])

class server:
    def __init__(self, bot):
        self.bot = bot
# this is empty, because servers are going bye bye for the time being
# as an attempt towards a more classic and original fishy bot