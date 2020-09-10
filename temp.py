""" this is js btw
    rodUpgradeBar : function(rodLvl){ // returns a string
        let decimal = Math.round((rodLvl % 1)*10)
        let arrayBar = Array(10).fill("##",0,decimal)
        arrayBar.fill("__",decimal)
        return arrayBar.join('')
    }
}
"""
import math
import random, decimal
import time
# while True:

#     rodlvl = decimal.Decimal(random.randrange(100, 199))/100
#     print(rodlvl)
#     def rodUpgradebar(rodLvl):
#         return f"{'#' * (decimal := round(rodLvl % 1 * 40))}{'_' * (40 - decimal)}"
#     returned_upgradeBar = rodUpgradebar(rodlvl)
#     print(returned_upgradeBar)
#     time.sleep(1)
ex_xp =  4.592
ex_level = 0
new_xp = ex_xp / 100
print(new_xp)