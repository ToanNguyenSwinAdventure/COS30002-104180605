from random import choice

class Rando(object):
    def update(self, gameinfo):
        # pass
        

        if gameinfo.my_planets and gameinfo.not_my_planets:
            src = choice(list(gameinfo.my_planets.values()))
            dest = choice(list(gameinfo.not_my_planets.values()))
            print("THIS IS SRC %s \nAND DEST %s" %( src, dest))

            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, round(src.num_ships*0.75,0))
        
        print("\nRANDO bot Being called")
        # print("Number of ships: ",src.num_ships)
