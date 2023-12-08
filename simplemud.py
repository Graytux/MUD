#!/usr/bin/env python
import os
import time
import pickle
import random
# import de la classe MudServer 
from mudserver import MudServer


# Définition des différentes pièces
rooms = {
    "Hall": {
        "description": "Vous etes dans le Hall d'acceuil",
        "exits": {"nord": "Couloir NORD", "sud": "Couloir SUD", "est": "Couloir EST", "ouest": "Couloir OUEST"},
    },
    "Couloir NORD": {
        "description": "Vous etes dans le Couloir NORD",
        "exits": {"sud": "Hall", "porte": "Arene NORD"},
    },
    "Arene NORD": {
        "description": "Vous etes dans l arene du NORD",
        "exits": {"porte": "Couloir NORD"},
    },
    "Couloir SUD": {
        "description": "Vous etes dans le Couloir SUD",
        "exits": {"nord": "Hall", "porte": "Arene SUD"},
    },
    "Arene SUD": {
        "description": "Vous etes dans l arene du SUD",
        "exits": {"porte": "Couloir SUD"},
    },
    "Couloir EST": {
        "description": "Vous etes dans le Couloir EST",
        "exits": {"ouest": "Hall", "porte": "Arene EST"},
    },
    "Arene EST": {
        "description": "Vous etes dans l arene de l EST",
        "exits": {"porte": "Couloir EST"},
    },
    "Couloir OUEST": {
        "description": "Vous etes dans le Couloir OUEST",
        "exits": {"est": "Hall", "porte": "Arene OUEST"},
    },
    "Arene OUEST": {
        "description": "Vous etes dans l arene de l OUEST",
        "exits": {"porte": "Couloir OUEST"},
    },
}


# Varible de stockage des joueurs
players = {}
regen = 0
# Démarre le serveur
mud = MudServer()

# Boucle Principale (infinie) - stop avec [Ctrl + C]
while True:

    # Pause pendant 1/5 de seconde sur chaque boucle, afin de ne pas utiliser constamment 100% du temps CPU
    time.sleep(0.2)

    # 'regen' des joueurs
    regen = regen + 1
    if regen >=120:
        regen = 0
        for pid, pl in players.items():
            if players[pid]["PVa"] < players[pid]["PVm"]:
                players[pid]["PVa"] = players[pid]["PVa"] + 1
                mud.send_message(pid, "##############################")
                mud.send_message(pid, "[DIEU] : vous rend 1 point de vie")
                mud.send_message(pid, "{} - PV:{}/{}".format(players[id]["name"], players[id]["PVa"], players[id]["PVm"]))
                mud.send_message(pid, "##############################")

    # 'update' doit être appelé dans la boucle pour que le jeu continue de fonctionner et nous donne des informations à jour
    mud.update()


    # Passage de tous les joueurs nouvellement connectés
    for id in mud.get_new_players():
        # Ajout du nouveau joueur au dictionnaire, en notant qu'il n'a pas encore été nommé.
        # La clé du dictionnaire est le numéro d'identification du joueur. Définition initiale de leur 'room' sur None => jusqu'à ce qu'ils aient saisi un nom.
        players[id] = {
            "name": None,
            "room": None,
            "titre": None,
            "PVa": 10,
            "PVm": 10,
            "FOR": 1,
            "END": 1,
            "CBT": 1,
            "xpCBT": 0,
            "equip": {
                "arme": {
                    "name": "mains nues",
                    "desc": "Pas d'armes, juste vos mains pour vous battre",
                    "degt": 3,    
                },
                "armure": {
                    "name": "Haillons",
                    "desc": "Vetement de tres mauvaise qualite",
                    "prot": 1,    
                },
            },
            "honor": 0,
            "money": 0,
        }

        mud.send_message(id, "- Quel est votre nom ?")
    
    # go through any recently disconnected players
    for id in mud.get_disconnected_players():
        if id not in players:
            continue
        for pid, pl in players.items():
            mud.send_message(pid, "\033[1;34m{}\033[1;0m quitte le jeu !".format(players[id]["name"]))
            # Sauvegarde PJ
            with open("./data/pj/{}.sav".format(players[id]["name"]), 'wb') as f:
                pickle.dump(players[id],f)
            f.close()
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():
        if id not in players:
            continue
        if players[id]["name"] is None:
            players[id]["name"] = command
            players[id]["room"] = "Hall"
        # Envoi au nouveau joueur d'un 'prompt question' pour son nom
        ## A revoir pour demande si nouveau PJ ou déjà un compte
            if os.path.isfile("./data/pj/{}.sav".format(players[id]["name"])) is False:
                mud.send_message(id, "+ Creation du compte {}.".format(players[id]["name"]))
                # Sauvegarde PJ
                with open("./data/pj/{}.sav".format(players[id]["name"]), 'wb') as f:
                    pickle.dump(players[id],f)
                f.close()
            elif os.path.isfile("./data/pj/{}.sav".format(players[id]["name"])) is True:
                mud.send_message(id, "+ Le compte {} existe.".format(players[id]["name"]))
                # Chargement PJ
                with open("./data/pj/{}.sav".format(players[id]["name"]), 'rb') as f:
                    players[id]=pickle.load(f)
                f.close()
                
            if players[id]["name"] != None:
                # Envoi à tous le nom du joueur qui viens de se connecter
                for pid, pl in players.items():
                    mud.send_message(pid, "\033[1;34m{}\033[1;0m entre dans le jeu !".format(players[id]["name"]))
                # Message de bienvenue au nouveau joueur connecter
                mud.send_message(id, "Bienvenue \033[1;34m{}\033[1;0m".format(players[id]["name"]))
                # Envoi au joueur qui viens de se connecter le rappel de la commande 'aide'
                mud.send_message(id, "\033[1;30mTaper 'aide' pour la liste des commandes\033[1;0m")
                # Envoi au joueur qui viens de se connecter la description de sa 'room'
                mud.send_message(id, rooms[players[id]["room"]]["description"])

        # 'aide' command
        elif command == "aide":
            # send the player back the list of possible commands
            mud.send_message(id, "Commandes:")
            mud.send_message(id, "- regarder         - Examine les environs")
            mud.send_message(id, "- dire <message>   - Dire quelque chose a voix haute, ")
            mud.send_message(id, "- aller <xxx>      - Se deplacer vers <xxx>, e.g. 'aller dehors'")
            mud.send_message(id, "- QUITTER le jeu : [Ctrl + $] go prompt [telnet>] taper 'quit'")

        # 'cheat' command
        elif command == "cheat":
            avant = players[id][params]
            players[id][params] = players[id][params] + 1
            mud.send_message(id, "CHEAT : vous augmenter {} de {} a {}".format(params, avant, players[id][params])) 

        # 'combat' command
        elif command == "cbt":
            for pid, pl in players.items():
                if players[pid]["name"] == params:
                    mud.send_message(id, "+ attaque sur {}".format(players[pid]["name"]))
                    mud.send_message(pid, "+ {} vous attaque".format(players[id]["name"]))
                    seuil = 50 + (players[pid]["CBT"] - players[id]["CBT"])
                    jet = random.randint(1, 100)
                    if jet >= seuil:
                        mud.send_message(id, "-+ vous touchez - {} > {}".format(jet, seuil))
                        mud.send_message(pid, "-+ {} vous touche".format(players[id]["name"]))
                        if (players[pid]["CBT"] - players[id]["CBT"]) >= 0:
                            gainxpcbt = 1 + (players[pid]["CBT"] - players[id]["CBT"])
                        else:
                            gainxpcbt = 1
                        players[id]["xpCBT"] = players[id]["xpCBT"] + gainxpcbt
                        if players[id]["xpCBT"] > players[id]["CBT"]:
                            players[id]["xpCBT"] = 0
                            players[id]["CBT"] = players[id]["CBT"] + 1
                            mud.send_message(id, "-+ vous passez au niveau {} en combat".format(players[id]["CBT"]))
                        tmpdegt = random.randint(1, players[id]["equip"]["arme"]["degt"]) + players[id]["FOR"]
                        tmpprot = players[pid]["equip"]["armure"]["prot"] + players[pid]["END"]
                        degat = tmpdegt - tmpprot
                        mud.send_message(id, "-+ vous infligez {} degats [att({}) - def({})]".format(degat, tmpdegt, tmpprot))
                        mud.send_message(pid, "-+ vous subissez {} degats dut a l'arme : {}".format(degat, players[id]["equip"]["arme"]["name"]))
                        players[pid]["PVa"] = players[pid]["PVa"] - degat
                        if players[pid]["PVa"] <= 0:
                            mud.send_message(id, "-+ vous tuez {}".format(players[pid]["name"]))
                            mud.send_message(pid, "-+ vous etes mort de la main de {}".format(players[id]["name"]))
                            if (players[pid]["CBT"] - players[id]["CBT"]) >= 0:
                                gainhonor = 1 + (players[pid]["CBT"] - players[id]["CBT"])
                            else:
                                gainhonor = 1
                            players[id]["honor"] = players[id]["honor"] + gainhonor
                            mud.send_message(id, "-+ vous gagnez {} d'honneur".format(gainhonor))
                            players[pid]["room"] = "Hall"
                            players[pid]["PVa"] = players[pid]["PVm"]
                            mud.send_message(pid, "[DIEU] : vous ramene a la vie dans le hall")
                    else:
                        mud.send_message(id, "-+ vous ratez - {} > {}".format(jet, seuil))
                        mud.send_message(pid, "-+ {} vous rate".format(players[id]["name"]))

        # 'dire' command
        elif command == "dire":
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    if players[id]["titre"] != None:
                        mud.send_message(pid, "\033[1;34m{} {}\033[1;0m dit {}\n".format(players[id]["titre"], players[id]["name"], params))
                    else:
                        mud.send_message(pid, "\033[1;34m{}\033[1;0m dit {}\n".format(players[id]["name"], params))

        # 'regarder' command
        elif command == "regarder":
            # store the player's current room
            rm = rooms[players[id]["room"]]
            # send the player back the description of their current room
            mud.send_message(id, rm["description"])
            playershere = []
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    if players[pid]["name"] is not None:
                            playershere.append(players[pid]["name"])
            # send player a message containing the list of players in the room
            mud.send_message(id, "Il y a : {}".format(", ".join(playershere)))
            # send player a message containing the list of exits from this room
            mud.send_message(id, "Les sorties sont: \033[1;34m{}\033[1;0m\n".format(", ".join(rm["exits"])))

        # 'stat' command
        elif command == 'stat':
            mud.send_message(id, "Stat : {}".format(players[id]))

        # 'aller' command
        elif command == "aller":
            # store the exit name
            ex = params.lower()
            # store the player's current room
            rm = rooms[players[id]["room"]]
            # if the specified exit is found in the room's exits list
            if ex in rm["exits"]:
                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, "{} va vers '{}'".format(players[id]["name"], ex))
                # update the player's current room to the one the exit leads to
                last = players[id]["room"]
                players[id]["room"] = rm["exits"][ex]
                rm = rooms[players[id]["room"]]
                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        mud.send_message(pid,"{} arrive depuis '{}'".format(players[id]["name"], last))
                # send the player a message telling them where they are now
                mud.send_message(id, "Vous arrivez a '{}'\n".format(players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                mud.send_message(id, "Sortie inconnue '{}'\n".format(ex))

        # 'unknown' command
        else:
            # send back an 'unknown command' message
            mud.send_message(id, "Commande inconnue '{}'\n".format(command))
        
        # prompt joueur
        mud.send_message(id, "##############################")
        mud.send_message(id, "{} - PV:{}/{}".format(players[id]["name"], players[id]["PVa"], players[id]["PVm"]))
        mud.send_message(id, "##############################")