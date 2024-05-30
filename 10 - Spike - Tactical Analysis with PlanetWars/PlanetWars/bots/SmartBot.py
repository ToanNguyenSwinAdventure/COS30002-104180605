from random import choice

class SmartBot(object):
    def update(self, gameinfo):
        # This bot simply send 75% ships from the planet have most ships to the lowest ship planet
        if gameinfo.my_planets and gameinfo.not_my_planets:
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)
            dest = min(gameinfo.not_my_planets.values(), key=lambda p: p.num_ships)
            
            # Only send ships if number of ships greater than 10
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, round(src.num_ships*0.75))
                print("\nSmart bot Being called")
                print("THIS IS SRC {} \nAND DEST {}" .format( src, dest))
        

