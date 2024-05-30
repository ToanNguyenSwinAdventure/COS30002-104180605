from random import choice

class SmartBot(object):
    def update(self, gameinfo):
        # pass

        if gameinfo.my_planets and gameinfo.not_my_planets:
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)
            dest = min(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)
            
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, round(src.num_ships*0.75,0))
                print("\nSmart bot Being called")
                print("THIS IS SRC %s \nAND DEST %s" %( src, dest))
        
        
        # print("Number of ships: ",src.num_ships)

