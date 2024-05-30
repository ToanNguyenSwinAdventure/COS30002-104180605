import time
import random

states = ["attack", "dodging", " chasing", "healing", "seeking"]

current_state = "seeking"

alive = True
range = 5
health = 100
power = 10

while alive:
    print("\n")
    #State Seeking
    if current_state == "seeking":
        print("Seeking for enemy...")
        chance_of_enemy = random.randint(0,1)
        power_of_enemy = random.randint(0,20)

        if (chance_of_enemy == 1) and (power_of_enemy < power):
            print("Enemy in range, ready to attack")
            current_state = "attack"
        else:
            print("Enemy in range, but I'm too weak...")
            current_state = "dodging"

    #State Attack
    if current_state == "attack":
        print("Attacking enemy...\nHahaha I'm Win!!! Just empower myself stronger")

        chance_of_enemy_running = random.randint(0,5)
        if chance_of_enemy_running == 1:
            print("Enemy running...")
            current_state = "chasing"

        if power <= 20:
            power += 1
        if power % 5 ==0:
            range +=1
        health = health * ((power - power_of_enemy)/power)

        # for i in range(0,3):
        #     print (".")
        #     time.sleep(0.1)
        print("Attacking enemy successfully")
        current_state = "healing"


    #State Dodging
    if current_state == "dodging":
        if random.randint(0,1) == 1:
            print("Runnnnnnnnnnnn...")
            print("Running from enemy successfully")
            current_state = "seeking"
        else:
            print("Enemy catching me...\nI'm Dead!!!!")
            alive = False

    #State Healing
    if current_state == "healing":
        print("Healing...")
        health = 100
        print("Healing successfully")
        current_state = "seeking"

    #State Chasing
    if current_state == "chasing":
        if random.randint(0,1) == 1:
            print("You not gonna run away this time")
            current_state = "attacking"
        else:
            print("You are lucky!")
            current_state = "seeking"

            