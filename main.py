import discord
from discord.ext import commands
import json
import random
import datetime
import time
import math
import os

print("La partie va commencer !")
client = discord.Client()
token = "ODAxODc4NjAxMDM3MzgxNjYy.YAnFpA.S6G6v5qXQFG60kDO8ZmO38xuiJQ"
bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
cascade_mere_bis = ["id", "id_ban", "players", "poule_done", "id_ban_refusal", "sondage", "autorisation_register"]
cascade_mere = []
all_poule = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'i']
list_poule = []
my_ping = 'Mabule#0001' #Veiller à bien mettre à jour mon tag discord
try:
    load = open('main.json')
except FileNotFoundError:
    open('main.json', 'w')
    load = {"cascade_mere": {}}
    for key in cascade_mere_bis:
        load['cascade_mere'][key] = key
    with open('main.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)


def add_account(ctx, arg1, arg2, load, id_member):
    id_member = str(id_member)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            res = 1
        else:
            b = {'id': id_member, 'name': arg2.lower(), 'score': 0.0, 'win': 0, 'loose': 0, 'tour': 0,
                 'poule': "A changer",
                 'disponible': True, 'color': "ffffff", 'author': str(ctx.author), 'cool-down_result': 0,
                 'cool-down_confirm': 0,
                 'current-opponent': "opponent", 'opponent': {}}
            load[arg1.lower()][arg2.lower()] = b
            res = 0
    else:
        b = {'score': 0.0, arg2.lower(): {'id': id_member, 'name': arg2.lower(), 'score': 0.0, 'win': 0, 'loose': 0,
                                          'tour': 0, 'poule': "A changer",
                                          'disponible': True, 'color': "ffffff", 'author': str(ctx.author),
                                          'cool-down_result': 0,
                                          'cool-down_confirm': 0, 'current-opponent': "opponent", 'opponent': {}}}
        load[arg1.lower()] = b
        res = 0
    if id_member not in load['id']:
        load['id'][id_member] = id_member
    load['players'][arg2.lower()] = arg1.lower()
    push(ctx, load)
    return res


def search(ctx, load):
    classe, player, tree = None, None, None
    for classe in get_class(str(ctx.guild)):
        for player in load[classe]:
            if player != "score":
                if load[classe][player]['author'] == str(ctx.author):
                    tree = load[classe][player]
                    break
            if tree is not None:
                break
    return str(classe), str(player), tree


def next_match(load, banned, tree, id1):
    joueur_trouve = 0
    opponent = {}
    if load['id_ban'][id1]['score_id1'] > load['id_ban'][id1]['score_id2']:
        banned['win'] += 1
        tree['loose'] += 1
        winner = 1
    else:
        banned['loose'] += 1
        tree['win'] += 1
        winner = -1
    if winner == 1:
        player = banned
        looser = tree
    else:
        player = tree
        looser = banned
    for key in load['players']:
        if load[load['players'][key]][key]['poule'] == player['poule'] and load[load['players'][key]][key][
            'disponible'] is True:  # load[load['players'][key]][key]['win'] == player['win'] and
            opponent = load[load['players'][key]][key]
            if opponent['name'] != player['name']:
                joueur_trouve = 1
                player['disponible'] = False
                load[load['players'][key]][key]['disponible'] = False
                player['current-opponent'] = load[load['players'][key]][key]['author']
                load[load['players'][key]][key]['current-opponent'] = player['author']
                break
    if joueur_trouve == 0:
        player['current-opponent'] = "Nobody"
        player['disponible'] = True
    looser['disponible'] = False
    looser['current-opponent'] = "Vous êtes éliminé"
    looser['cool-down_result'] = 9999999999
    looser['cool-down_confirm'] = 9999999999
    return joueur_trouve, player, looser, opponent, winner


def build(load):
    for liste in cascade_mere_bis:
        load[liste] = {}
    return load


def get_admins(ctx):
    with open('main.json') as load:
        load = json.load(load)
    list_admins = load[ctx]['admins']
    return list_admins


def get_class(ctx):
    with open('main.json') as load:
        load = json.load(load)
    list_class = load[ctx]['class']
    if list_class == {}:
        return None
    else:
        return list_class


def get(ctx):
    with open(str(ctx.guild) + '.json') as load:
        load = json.load(load)
    return load


def push(ctx, load):
    with open(str(ctx.guild) + '.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)


def end_of_match(banned, id1, confirm, load):
    banned['score'] += float(load['id_ban'][id1]['score_id1'])
    confirm['score'] += float(load['id_ban'][id1]['score_id2'])
    load[load['id_ban'][id1]['class_banned']]['score'] += float(load['id_ban'][id1]['score_id1'])
    load[load['id_ban'][id1]['class_confirm']]['score'] += float(load['id_ban'][id1]['score_id2'])
    joueur_trouve, player, looser, opponent, winner = next_match(load, banned, confirm, id1)
    return joueur_trouve, player, looser, opponent, winner


@bot.event
async def on_ready():
    global cascade_mere
    with open('main.json') as load:
        load = json.load(load)
    for it in load['cascade_mere']:
        cascade_mere.append(it)
    files = os.listdir("./")
    all_file = []
    for file in list(files):
        z = file.split('.')[-1]
        if z == "json":
            all_file.append(file)
    for file in all_file:
        if file != "main.json":
            with open(file) as load:
                load = json.load(load)
            try:
                temp = load['id']
            except KeyError:
                load['id'] = {}
                for biblio in load:
                    if biblio not in cascade_mere:
                        for player in load[biblio]:
                            if player != "score":
                                load['id'][load[biblio][player]['id']] = load[biblio][player]['id']
            try:
                temp = load['id_ban']
            except KeyError:
                load['id_ban'] = {}
            try:
                temp = load['players']
            except KeyError:
                load['players'] = {}
                for biblio in load:
                    if biblio not in cascade_mere:
                        for player in load[biblio]:
                            if player != "score":
                                load['players'][player] = biblio
            try:
                temp = load['poule_done']
            except KeyError:
                load['poule_done'] = {}
                for biblio in load:
                    if biblio not in cascade_mere:
                        for player in load[biblio]:
                            if player != "score":
                                if load[biblio][player]['poule'] != "A changer":
                                    load['poule_done'][player] = load[biblio][player]['poule']
            try:
                temp = load['id_ban_refusal']
            except KeyError:
                load['id_ban_refusal'] = {}
            try:
                temp = load['sondage']
            except KeyError:
                load['sondage'] = {}
            with open(file, "w") as f:
                json.dump(load, f, ensure_ascii=False, indent=4)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!help"))
    print("La partie commence ...")


@bot.event
async def on_guild_join(ctx):
    guild = str(ctx)
    with open('main.json') as load:
        load = json.load(load)
    load['cascade_mere'][guild] = guild
    load[guild] = {"admins": {my_ping: True}, "class": {}}
    with open('main.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    open(guild + '.json', 'w')
    load = {}
    load = {"server_title": guild}
    load = build(load)
    load["autorisation_register"] = True
    with open(guild + '.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    cascade_mere.append(guild)


@bot.event
async def on_guild_remove(ctx):
    guild = str(ctx)
    with open('main.json') as load:
        load = json.load(load)
    del load['cascade_mere'][guild]
    del load[guild]
    with open('main.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    os.remove(guild + '.json')


@bot.command()  # admin command
async def add_admin(ctx, member: discord.Member = None, king='xxxxx'):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if member is not None:
            with open('main.json') as load:
                load = json.load(load)
            if load[str(ctx.guild)]['admins'][str(ctx.author)]:
                if str(member) not in get_admins(str(ctx.guild)):
                    if king == 'xxxxx':
                        load[str(ctx.guild)]['admins'][str(member)] = False
                        await ctx.send(f"La personne <@{member.id}> est bien devenue admin")
                    else:
                        load[str(ctx.guild)]['admins'][str(member)] = True
                        await ctx.send(f"La personne <@{member.id}> est bien devenue super admin")
                    with open('main.json', "w") as f:
                        json.dump(load, f, ensure_ascii=False, indent=4)
                else:
                    await ctx.send(f"La personne <@{member.id}> est déjà admin")
            else:
                await ctx.send("Vous n'êtes pas super admin, seul un super admin peut rajouter d'autres administrateur")
        else:
            await ctx.send("⚠ Veuillez renseigner comme premier paramètre le ping discord de la personne à mettre à "
                           "administrateur et si vous voulez la mettre super admin veuillez renseigner un 2nd "
                           "paramètre quelconque")
    print("Commande add_admin")


@bot.command()  # admin command
async def delete_admin(ctx, member: discord.Member):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if str(member) != my_ping:
            with open('main.json') as load:
                load = json.load(load)
            if str(member) in get_admins(str(ctx.guild)):
                del load[str(ctx.guild)]['admins'][str(member)]
                await ctx.send(f"La personne <@{member.id}> n'est plus admin")
                with open('main.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
            else:
                await ctx.send(f"La personne <@{member.id}> n'était pas admin")
        else:
            await ctx.send("Vous ne pouvez pas effacer le développeur des supers admins")
    print("Commande delete_admin")


@bot.command()  # admin command
async def add_class(ctx, classe=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if classe is not None:
            with open('main.json') as load:
                load = json.load(load)
            if classe not in get_class(str(ctx.guild)):
                load[str(ctx.guild)]['class'][classe] = classe
                await ctx.send(f"La classe {classe} a bien été rajoutée")
                with open('main.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
            else:
                await ctx.send("La classe est déjà présente")
        else:
            await ctx.send("⚠ Veuillez donner en paramètre le nom de la classe à rajouter")
    print("Commande add_class")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="__Résumé des commandes__", description="", color=0xf0f0f0)
    embed.add_field(
        name="Pour une liste des commandes ainsi que leur description et explication d'utilisation, veuillez vous "
             "référer au site : ",
        value="***https://mabule.github.io/chess.com/index.html***", inline=False)
    await ctx.send(embed=embed)
    print("Commande help")


@bot.command()
async def result(ctx, arg3=None, arg4=None, arg5=None, arg6=None):
    load = get(ctx)
    arg1, arg2, tree = search(ctx, load)
    if tree is not None:
        if arg3 is not None:
            if arg4 is not None:
                if arg5 is not None:
                    if arg6 is not None:
                        if arg4.lower() in load:
                            if arg5.lower() in load[arg4.lower()]:
                                if load[arg4.lower()][arg5.lower()]['author'] == tree['current-opponent']:
                                    already_see = 0
                                    for result in load['id_ban']:
                                        if tree['id'] == result['to_confirm']:
                                            already_see = 1
                                    if already_see == 0:
                                        delta = datetime.datetime.timestamp(datetime.datetime.now()) - tree[
                                            'cool-down_result']
                                        if delta >= 60:
                                            if tree['current-opponent'] != "Nobody":
                                                id1 = str(tree['id'])
                                                id2 = str(load[arg4.lower()][arg5.lower()]['id'])
                                                if id1 not in load['id_ban']:
                                                    load['id_ban'][id1] = id1
                                                    load['id_ban'][id1] = {"banned": id1, "class_banned": arg1.lower(),
                                                                           "name_banned": arg2.lower(),
                                                                           "to_confirm": id2,
                                                                           "class_confirm": arg4.lower(),
                                                                           "name_confirm": arg5.lower(),
                                                                           "score_id1": float(arg3),
                                                                           "score_id2": float(arg6)}
                                                    await ctx.send(
                                                        "Le résultat du match a bien été enregistré\nEn attente de la commande "
                                                        f"`!match_result_confirm` de la part du second joueur (<@{load[arg4.lower()][arg5.lower()]['id']}>)...")
                                                else:
                                                    await ctx.send(
                                                        "Vous ne pouvez pas envoyer plus de résultat car le dernier n'a toujours pas "
                                                        "été confirmé")
                                            else:
                                                await ctx.send(
                                                    "Vous ne pouvez pas déposer de résultat car vous n'avez pas d'adversaire")
                                            tree['cool-down_result'] = datetime.datetime.timestamp(
                                                datetime.datetime.now())
                                            push(ctx, load)
                                        else:
                                            await ctx.send(
                                                f"Il faut attendre 60 secondes entre chaque commande `!result` donc vous devez encore "
                                                f"attendre {round(60 - delta, 1)} secondes")
                                    else:
                                        await ctx.send(
                                            "Ton adversaire a déjà déposé un résultat, confirme le en suivant la forme: \n "
                                            "`!result_confirm @Toooom#2689 <ping discord de ton adversaire> <'y' pour "
                                            "confirmer, 'n' pour refuser>`")
                                else:
                                    await ctx.send(
                                        f"{load[arg4.lower()][arg5.lower()]['name']} n'est pas votre adversaire")
                            else:
                                await ctx.send("Le prénom du joueur 2 n'a pas été trouvé dans la classe donnée")
                        else:
                            await ctx.send("La classe du joueur 2 n'existe pas")
                    else:
                        await ctx.send("⚠ Veuillez renseigner le score de votre adversaire")
                else:
                    await ctx.send("⚠ Veuillez renseigner en 3ème paramètre le nom de votre avdversaire et son score")
            else:
                await ctx.send("⚠ Veuillez renseigner en 2nd paramètre la classe de votre adversaire, son nom et son "
                               "score")
        else:
            await ctx.send("⚠ Veuillez renseigner en paramètre votre score, la classe de votre adversaire, le nom de "
                           "votre adversaire et son score")
    else:
        await ctx.send("⚠ Veuillez créer un compte avant de faire cette commande")
    print("Commande result")


@bot.command()
async def result_confirm(ctx, member: discord.Member = None, member1: discord.Member = None, arg1=None):
    id1 = str(member1.id)
    load = get(ctx)
    trash, trash, tree = search(ctx, load)
    id2 = tree['id']
    if tree is not None:
        if member is not None:
            if member1 is not None:
                if arg1 is not None:
                    if str(member) == "Toooom#2689":
                        if id1 in load['id_ban']:
                            if id2 == load['id_ban'][id1]['to_confirm'] or str(ctx.author) in get_admins(ctx):
                                banned = load[load['id_ban'][id1]['class_banned']][load['id_ban'][id1]['name_banned']]
                                if arg1 == "y":
                                    delta = datetime.datetime.timestamp(datetime.datetime.now()) - tree[
                                        'cool-down_confirm']
                                    if delta >= 60:
                                        for classe in get_class(ctx):
                                            for player in load[classe]:
                                                if player != "score":
                                                    if load[classe][player]['loose'] == 0:
                                                        load[classe][player]['tour'] += 1
                                        (joueur_trouve, player, looser, opponent, winner) = end_of_match(banned, id1,
                                                                                                         tree, load)
                                        embed = discord.Embed(title="VICTORY", description="", color=0x00ff00)
                                        embed.add_field(name="\0",
                                                        value=f"Résultat du match entre {member1} et {tree['author']} a été approuvé")
                                        await member.send(embed=embed)
                                        await ctx.send("Le résultat a bien été pris en compte !")
                                        if joueur_trouve == 1:
                                            await ctx.send(
                                                f"Le joueur {player['name']} <@{player['id']}> a un nouveau match avec {opponent['name']} <@{opponent['id']}>")
                                        else:
                                            await ctx.send(
                                                f"Aucun match n'a été trouvé pour {player['name']} vous êtes donc mis en attente "
                                                f"pour l'instant")
                                        await ctx.send(f"Désolé à toi {looser['name']} mais tu es éliminé du tournoi !")
                                        banned['opponent'][tree['name']] = tree['author']
                                        tree['opponent'][banned['name']] = banned['author']
                                        del load['id_ban'][id1]
                                    else:
                                        await ctx.send(
                                            f"Il faut attendre 60 secondes entre chaque commande `!result_confirm` donc vous devez encore "
                                            f"attendre {round(60 - delta, 1)} secondes")
                                elif arg1 == "n":
                                    load['id_ban_refusal'][id1] = load['id_ban'][id1]
                                    del load['id_ban'][id1]
                                    embed = discord.Embed(title="CA TOURNE MAL EXPLICATION !!!!",
                                                          description="Refu de défaite",
                                                          color=0xff0000)
                                    embed.add_field(name="\0",
                                                    value=f"Refu du résultat du match entre : {banned['name']} et {tree['name']}")
                                    await member.send(embed=embed)
                                    await ctx.send(
                                        "Le résultat du dernier match a donc été contesté et l'information remontera à un "
                                        "administrateur pour régler le problème")
                                else:
                                    await ctx.send(
                                        "Veuillez saisir un deuxième paramètre parmi les caractères 'y' ou 'n'")
                                tree['cool-down_result'] = datetime.datetime.timestamp(datetime.datetime.now())
                                push(ctx, load)
                            else:
                                await ctx.send(f"{tree['author']} vous n'êtiez pas l'adversaire de {member1}")
                        else:
                            await ctx.send("La personne mentionnée n'a pas donnée de résultat récemment")
                        push(ctx, load)
                    else:
                        await ctx.send("Veuillez mentionner l'administrateur Toooom#2689 et non quelqu'un d'autre")
                else:
                    await ctx.send("⚠ Veuillez renseigner un caractère ('y' ou 'n') pour confirmer le résultat ou le rejeter")
            else:
                await ctx.send("⚠ Veuillez renseigner en 2nd paramètre le ping discord de la personne ayant déposée le résultat et un caractère ('y' ou 'n') pour confirmer le résultat ou le rejeter")
        else:
            await ctx.send("⚠ Veuillez renseigner comme paramètre le ping discord de Tom, le ping discord la personne ayant déposée le résultat et un caractère ('y' ou 'n') pour confirmer le résultat ou le rejeter")
    else:
        await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande result_confirm")


@bot.command()
async def confirm_refusal(ctx, member: discord.Member = None, arg=None):
    if member is not None:
        if arg is not None:
            id1 = str(member.id)
            load = get(ctx)
            if str(ctx.author) in get_admins(ctx):
                if arg == 'y':
                    if id1 in load['id_ban_refusall']:
                        banned = load[load['id_banrefusal'][id1]['class_banned']][
                            load['id_ban_refusal'][id1]['name_banned']]
                        tree = load[load['id_ban_refusal'][id1]['class_confirm']][
                            load['id_ban_refusal'][id1]['name_confirm']]
                        banned['score'] += float(load['id_ban_refusal'][id1]['score_id1'])
                        tree['score'] += float(load['id_ban_refusal'][id1]['score_id2'])
                        load[load['id_ban_refusal'][id1]['class_banned']]['score'] += float(
                            load['id_ban_refusal'][id1]['score_id1'])
                        load[load['id_ban_refusal'][id1]['class_confirm']]['score'] += float(
                            load['id_ban_refusal'][id1]['score_id2'])
                        if load['id_ban_refusal'][id1]['score_id1'] < load['id_ban_refusal'][id1]['score_id2']:
                            banned['loose'] += 1
                            tree['win'] += 1
                        else:
                            banned['win'] += 1
                            tree['loose'] += 1
                        await ctx.send("Le résultat a bien été pris en compte")
                        joueur_trouve, player, looser, opponent, winner = next_match(load, banned, tree, id1)
                        if joueur_trouve == 1:
                            await ctx.send(
                                f"Le joueur {player['name']} <@{player['id']}> a un nouveau match avec {opponent['name']} <@{opponent['id']}>")
                        else:
                            await ctx.send(
                                f"Aucun match n'a été trouvé pour {player['name']} vous êtes donc mis en attente pour "
                                "l'instant")
                        await ctx.send(f"Désolé à toi {looser['name']} mais tu es éliminé du tournoi !")
                        banned['opponent'][tree['name']] = tree['author']
                        tree['opponent'][banned['name']] = banned['author']
                        del load['id_ban_refusal'][id1]
                    else:
                        await ctx.send("⚠ Aucun match n'a été déposé pour ce joueur")
                else:
                    del load['id_ban_refusal'][id1]
                    await ctx.send("Le résultat a bien été éffacé")
                push(ctx, load)
        else:
            await ctx.send("⚠ Veuillez saisir en 2nd paramètre un caractère ('y' ou 'n') pour accepter le résultat du match ou pour annuler le résultat déposé")
    else:
        await ctx.send("⚠ Veuillez saisir en paramètre le ping discord de la personne ayant donnée le résultat du "
                       "match et un caractère ('y' ou 'n') pour accepter le résultat du match ou pour annuler le résultat déposé")
    print("Commande confirm_refusal")


# @bot.command()
# async def score_player(ctx, arg1, arg2):
#    with open(str(ctx.guild)+'.json') as f:
#        load = json.load(f)
#    if arg1.lower() in load:
#       if arg2.lower() in load[arg1.lower()]:
#            embed = discord.Embed(title="Score de " + arg2.lower(), description="",
#                                  color=int(load[arg1.lower()][arg2.lower()]['color'], 16))
#            embed.add_field(name="Victoire : ", value=load[arg1.lower()][arg2.lower()]['win'], inline=False)
#           embed.add_field(name="Défaite : ", value=load[arg1.lower()][arg2.lower()]['loose'], inline=False)
#            embed.add_field(name="Score : ", value=load[arg1.lower()][arg2.lower()]['score'],
#                            inline=False)
#            await ctx.send(embed=embed)
#        else:
#            await ctx.send("Aucun joueur de ce nom n'a été trouvé dans cette classe")
#    else:
#        await ctx.send("Veuillez saisir une classe existante")
#    print("Commande score_player")


@bot.command()
async def score_class(ctx, arg1=None):
    if arg1 is not None:
        load = get(ctx)
        if arg1.lower() in load:
            embed = discord.Embed(title="Score de " + arg1.lower(), description="", color=0x990099)
            embed.add_field(name="Score : ", value=load[arg1.lower()]['score'], inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Veuillez saisir une classe existante")
    else:
        await ctx.send("⚠ Veuillez saisir en paramètre la classe dont vous voulez connaitre le score")
    print("Commande score_class")


@bot.command()
async def register(ctx, member: discord.Member = None, arg1=None, arg2=None):
    if member is not None:
        if arg1 is not None:
            if arg2 is not None:
                res = 3
                load = get(ctx)
                if load['autorisation_register']:
                    id_member = str(member.id)
                    if str(ctx.author) not in get_admins(str(ctx.guild)):
                        if id_member not in load['id']:
                            if ctx.author == member:
                                if arg1.lower() in get_class(str(ctx.guild)):
                                    if arg2.lower() != "score":
                                        res = add_account(ctx, arg1, arg2, load, id_member)
                                    else:
                                        await ctx.send("Veillez à ne pas donner de nom de ce type ;)")
                                else:
                                    if get_class(str(ctx.guild)) is None:
                                        await ctx.send("Il faudrait d'abord commencer par renseigner la liste des clases permises via la commande !add_class par des admins")
                                    else:
                                        await ctx.send(f"Veuillez saisir une classe parmi la liste suivante : {get_class(str(ctx.guild))}")
                            else:
                                await ctx.send("Veuillez enregistrer un compte pour vous et pas pour quelqu'un d'autre")
                        else:
                            await ctx.send("Désolé mais vous ne pouvez pas enregistrer plus de 1 participant")
                    else:
                        if arg1.lower() in get_class(str(ctx.guild)):
                            if arg2.lower() != "score":
                                res = add_account(ctx, arg1, arg2, load, id_member)
                            else:
                                await ctx.send("Veillez à ne pas donner de nom de ce type ;)")
                        else:
                            await ctx.send(
                                f"Veuillez saisir une classe parmi la liste suivante : {get_class(str(ctx.guild))}")
                    if res == 0:
                        await ctx.send(f"Le participant {arg2} de la classe {arg1} est enregistré")
                    elif res == 1:
                        await ctx.send(
                            f"Une erreur s'est produite car le participant {arg2} pour la classe {arg1} existe déjà")
                else:
                    await ctx.send("Désolé mais vous ne pouvez plus vous enregistrer car la compétition a commencée")
            else:
                await ctx.send("⚠ Veuillez saisir 3ème paramètre le nom du joueur")
        else:
            await ctx.send("⚠ Veuillez saisir en 2nd paramètre la classe du joueur et en 3ème son nom")
    else:
        await ctx.send(
            "⚠ Veuillez saisir en paramètre le ping discord du joueur s'inscrivant, la classe du joueur et son nom")
    print("Commande register")


@bot.command()  # admin command
async def modif_class(ctx, arg1=None, arg2=None, arg3=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if arg1 is not None:
            if arg2 is not None:
                if arg3 is not None:
                    load = get(ctx)
                    if arg1.lower() in load:
                        if arg2.lower() in load[arg1.lower()]:
                            if arg3.lower() in load and arg3.lower() in get_class(ctx):
                                if arg3.lower() != arg1.lower():
                                    player = load[arg1.lower()][arg2.lower()]
                                    load[arg3.lower()][arg2.lower()] = player
                                    load['players'][arg2.lower()] = arg3.lower()
                                    del load[arg1.lower()][arg2.lower()]
                                    push(ctx, load)
                                    await ctx.send(
                                        f"Le changement de la classe {arg1} pour la classe {arg3} du joueur {arg2} a bien été éffectué")
                                else:
                                    await ctx.send(
                                        "La classe mentionnée pour le changement est la même que celle que vous "
                                        "avez actuellement")
                            else:
                                await ctx.send("⚠ Veuillez renseigner une classe d'arrivée existante")
                        else:
                            await ctx.send("⚠ Aucun joueur de ce nom n'a été trouvé dans cette classe")
                    else:
                        await ctx.send("⚠ Veuillez saisir une classe existante")
                else:
                    await ctx.send("⚠ Veuillez saisir en 3ème paramètre la nouvelle classe")
            else:
                await ctx.send("⚠ Veuillez saisir en 2nd aparamètre le nom du joueur à changer de classe et en 3ème "
                               "la nouvelle classe")
        else:
            await ctx.send("⚠ Veuillez saisir en paramètre la classe de base, le nom du joueur et la nouvelle classe")
    print("Commande modif_class")


@bot.command()  # admin command
async def modif_player(ctx, arg1=None, arg2=None, arg3=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if arg1 is not None:
            if arg2 is not None:
                if arg3 is not None:
                    load = get(ctx)
                    if arg1.lower() in load:
                        if arg2.lower() in load[arg1.lower()]:
                            player = load[arg1.lower()][arg2.lower()]
                            if arg3.lower() != player['name']:
                                del load[arg1.lower()][arg2.lower()]
                                player['name'] = arg3.lower()
                                load[arg1.lower()][arg3.lower()] = player
                                del load['players'][arg2.lower()]
                                load['players'][arg3.lower()] = arg1.lower()
                                push(ctx, load)
                                await ctx.send(
                                    f"Le changement de prénom de {arg2} pour {arg3} dans la classe {arg1} a bien été éffectué")
                            else:
                                await ctx.send(
                                    "Les deux noms sont identiques, donc le changement est inutile (toutes les chaînes de caractères"
                                    "sont converties à leur équivalent en minuscule)")
                        else:
                            await ctx.send("⚠ Aucun joueur de ce nom n'a été trouvé dans cette classe")
                    else:
                        await ctx.send("⚠ Veuillez saisir une classe existante")
                else:
                    await ctx.send("⚠ Veuillez saisir en 3ème paramètre le nouveau nom")
            else:
                await ctx.send("⚠ Veuillez saisir en 2nd paramètre le nom actuel du joueur et en 3ème son futur nom")
        else:
            await ctx.send("⚠ Veuillez saisir en paramètre la classe du joueur, son nom actuel et son futur nom")
    print("Commande modif_player")


@bot.command()  # admin command
async def admin(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        try:
            await ctx.send(get(ctx))
        except discord.errors.HTTPException:
            await ctx.send("⚠ Il y a trop d'information pour qu'elles puissent être envoyées")
    print("Commande admin")


@bot.command()  # admin command
async def list_player(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        load = get(ctx)
        embed = discord.Embed(title="Liste des joueurs et de leur classe", description="", color=0xeeeeee)
        for key in load['players']:
            embed.add_field(name="Joueur : __" + key + "__ dans la classe : ",
                            value="**__" + load['players'][key] + "__\n\n**", inline=False)
        await ctx.send(embed=embed)
    print("Commande list_player")


@bot.command()  # admin command
async def delete_class(ctx, arg=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if arg is not None:
            load = get(ctx)
            if arg.lower() in load:
                player_list = []
                id_create_player = []
                for player in load[arg.lower()]:
                    if player != 'score':
                        player_list.append(player)
                        id_create_player.append(load[arg.lower()][player]['id'])
                del load[arg.lower()]
                for player in list(load['players']):
                    if player in player_list:
                        del load['players'][player]
                for id_key in list(load['id']):
                    if id_key in id_create_player:
                        del load['id'][id_key]
                for id_key in list(load['id_ban']):
                    if id_key in id_create_player:
                        del load['id_ban'][id_key]
                for id_key in list(load['id_ban_refusal']):
                    if id_key in id_create_player:
                        del load['id_ban_refusal'][id_key]
                push(ctx, load)
                with open('main.json') as load:
                    load = json.load(load)
                del load[str(ctx.guild)]['class'][arg.lower()]
                with open('main.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
                await ctx.send(f"L'effacement de la classe {arg.lower()} s'est bien éffectué")
            else:
                await ctx.send("⚠ La classe renseignée n'existe pas")
        else:
            await ctx.send("⚠ Veuillez saisir le nom de la classe à effacer")
    print("Commande delete_class")


@bot.command()  # admin command
async def delete_player(ctx, arg1=None, arg2=None):
    if str(ctx.author) in get_admins(ctx):
        if arg1 is not None:
            if arg2 is not None:
                load = get(ctx)
                if arg1.lower() in load:
                    if arg2.lower() in load[arg1.lower()]:
                        player = load[arg1.lower()][arg2.lower()]
                        load[arg1.lower()]['score'] -= player['score']
                        del load['players'][arg2.lower()]
                        if arg2.lower() in load['poule_done']:
                            del load['poule_done'][arg2.lower()]
                        if player['id'] in load['id_ban']:
                            del load['id_ban'][player['id']]
                        if player['id'] in load['id_ban_refusal']:
                            del load['id_ban_refusal'][player['id']]
                        del load['id'][player['id']]
                        del load[arg1.lower()][arg2.lower()]
                        push(ctx, load)
                        await ctx.send(f"Le joueur {arg2.lower()} a bien été éffacé")
                    else:
                        await ctx.send(f"⚠ Le joueur mentionné n'a pas été trouvé dans la classe {arg1.lower()}")
                else:
                    await ctx.send("⚠ La classe mentionnée n'existe pas")
            else:
                await ctx.send("⚠ Veuillez saisir le nom d'un joueur")
        else:
            await ctx.send("⚠ La classe du joueur suivit de son nom")
    print("Commande delete_player")


@bot.command()  # admin command
async def restart(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        load = get(ctx)
        for key in list(load):
            del load[key]
        load = build(load)
        push(ctx, load)
        with open('main.json') as load:
            load = json.load(load)
        for classe in load[str(ctx.guild)]['class']:
            del load[str(ctx.guild)][classe]
        with open('main.json', "w") as f:
            json.dump(load, f, ensure_ascii=False, indent=4)
        await ctx.send("Le fichier a bien été réinitialisé")
    print("Commande reset")


@bot.command()
async def edit_color_profil(ctx, arg3=None):
    load = get(ctx)
    arg1, arg2, tree = search(ctx, load)
    if tree is not None:
        if arg3 is not None:

            if len(arg3) <= 6:
                tree['color'] = "0x" + arg3.lower()
                push(ctx, load)
                await ctx.send("Votre couleur a bien été modifiée")
            else:
                await ctx.send("⚠ Veuillez saisir un code héxadécimal valide (ex : ffffff => couleur noir)")
        else:
            await ctx.send("⚠ Veuillez saisir une couleur en héxadécimale (ex : ffffff => couleur noir)")
    else:
        await ctx.send("⚠ Veuillez créer un compte avant de faire cette commande")
    print("Commande edit_color_profil")


@bot.command()
async def show_profile(ctx, member: discord.Member = None):
    load = get(ctx)
    if member is not None:
        ctx.author = member
        arg1, arg2, player = search(ctx, load)
    else:
        arg1, arg2, player = search(ctx, load)
    if player is not None:
        embed = discord.Embed(title=f"Profil du joueur {arg2}", description="", color=int(player['color'], 16))
        embed.add_field(name="Classe", value=arg1, inline=False)
        embed.add_field(name="Poule", value=player['poule'], inline=False)
        embed.add_field(name="Adversaire actuel", value=player['current-opponent'], inline=False)
        embed.add_field(name="Score total", value=player['score'], inline=False)
        embed.add_field(name="Nombre de match gagné", value=player['win'], inline=False)
        embed.add_field(name="Nombre de match perdu", value=player['loose'], inline=False)
        if player['loose'] >= 1:
            embed.add_field(name="Rang définitif", value=f"{player['tour']} ème", inline=False)
        else:
            embed.add_field(name="Rang actuel", value=f"{player['tour']} ème", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Veuillez créer un compte avant de faire cette commande")
    print("Commande show_profil")


@bot.command()  # admin command
async def show_class(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        load = get(ctx)
        embed = discord.Embed(title="Affichage des joueurs dans leur classe", description="", color=0x228B22)
        for biblio in load:
            if biblio not in cascade_mere:
                all_key = load[biblio]
                for key in all_key:
                    if key != "score":
                        embed.add_field(name=f"Classe  {biblio}", value=key, inline=False)
        await ctx.send(embed=embed)
    print("Commande show_class")


reaction = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']


@bot.command()  # admin command
async def create_sondage(ctx, quest=None, poss1=None, poss2=None, poss3=None, poss4=None, poss5=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if quest is not None:
            if (poss1 is not None) and (poss2 is not None):
                load = get(ctx)
                embed = discord.Embed(title="Sondage", description=f"{quest}", color=0x6F00F6)
                embed.add_field(name="Réagissez avec l'emoji 1️⃣ pour:", value=poss1, inline=False)
                embed.add_field(name="Réagissez avec l'emoji 2️⃣ pour:", value=poss2, inline=False)
                contenu = {'question': quest, 'nb_vote': 0, 'voter': {}, 'answer1': poss1, 'answer2': poss2,
                           'nb_answer1': 0, 'nb_answer2': 0}
                nb_rep = 2
                if poss3 is not None:
                    contenu['answer3'] = poss3
                    contenu['nb_answer3'] = 0
                    embed.add_field(name="Réagissez avec l'emoji 3️⃣ pour:", value=poss3, inline=False)
                    nb_rep = 3
                    if poss4 is not None:
                        contenu['answer4'] = poss4
                        contenu['nb_answer4'] = 0
                        embed.add_field(name="Réagissez avec l'emoji 4️⃣ pour:", value=poss4, inline=False)
                        nb_rep = 4
                        if poss5 is not None:
                            contenu['answer5'] = poss5
                            contenu['nb_answer5'] = 0
                            embed.add_field(name="Réagissez avec l'emoji 5️⃣ pour:", value=poss5, inline=False)
                            nb_rep = 5
                await ctx.send(embed=embed)
                time.sleep(1)
                for message in await ctx.message.channel.history(limit=1).flatten():
                    id_sondage = message.id
                    break
                contenu['nb_rep'] = nb_rep
                load['sondage'][id_sondage] = contenu
                push(ctx, load)
            else:
                await ctx.send("Veuillez saisir au moins 2 choix de réponse et 5 maximum")
        else:
            await ctx.send("Veuillez Saisir une question suivit d'au minimum 2 choix et au maximum 5 choix")
    print("Commande create_sondage")


@bot.event
async def on_raw_reaction_add(payload):
    #--------------------------------------------------------------------------------
    if str(payload.message_id) == "839637284369727518":
        admin_role = bot.get_guild(payload.guild_id).roles
        for role in admin_role:
            if str(role.name) == "🌺 Membre":
                ad = role
        member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
        await member.add_roles(ad)
        
    # --------------------------------------------------------------------------------
    if payload.user_id != "801878601037381662":
        guild = bot.get_guild(payload.guild_id)
        with open(str(guild) + '.json') as load:
            load = json.load(load)
        ctx = bot.get_channel(payload.channel_id)
        member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
        try:
            sondage = load['sondage'][str(payload.message_id)]
            choice = str(payload.emoji)
            if choice in reaction:
              if str(member) not in sondage['voter']:
                sondage['nb_vote'] += 1
                sondage['voter'][str(member)] = str(member)
                round = 1
                for emote in reaction:
                  if emote == choice:
                    sondage['nb_answer' + str(round)] += 1
                    round += 1
                    push(ctx, load)
              else:
                await ctx.send("⚠ Vous ne pouvez donner votre avis que pour 1 choix⚠ ")
                for mess in await ctx.history(limit=30).flatten():
                  if str(mess.id) == str(payload.message_id):
                    message = mess
                    break
                await message.clear_reaction(choice)
                time.sleep(2)
                await ctx.purge(limit=1)
            else:
              list_react = []
              i = 0
              while i < sondage['nb_rep']:
                list_react.append(reaction[i])
                i += 1
              await ctx.send("Veuillez réagir avec les emojs : " + str(list_react))
              for mess in await ctx.history(limit=30).flatten():
                if str(mess.id) == str(payload.message_id):
                  message = mess
                  break
              await message.clear_reaction(choice)
              time.sleep(2)
              await ctx.purge(limit=1)
        except KeyError:
          pass
    print("Event reaction added")


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    with open(str(guild) + '.json') as load:
        load = json.load(load)
    ctx = bot.get_channel(payload.channel_id)
    member = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
    try:
      sondage = load['sondage'][str(payload.message_id)]
      choice = str(payload.emoji)
      sondage['nb_vote'] -= 1
      del sondage['voter'][str(member)]
      round = 1
      for emote in reaction:
        if emote == choice:
          sondage['nb_answer' + str(round)] -= 1
          break
        round += 1
      push(ctx, load)
    except KeyError:
      pass
    print("Event reaction removed")


@bot.command()  # admin command
async def delete_sondage(ctx, id_sondage=None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if id_sondage is not None:
            load = get(ctx)
            if id_sondage in load['sondage']:
                message_finded = False
                for message in await ctx.message.channel.history(limit=1000).flatten():
                    if str(message.id) == str(id_sondage):
                        ctx.message = message
                        await ctx.message.delete()
                        message_finded = True
                        break
                if not message_finded:
                    await ctx.send("⚠ Le sondage ne se situe pas dans ce channel, veuillez refaire la commande dans le "
                                   "channel où se situe le sondage ⚠")
                    time.sleep(2)
                    await ctx.purge(limit=1)
                else:
                    del load['sondage'][id_sondage]
                    await ctx.send("✅ Le sondage a bien été éffacé ✅\n**Ce message s'effacera dans 3 secondes**")
                    push(ctx, load)
                    time.sleep(2)
                    await ctx.channel.purge(limit=2)
            else:
                await ctx.send(
                    f"⚠ L'id du message n'existe pas actuellement voici l'id des sondages existants : {load['sondage']}")
        else:
            await ctx.send("⚠ Veuillez renseigner l'id du message correspondant au sondage")
    print("Commande delete_sondage")


@bot.command()  # admin command
async def clear(ctx, nb_mess=1):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        try:
            await ctx.channel.purge(limit=int(nb_mess) + 1)
        except ValueError:
            await ctx.send("Veuillez saisir un nombre")
    print("Commande clear")


@bot.command()  # admin command
async def start(ctx, nb_poule=0):
    global list_poule
    if str(ctx.author) in get_admins(str(ctx.guild)):
        load = get(ctx)
        nb_poule = int(nb_poule)
        if len(load['players']) % nb_poule == 0:
            list_poule = []
            for i in range(0, nb_poule):
                list_poule.append(all_poule[i])
            poule(ctx, len(load['players']), nb_poule)
            load = get(ctx)
            casey = []
            for letter in list_poule:
                same_poule = []
                for player in load['poule_done']:
                    if load['poule_done'][player] == letter:
                        same_poule.append(player)
                nobody = []
                for player in same_poule:
                    player = load[load['players'][player]][player]
                    if player['current-opponent'] == "opponent":
                        j = random.randint(0, len(same_poule) - 1)
                        maybe = load[load['players'][same_poule[j]]][same_poule[j]]
                        while maybe['author'] in casey:
                            j = random.randint(0, len(same_poule) - 1)
                            maybe = load[load['players'][same_poule[j]]][same_poule[j]]
                        if (player['author'] != maybe['author']) and (maybe['current-opponent'] == "opponent"):
                            player['current-opponent'] = maybe['author']
                            player['disponible'] = False
                            maybe['current-opponent'] = player['author']
                            maybe['disponible'] = False
                            print(f"{player['name']}<=>{maybe['name']}")
                            casey.append(player['name'])
                            casey.append(maybe['name'])
                print(same_poule)
                for player in same_poule:
                    if player not in casey:
                        nobody.append(player)
                if len(nobody) == 2:
                    player = nobody[0]
                    player = load[load['players'][player]][player]
                    maybe = nobody[1]
                    maybe = load[load['players'][maybe]][maybe]
                    player['current-opponent'] = maybe['author']
                    player['disponible'] = False
                    maybe['current-opponent'] = player['author']
                    maybe['disponible'] = False
                    print(f"{player['name']}//\\\\{maybe['name']}")
                    casey.append(player['name'])
                    casey.append(maybe['name'])
            load['autorisation_register'] = False
            push(ctx, load)
            await ctx.send("Tous les joueurs ont leur match !!\n**QUE LA COMPÉTITION COMMENCE !!!!**")
        else:
            await ctx.send("⚠ Il faut que le nombre de poule soit un multiple du nombre total de joueur\n"
                           f"Nombre de poule : {nb_poule}\n"
                           f"Nombre de joueur : {len(load['players'])}")
    print("Commande start")


def poule(ctx, size, nb_poule):
    global list_poule
    load = get(ctx)
    all_player_list = []
    for player in load['players']:
        all_player_list.append(player)
    for letter in list_poule:
        same_poule = []
        j = random.randint(0, len(all_player_list) - 1)
        for i in range(0, math.floor(size / nb_poule)):
            player = all_player_list[j]
            while player in load['poule_done']:
                j = random.randint(0, len(all_player_list) - 1)
                player = all_player_list[j]
            same_poule.append(player)
            load['poule_done'][player] = letter
        for player in same_poule:
            class_player = load['players'][player]
            load[class_player][player]['poule'] = letter
    push(ctx, load)


@bot.command()  # admin command
async def show_poule(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        load = get(ctx)
        if load['poule_done'] != {}:
            embed = discord.Embed(title="Répartition des joueurs dans les poules", description='', color=0xffff00)
            for player in load['poule_done']:
                embed.add_field(name=f"Joueur **{player}** dans : ", value=load['poule_done'][player], inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Aucun joueur n'est répartit dans une poule")
    print("Commande show_poule")


@bot.command()  # admin command
async def alive(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        with open('main.json') as load:
            load = json.load(load)
        main = load[str(ctx.guild)]['class']
        load = get(ctx)
        embed = discord.Embed(title="Joueurs encore en vie :", description='', color=0xffff00)
        for classe in main:
            for player in load[classe]:
                if player != "score":
                    if load[classe][player]['current-opponent'] != "Vous êtes éliminé":
                        embed.add_field(name=f"**{player}**", value=load[classe][player]['poule'], inline=False)
        await ctx.send(embed=embed)
    print("Commande alive")


@bot.command()  # admin command
async def isDead(ctx):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        with open('main.json') as load:
            load = json.load(load)
        main = load[str(ctx.guild)]['class']
        load = get(ctx)
        embed = discord.Embed(title="Joueurs morts :", description='', color=0xffff00)
        for classe in main:
            for player in load[classe]:
                if player != "score":
                    if load[classe][player]['current-opponent'] == "Vous êtes éliminé":
                        embed.add_field(name=f"**{player}**", value=load[classe][player]['poule'], inline=False)
        await ctx.send(embed=embed)
    print("Commande isDead")


@bot.command()  # admin command
async def destroy(ctx, member: discord.Member = None, member2: discord.Member = None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if member is not None:
            if member2 is not None:
                load = get(ctx)
                ctx.author = member
                classe, name, tree = search(ctx, load)
                ctx.author = member2
                classe2, name2, tree2 = search(ctx, load)
                if tree is not None:
                    if tree2 is not None:
                        if tree['current-opponent'] == str(member2):
                            alea = random.randint(1, 2)
                            if alea == 1:
                                id1 = tree['id']
                                arg1 = classe
                                arg2 = name
                                id2 = tree2['id']
                                arg4 = classe2
                                arg5 = name2
                                arg3 = 2
                                arg6 = 0
                                banned = tree
                                confirm = tree2
                            else:
                                id1 = tree2['id']
                                arg1 = classe2
                                arg2 = name2
                                id2 = tree['id']
                                arg4 = classe
                                arg5 = name
                                arg3 = 0
                                arg6 = 2
                                banned = tree2
                                confirm = tree
                            load['id_ban'][id1] = id1
                            load['id_ban'][id1] = {"banned": id1, "class_banned": arg1.lower(),
                                                   "name_banned": arg2.lower(),
                                                   "to_confirm": id2, "class_confirm": arg4.lower(),
                                                   "name_confirm": arg5.lower(), "score_id1": float(arg3),
                                                   "score_id2": float(arg6)}
                            for classe in get_class(ctx):
                                for player in load[classe]:
                                    if player != "score":
                                        if load[classe][player]['loose'] == 0:
                                            load[classe][player]['tour'] += 1
                            (joueur_trouve, player, looser, opponent, winner) = end_of_match(banned, id1, tree, load)
                            if joueur_trouve == 1:
                                await ctx.send(
                                    f"Le joueur {player['name']} <@{player['id']}> a un nouveau match avec {opponent['name']} <@{opponent['id']}>")
                            else:
                                await ctx.send(
                                    f"Aucun match n'a été trouvé pour {player['name']} vous êtes donc mis en attente"
                                    f" pour l'instant")
                            await ctx.send(f"Désolé à toi {looser['name']} mais tu es éliminé du tournoi !")
                            banned['opponent'][confirm['name']] = confirm['author']
                            confirm['opponent'][banned['name']] = banned['author']
                            del load['id_ban'][id1]
                            push(ctx, load)
                        else:
                            await ctx.send("⚠ Ces deux personnes ne sont pas adversaire")
                    else:
                        await ctx.send("⚠ Le deuxième joueur n'existe pas")
                else:
                    await ctx.send("⚠ Le premier joueur n'existe pas")
            else:
                await ctx.send(f"⚠ Veuillez fournir le ping discord de l'adversaire de {member}")
        else:
            await ctx.send("⚠ Veuillez donner deux pings discord de joueur en paramètre")
    print("Commande destroy")


@bot.command()
async def force(ctx, member: discord.Member = None):
    if str(ctx.author) in get_admins(str(ctx.guild)):
        if member is not None:
            load = get(ctx)
            ctx.author = member
            classe, name, tree = search(ctx, load)
            if tree is not None:
                if tree['current-opponent'] != "Nobody":
                    for classe2 in get_class(ctx):
                        for player2 in load[classe2]:
                            if player2 != "score":
                                if load[classe2][player2]['author'] == tree['current-opponent']:
                                    tree2 = load[classe2][player2]
                                    break
                            if tree2 is not None:
                                break
                    id1 = tree['id']
                    arg1 = classe
                    arg2 = tree['name']
                    id2 = tree2['id']
                    arg4 = classe2
                    arg5 = tree2['id']
                    arg3 = 2
                    arg6 = 0
                    banned = tree
                    confirm = tree2
                    load['id_ban'][id1] = id1
                    load['id_ban'][id1] = {"banned": id1, "class_banned": arg1.lower(), "name_banned": arg2.lower(),
                                           "to_confirm": id2, "class_confirm": arg4.lower(),
                                           "name_confirm": arg5.lower(), "score_id1": float(arg3),
                                           "score_id2": float(arg6)}
                    for classe in get_class(ctx):
                        for player in load[classe]:
                            if player != "score":
                                if load[classe][player]['loose'] == 0:
                                    load[classe][player]['tour'] += 1
                    (joueur_trouve, player, looser, opponent, winner) = end_of_match(banned, id1, tree, load)
                    if joueur_trouve == 1:
                        await ctx.send(
                            f"Le joueur {player['name']} <@{player['id']}> a un nouveau match avec {opponent['name']} <@{opponent['id']}>")
                    else:
                        await ctx.send(f"Aucun match n'a été trouvé pour {player['name']} vous êtes donc mis en attente"
                                       f" pour l'instant")
                    await ctx.send(f"Désolé à toi {looser['name']} mais tu es éliminé du tournoi !")
                    banned['opponent'][confirm['name']] = confirm['author']
                    confirm['opponent'][banned['name']] = banned['author']
                    del load['id_ban'][id1]
                    push(ctx, load)
                else:
                    await ctx.send(
                        "⚠ Vous ne pouvez pas faire passer ce joueur au tour suivant car actuellement il n'a aucun adversaire")
            else:
                await ctx.send("⚠ La personne ne s'est pas enregistrée dans la compétition")
        else:
            await ctx.send("⚠ Veuillez renseigner un joueur à faire passer de force au tour suivant")
    print("Commande force")


# -------------------Bot projet tut-------------

@bot.command()
async def move(ctx, id_message, name_channel):
    print(ctx.message.content)
    print(ctx.channel.id)
    print(ctx.guild.channels)
    to_move = 0
    for channel in ctx.guild.channels:
        if channel.name == name_channel:
            ctx.channel = channel
    for message in await ctx.message.channel.history(limit=100).flatten():
        if str(message.id) == str(id_message):
            ctx.message = message
            to_move = message.content
            await ctx.message.delete()
    await ctx.send(to_move)


@bot.command()
async def wa(ctx):
    embed = discord.Embed(title="Joueurs encore en vie :", description='Date A Live \n 131:kakera: \n React with any '
                                                                       'emoji to claim! \n (Read $togglereact)',
                          color=0xffff00, image="https://i.imgur.com/dpBgivA.png")
    await ctx.send(embed=embed)


bot.run(token)
