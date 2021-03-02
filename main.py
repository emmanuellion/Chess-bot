import discord
from discord.ext import commands
import json
import random
import datetime

print("La partie va commencer !")
client = discord.Client()
token = "ODAxODc4NjAxMDM3MzgxNjYy.YAnFpA.6nlchzJK_wLaAERB0ntsYWWlTKo"
bot = commands.Bot(command_prefix="!")
cascade_mere = ['id', 'id_ban', 'players', 'poule_done', 'id_ban_refusal']


def add_account(ctx, arg1, arg2, load, id_member):
    id_member = str(id_member)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            res = 1
        else:
            b = {'id': id_member, 'name': arg2.lower(), 'score': 0.0, 'win': 0, 'loose': 0, 'tour': 0,
                 'poule': "A changer",
                 'disponible': True, 'color': "ffffff", 'author': ctx, 'cool-down_result': 0, 'cool-down_confirm': 0,
                 'current-opponent': "opponent", 'opponent': {}}
            load[arg1.lower()][arg2.lower()] = b
            res = 0
    else:
        b = {'score': 0.0, arg2.lower(): {'id': id_member, 'name': arg2.lower(), 'score': 0.0, 'win': 0, 'loose': 0,
                                          'tour': 0, 'poule': "A changer",
                                          'disponible': True, 'color': "ffffff", 'author': ctx, 'cool-down_result': 0,
                                          'cool-down_confirm': 0, 'current-opponent': "opponent", 'opponent': {}}}
        load[arg1.lower()] = b
        res = 0
    if id_member not in load['id']:
        load['id'][id_member] = id_member
    load['players'][arg2.lower()] = arg1.lower()
    with open('register.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    return res


def search(ctx, load):
    classe, player, tree = None, None, None
    for classe in load.keys():
        if classe not in cascade_mere:
            for player in load[classe].keys():
                if player != "score":
                    if load[classe][player]['author'] == str(ctx.author):
                        tree = load[classe][player]
                        break
            if tree is not None:
                break
    return str(classe), str(player), tree


@bot.event
async def on_ready():
    try:
        with open('register.json') as load:
            load = json.load(load)
    except FileNotFoundError:
        open('register.json', 'w')
        load = {}
    try:
        print(load['id'])
    except KeyError:
        load['id'] = {}
        for biblio in load.keys():
            if biblio not in ["id", "id_ban", "players", "poule_done"]:
                for player in load[biblio].keys():
                    if player != "score":
                        load['id'][load[biblio][player]['id']] = load[biblio][player]['id']
    try:
        print(load['id_ban'])
    except KeyError:
        load['id_ban'] = {}
    try:
        print(load['players'])
    except KeyError:
        load['players'] = {}
        for biblio in load.keys():
            if biblio not in cascade_mere:
                for player in load[biblio].keys():
                    if player != "score":
                        load['players'][player] = biblio
    try:
        print(load['poule_done'])
    except KeyError:
        load['poule_done'] = {}
        for biblio in load.keys():
            if biblio not in ["id", "id_ban", "players", "poule_done"]:
                for player in load[biblio].keys():
                    if player != "score":
                        if load[biblio][player]['poule'] != "A changer":
                            load['poule_done'][player] = load[biblio][player]['poule']
    try:
        print(load['id_ban_refusal'])
    except KeyError:
        load['id_ban_refusal'] = {}
    with open('register.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    #for i in range(0, 9):
    #    add_account("Mabule#2890", "classe_1", f"j_{i}", load, 414476886501228556)
    #for i in range(9, 16):
    #    add_account("Mabule#2890", "classe_2", f"j_{i}", load, 414476886501228556)
    #with open('register.json', "w") as f:
    #    json.dump(load, f, ensure_ascii=False, indent=4)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Joue aux échecs"))
    print("La partie commence ...")


@bot.command()
async def _help(ctx):
    embed = discord.Embed(title="**__Résumé des commandes__**", description="", color=0xf0f0f0)
    embed.add_field(
        name="**Pour une liste des commandes ainsi que leur description et explication d'utilisation, veuillez vous "
             "référer au site : **",
        value="***https://mabule.github.io/chess.com/index.html***", inline=False)
    await ctx.send(embed=embed)
    print("Commande _help")


@bot.command()
async def result(ctx, arg3, arg4, arg5, arg6):
    with open('register.json') as load:
        load = json.load(load)
    arg1, arg2, tree = search(ctx, load)
    if tree is not None:
        if arg4.lower() in load:
            if arg5.lower() in load[arg4.lower()]:
                delta = datetime.datetime.timestamp(datetime.datetime.now()) - tree['cool-down_result']
                if delta >= 60:
                    id1 = str(tree['id'])
                    id2 = str(load[arg4.lower()][arg5.lower()]['id'])
                    if id1 not in load['id_ban']:
                        load['id_ban'][id1] = id1
                        load['id_ban'][id1] = {"banned": id1, "class_banned": arg1.lower(), "name_banned": arg2.lower(),
                                               "to_confirm": id2, "class_confirm": arg4.lower(),
                                               "name_confirm": arg5.lower(), "score_id1": float(arg3),
                                               "score_id2": float(arg6)}
                        await ctx.send("Le résultat du match a bien était enregistré\nEn attente de la commande "
                                       f"`!match_result_confirm` de la part du second joueur (<@{load[arg4.lower()][arg5.lower()]['id']}>)...")
                    else:
                        await ctx.send("Vous ne pouvez pas envoyer plus de résultat car le dernier n'a toujours pas "
                                       "était confirmé")
                    tree['cool-down_result'] = datetime.datetime.timestamp(datetime.datetime.now())
                    with open('register.json', "w") as f:
                        json.dump(load, f, ensure_ascii=False, indent=4)
                else:
                    await ctx.send(f"Il faut attendre 60 secondes entre chaque commande result donc vous devez encore "
                                   f"attendre {round(60 - delta, 1)}")
            else:
                await ctx.send("Le prénom du joueur 2 n'a pas était trouvé dans la classe donnée")
        else:
            await ctx.send("La classe du joueur 2 n'existe pas")
    else:
        await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande result")


@bot.command()
async def result_confirm(ctx, member: discord.Member, member1: discord.Member, arg1):
    id1 = str(member1.id)
    with open('register.json') as load:
        load = json.load(load)
    trash, trash, tree = search(ctx, load)
    id2 = tree['id']
    if tree is not None:
        if id1 in load['id_ban']:
            if id2 == load['id_ban'][id1]['to_confirm']:
                banned = load[load['id_ban'][id1]['class_banned']][load['id_ban'][id1]['name_banned']]
                if arg1 == "y":
                    delta = datetime.datetime.timestamp(datetime.datetime.now()) - tree['cool-down_confirm']
                    if delta >= 60:
                        for classe in load.keys():
                            if classe not in cascade_mere:
                                for player in load[classe].keys():
                                    if player != "score":
                                        load[classe][player]['tour'] += 1
                        banned['score'] += float(load['id_ban'][id1]['score_id1'])
                        tree['score'] += float(load['id_ban'][id1]['score_id2'])
                        load[load['id_ban'][id1]['class_banned']]['score'] += float(load['id_ban'][id1]['score_id1'])
                        load[load['id_ban'][id1]['class_confirm']]['score'] += float(load['id_ban'][id1]['score_id2'])
                        embed = discord.Embed(title="VICTORY", description="", color=0x00ff00)
                        embed.add_field(name="\0",
                                        value=f"Résultat du match entre {member1} et {tree['author']} a été approuvé")
                        await member.send(embed=embed)
                        await ctx.send("Le résultat a bien était prit en compte !")
                        # -----------------------------------------------
                        if load['id_ban'][id1]['score_id1'] < load['id_ban'][id1]['score_id2']:
                            banned['loose'] += 1
                            tree['win'] += 1
                        else:
                            banned['win'] += 1
                            tree['loose'] += 1
                        joueur_trouve = 0
                        for key in load['players'].keys():
                            if load[load['players'][key]][key]['win'] == banned['win'] and load[load['players'][key]][key][
                                'poule'] == banned['poule'] and load[load['players'][key]][key][
                                'disponible'] == True and key not in banned['opponent']:
                                opponent = load[load['players'][key]][key]
                                if opponent['name'] != banned['name']:
                                    await ctx.send(
                                        f"Le joueur {banned['name']} <@{banned['id']}> a un nouveau match avec {opponent['name']} <@{opponent['id']}>")
                                    joueur_trouve = 1
                                    banned['disponible'] = False
                                    load[load['players'][key]][key]['disponible'] = False
                                    banned['current-opponent'] = load[load['players'][key]][key]['author']
                                    load[load['players'][key]][key]['current-opponent'] = banned['author']
                        if joueur_trouve == 0:
                            await ctx.send(
                                f"Aucun match n'a était trouvé pour {banned['name']} vous êtes donc mis en attente pour "
                                f"l'instant")
                            banned['current-opponent'] = "Nobody"
                        joueur_trouve = 0
                        for key in load['players'].keys():
                            if load[load['players'][key]][key]['win'] == tree['win'] and load[load['players'][key]][key][
                                'poule'] == tree['poule'] and load[load['players'][key]][key][
                                'disponible'] == True and key not in tree['opponent']:
                                opponent = load[load['players'][key]][key]
                                if opponent['name'] != tree['name']:
                                    await ctx.send(
                                        f"Le joueur {tree['name']}(<@{tree['id']}>) a un nouveau match avec {opponent['name']}(<@{opponent['id']}>)")
                                    joueur_trouve = 1
                                    tree['disponible'] = False
                                    load[load['players'][key]][key]['disponible'] = False
                                    tree['current-opponent'] = load[load['players'][key]][key]['author']
                                    load[load['players'][key]][key]['current-opponent'] = tree['author']
                        if joueur_trouve == 0:
                            await ctx.send(
                                f"Aucun match n'a était trouvé pour {tree['name']} vous êtes donc mis en attente pour "
                                f"l'instant")
                            tree['current-opponent'] = "Nobody"
                            # -----------------------------------------------
                        banned['opponent'][tree['name']] = tree['author']
                        tree['opponent'][banned['name']] = banned['author']
                        del load['id_ban'][id1]
                    else:
                        await ctx.send(f"Il faut attendre 60 secondes entre chaque commande result donc vous devez encore "
                                       f"attendre {round(60 - delta, 1)}")
                elif arg1 == "n":
                    load['id_ban_refusal'][id1] = load['id_ban'][id1]
                    del load['id_ban'][id1]
                    embed = discord.Embed(title="CA TOURNE MAL EXPLICATION !!!!", description="Refus de défaite",
                                          color=0xff0000)
                    embed.add_field(name="\0",
                                    value=f"Refus du résultat du match entre : {banned['name']} et {tree['name']}")
                    await member.send(embed=embed)
                    await ctx.send("Le résultat du dernier match a donc était contesté et l'information remontera à un "
                                   "administrateur pour régler le problème")
                else:
                    await ctx.send("Veuillez saisir un deuxième paramètre parmis les caractères 'y' ou 'n'")
                tree['cool-down_result'] = datetime.datetime.timestamp(datetime.datetime.now())
                with open('register.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
            else:
                await ctx.send(f"{tree['author']} vous n'êtiez pas l'adversaire de {member1}")
        else:
            await ctx.send("La personne mentionnée n'a pas donné de résultat récemment")
        with open('register.json', "w") as f:
            json.dump(load, f, ensure_ascii=False, indent=4)
    else:
        await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande result_confirm")


@bot.command()
async def score_player(ctx, arg1, arg2):
    with open('register.json') as f:
        load = json.load(f)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            embed = discord.Embed(title="Score de " + arg2, description="",
                                  color=int(load[arg1.lower()][arg2.lower()]['color'], 16))
            embed.add_field(name="Victoire : ", value=load[arg1.lower()][arg2.lower()]['win'], inline=False)
            embed.add_field(name="Défaite : ", value=load[arg1.lower][arg2.lower()]['loose'], inline=False)
            embed.add_field(name="Score : ", value=f"**{str(load[arg1.lower()][arg2.lower()]['score'])}**",
                            inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Joueur incorrecte")
    else:
        await ctx.send("Classe incorrecte")
    print("Commande score_player")


@bot.command()
async def score_class(ctx, arg1):
    with open('register.json') as f:
        load = json.load(f)
    if arg1.lower():
        embed = discord.Embed(title="Score de " + arg1, description="", color=0x990099)
        embed.add_field(name="Score : ", value=f"**{str(load[arg1.lower()]['score'])}**", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Classe incorrecte")
    print("Commande score_class")


@bot.command()
async def register(ctx, member: discord.Member, arg1, arg2):
    res = 2
    with open('register.json') as load:
        load = json.load(load)
    id_member = str(member.id)
    if str(ctx.author) != "Mabule#2890" and "oitzyhrr#1141" and "Toooom#2689":
        if id_member not in load['id']:
            if ctx.author == member:
                if arg1.lower() not in cascade_mere:
                    if arg2.lower() != "score":
                        res = add_account(str(ctx.author), arg1, arg2, load, id_member)
                    else:
                        await ctx.send("Veillez à ne pas donner de nom de ce type ;)")
                else:
                    await ctx.send(f"Veillez à ne pas donner un nom de classe parmi {cascade_mere}")
            else:
                    await ctx.send("Qu'est-ce que tu fous ?? Enregistre le compte pour toi pas pour un autre")
        else:
            await ctx.send("Désolé mais vous ne pouvez pas enregistrer plus de 1 participant")
    else:
        if arg1.lower() not in cascade_mere:
            if arg2.lower() != "score":
                res = add_account(str(ctx.author), arg1, arg2, load, id_member)
            else:
                await ctx.send("Veillez à ne pas donner de nom de ce type ;)")
        else:
            await ctx.send(f"Veillez à ne pas donner un nom de classe parmi {cascade_mere}")
    if res == 0:
        await ctx.send(f"Le participant {arg2} de la classe {arg1} est enregistré")
    elif res == 1:
        await ctx.send(f"Une erreur s'est produite car le participant {arg2} pour la classe {arg1} doit déjà exister")
    print("Commande register")
    print(cascade_mere)


@bot.command()
async def modif_class(ctx, arg3):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        arg1, arg2, tree = search(ctx, load)
        if tree is not None:
            if arg3.lower() in load.keys() and arg3.lower() not in cascade_mere:
                print(tree)
                if str(arg3.lower()) != str(arg1.lower()):
                    load[arg3.lower()][arg2] = tree
                    load['players'][arg2] = arg3.lower()
                    del load[arg1][arg2]
                    with open('register.json', "w") as f:
                        json.dump(load, f, ensure_ascii=False, indent=4)
                    await ctx.send(
                        f"Le changement de la classe {arg1} pour la classe {arg3} du joueur {arg2} a bien était éffectué")
                else:
                    await ctx.send(
                        "La classe mentionnée pour le changement est la même que celle que vous avez actuellement")
            else:
                await ctx.send("Veuillez renseigner une classe d'arrivée existante :)")
        else:
            await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande modif_class")


@bot.command()
async def modif_player(ctx, arg3):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        arg1, arg2, tree = search(ctx, load)
        if tree is not None:
            if arg2 != arg3.lower():
                del load[arg1][arg2]
                load[arg1][arg3.lower()] = tree
                del load['players'][arg2]
                load['players'][arg3.lower()] = arg1
                with open('register.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
                await ctx.send(
                    f"Le changement de prénom de {arg2} pour {arg3} dans la classe {arg1} a bien été éffectué")
            else:
                await ctx.send("Les deux noms sont identiques, donc le changement est inutile (toutes les chaines "
                               "sont converties à leur équivalent en minuscule)")
        else:
            await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande modif_player")


@bot.command()
async def admin(ctx):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        await ctx.send(load)
    print("Commande admin")


@bot.command()
async def list_player(ctx):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        embed = discord.Embed(title="Liste des joueurs et de leur classe", description="", color=0x9400D3)
        for key in load['players'].keys():
            embed.add_field(name="Joueur : __" + key + "__ dans la classe : ",
                            value="**__" + load['players'][key] + "__\n\n**", inline=False)
        await ctx.send(embed=embed)
    print("Commande list_player")


@bot.command()
async def delete_class(ctx, arg):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        if arg.lower() in load:
            player_list = []
            id_create_player = []
            for player in load[arg.lower()].keys():
                if player != 'score':
                    player_list.append(player)
                    id_create_player.append(load[arg.lower()][player]['id'])
            del load[arg.lower()]
            for player in list(load['players'].keys()):
                if player in player_list:
                    del load['players'][player]
            for id_key in list(load['id'].keys()):
                if id_key in id_create_player:
                    del load['id'][id_key]
            with open('register.json', "w") as f:
                json.dump(load, f, ensure_ascii=False, indent=4)
            await ctx.send(f"L'effacement de la classe {arg.lower()} s'est bien éffectué")
        else:
            await ctx.send("La classe renseignée n'existe pas ¯\_(ツ)_/¯")
    print("Commande delete_class")


@bot.command()
async def delete_player(ctx, arg1, arg2):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
            if arg1.lower() in load:
                if arg2.lower() in load[arg1.lower()]:
                    player = load[arg1.lower()][arg2.lower()]
                    load[arg1.lower()]['score'] -= player['score']
                    del load['players'][arg2.lower()]
                    if arg2.lower() in load['poule_done']:
                        del load['poule_done'][arg2.lower()]
                    if player['id'] in load['id_ban']:
                        del load['id_ban'][player['id']]
                    del load['id'][player['id']]
                    del load[arg1.lower()][arg2.lower()]
                    await ctx.send(f"Le joueur {arg2.lower()} a bien été éffacé")
                else:
                    await ctx.send(f"Le joueur montionné n'a pas été trouvé dans la classe {arg1.lower()}")
            else:
                await ctx.send("La classe mentionnée n'existe pas")
        with open('register.json', "w") as f:
            json.dump(load, f, ensure_ascii=False, indent=4)
    print("Commande delete_player")


@bot.command()
async def reset(ctx):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        for key in list(load.keys()):
            del load[key]
        with open('register.json', "w") as f:
            json.dump(load, f, ensure_ascii=False, indent=4)
        await ctx.send("Le fichier a bien été réinitialisé")
    print("Commande reset")


@bot.command()
async def rebuild(ctx):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        for list in cascade_mere:
            load[list] = {}
        with open('register.json', "w") as f:
            json.dump(load, f, ensure_ascii=False, indent=4)
        await ctx.send("Le fichier a bien été rebuild")
    print("Commande rebuild")


@bot.command()
async def poule(ctx):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        all_player_list = []
        for biblio in load.keys():
            if biblio not in cascade_mere:
                for key in load[biblio].keys():
                    if key != "score":
                        all_player_list.append(key)
        if len(all_player_list) % 8 == 0:  # and len(all_player_list) == 32
            list_poule = ['A', 'B']
            for letter in list_poule:
                same_poule = []
                j = random.randint(0, len(all_player_list) - 1)
                for i in range(0, 8):
                    player = all_player_list[j]
                    if player in load['poule_done']:
                        while player in load['poule_done']:
                            j = random.randint(0, len(all_player_list) - 1)
                            player = all_player_list[j]
                    same_poule.append(player)
                    load['poule_done'][player] = letter
                for player in same_poule:
                    class_player = load['players'][player]
                    load[class_player][player]['poule'] = letter
            with open('register.json', "w") as f:
                json.dump(load, f, ensure_ascii=False, indent=4)
            await ctx.send("L'affectation aux poules à bien était éffectué")
        else:
            await ctx.send(
                "L'adressage des poules aux participants n'est pas réalisable car le nombre total de participant n'est pas divisable par poule de 8")
    print("Commande poule")


@bot.command()
async def edit_color_profil(ctx, arg3):
    with open('register.json') as load:
        load = json.load(load)
    arg1, arg2, tree = search(ctx, load)
    if tree is not None:
        if len(arg3) <= 6:
            tree['color'] = "0x" + arg3.lower()
            with open('register.json', "w") as f:
                json.dump(load, f, ensure_ascii=False, indent=4)
            await ctx.send("Votre couleur a bien était modifiée")
        else:
            await ctx.send("Veuillez saisir un code héxadécimal valide (ex : ffffff => couleur noir)")
    else:
        await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande edit_color_profil")


@bot.command()
async def show_profil(ctx):
    with open('register.json') as load:
        load = json.load(load)
    arg1, arg2, player = search(ctx, load)
    if player is not None:
        embed = discord.Embed(title=f"Profil du joueur {arg2}", description="", color=int(player['color'], 16))
        embed.add_field(name="Classe", value=arg1, inline=False)
        embed.add_field(name="Poule", value=player['poule'], inline=False)
        print(player.keys())
        embed.add_field(name="Adversaire actuel", value=player['current-opponent'], inline=False)
        embed.add_field(name="Score total", value=player['score'], inline=False)
        embed.add_field(name="Nombre de match gagné", value=player['win'], inline=False)
        embed.add_field(name="Nombre de match perdu", value=player['loose'], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Vous ne vous êtes pas enregistré en tant que joueur")
    print("Commande show_profil")


bot.run(token)
