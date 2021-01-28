import aiosqlite
import math
import typing
from discord import User as DiscordUser
from cogs.utils.botchecks import FishNotFound

class fish:
    def __init__(self, data):
        if not data:
            raise FishNotFound()
        self.oid = data[0]
        self.image_url = data[1]
        self.rarity = float(data[2])
        self.db_position = data[3]
        self.original_length = float(data[4])
        self.modified_length = self.original_length
        self.name = data[5]
    
    async def coin_value(self, rod_level):
        #fishes.filter(fish => fish.fishLength >= ((0.8) * Math.floor(player.activeRod)) && fish.fishLength <= Math.floor(player.activeRod))
        # this^ is javascript
        #now i gotta replicate it in python
        max_length = (0.8) * math.floor(rod_level)
        cur = await self.bot.db.execute("SELECT * FROM fishes WHERE fishlength <= ? AND fishlength <= ? ORDER BY RANDOM();",(max_length, math.floor(rod_level)))
        

class player:
    def __init__(self, bot, data):
        self.bot = bot
        self.id = int(data[0])
        self.name = str(data[1])
        self.guild_id = int(data[2])
        self.coins = float(data[3])
        self.trophy_oid = str(data[4])
        self.trophy_rod_level = int(data[5])
        self.hex_color = str(data[6])
        self.review_message_id = int(data[7])
        
    @staticmethod
    async def create(bot, user: DiscordUser):
        player = bot.usercheck(user.id)
        if player:
            return False
        
        await bot.db.execute("INSERT INTO f_users VALUES (?, ?, None, 1, 0, None, 0, None, 0)",(user.id, user.name,))
        await bot.db.commit()
        return True

    async def get_rod_level(self):
        c = await self.bot.db.execute("SELECT level FROM f_rods WHERE userid = ?",(self.id,))
        lvl = await c.fetchone()
        try: return lvl[0]
        except: return None # this shouldnt happen but eh
    ##Now for updates n stuff
    async def update_collection(self,oid):
        c = await self.bot.db.execute("SELECT * FROM f_collections WHERE userid = ? AND oid = ?",(self.id, oid,))
        if (await c.fetchone()):   
            await self.bot.db.execute("INSERT INTO f_collections VALUES (?, ?)",(self.id,))
        else: pass
        await self.bot.db.commit()
    async def check_trophy(self, caughtoid):
        usersid = self.id
        c = await self.bot.db.execute("SELECT * FROM fishes WHERE oid = ?",(caughtoid,))
        data2 = await c.fetchone()
        c = await self.bot.db.execute("SELECT * FROM fishes WHERE oid = ?",(self.trophy_oid,))
        data = await c.fetchone()
        await self.bot.db.commit()
        try:
            FishLengthFromTrophy = data[4]
            FishLengthJustCaught = data2[4]
            if float(FishLengthFromTrophy) < float(FishLengthJustCaught):
                await self.bot.db.execute("Update f_users set trophyoid = ? where userid = ?", (caughtoid, usersid,))
                await self.bot.db.commit()
                return
            else:
                #No updating needed
                return
        except:
            await self.bot.db.execute("Update f_users set trophyoid = ? where userid = ?",(caughtoid,usersid,))
            await self.bot.db.commit()
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

class server:
    def __init__(self, bot):
        self.bot = bot

# this is empty, because servers are going bye bye for the time being
# as an attempt towards a more classic and original fishy bot