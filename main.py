import discord
from discord.ext import commands
import json

print("La partie va commencer !")
client = discord.Client()
token = "ODAxODc4NjAxMDM3MzgxNjYy.YAnFpA.s0fJEBdu9fW9CqgOl_VAJgCjwas"
bot = commands.Bot(command_prefix="!")


def add_account(arg1, arg2, load, id_member):
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            res = 1
        else:
            b = {'score': 0.0, 'win': 0, 'loose': 0, 'poule': "A changer", "disponible": True}
            load[arg1.lower()][arg2.lower()] = b
            res = 0
    else:
        b = {'score': 0.0, arg2.lower(): {'score': 0.0, 'win': 0, 'loose': 0, 'poule': "A changer", "disponible": True}}
        load[arg1.lower()] = b
        res = 0
    load['id'][id_member] = id_member
    load['players'][arg2.lower()] = arg1.lower()
    with open('register.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    return res


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
    try:
        print(load['id_ban'])
    except KeyError:
        load['id_ban'] = {}
    try:
        print(load['players'])
    except KeyError:
        load['players'] = {}
        for biblio in load.keys():
            if biblio not in ["id", "id_ban", "players", "poule_done"]:
                for player in load[biblio].keys():
                    if player != "score":
                        load['players'][player] = biblio
    try:
        print(load['poule_done'])
    except KeyError:
        load['poule_done'] = {}
    with open('register.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Joue aux échecs"))
    print("La partie commence ...")


@bot.command()
async def _help(ctx):
    embed = discord.Embed(title="**__Résumé des commandes__**", description="", color=0xf0f0f0)
    embed.add_field(name="**Pour une liste des commandes ainsi que leur description et explication "
                         "d'utilisation, veuillez vous référer au site : **",
                    value="***https://mabule.github.io/chess.com/index.html***", inline=False)
    await ctx.send(embed=embed)
    print("Commande _help")


@bot.command()
async def result(ctx, member1: discord.Member, arg1, arg2, arg3, member2: discord.Member, arg4, arg5, arg6):
    with open('register.json') as load:
        load = json.load(load)
    id1 = str(member1.id)
    id2 = str(member2.id)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            if arg4.lower() in load:
                if arg5.lower() in load[arg4.lower()]:
                    load['id_ban'][id1] = id1
                    load['id_ban'][id1] = {"banned": id1, "class_banned": arg1.lower(), "name_banned": arg2.lower(),
                                           "to_confirm": id2, "class_confirm": arg4.lower(),
                                           "name_confirm": arg5.lower(), "score_id1": float(arg3),
                                           "score_id2": float(arg6)}
                    with open('register.json', "w") as f:
                        json.dump(load, f, ensure_ascii=False, indent=4)
                    await ctx.send("Le résultat du match a bien était enregistré\nEn attente de la commande "
                                   "`!match_result_confirm` de la part du second joueur...")
                else:
                    await ctx.send("Une erreur pour le deuxième joueur a été recensé")
            else:
                await ctx.send("Une erreur pour la deuxième classe a été recensé")
        else:
            await ctx.send("Une erreur pour le premier joueur a été recensé")
    else:
        await ctx.send("Une erreur pour la première classe a été recensé")
    print("Commande result")


@bot.command()
async def result_confirm(ctx, member: discord.Member, member1: discord.Member, arg1, member2: discord.Member):
    id1 = str(member1.id)
    id2 = str(member2.id)
    with open('register.json') as load:
        load = json.load(load)
    if id1 in load['id_ban']:
        if id2 in load['id_ban'][id1]['to_confirm']:
            if arg1 == "y":
                banned = load[load['id_ban'][id1]['class_banned']][load['id_ban'][id1]['name_banned']]
                confirm = load[load['id_ban'][id1]['class_confirm']][load['id_ban'][id1]['name_confirm']]
                banned['score'] += float(load['id_ban'][id1]['score_id1'])
                confirm['score'] += float(load['id_ban'][id1]['score_id2'])
                load[load['id_ban'][id1]['class_banned']]['score'] += float(load['id_ban'][id1]['score_id1'])
                load[load['id_ban'][id1]['class_confirm']]['score'] += float(load['id_ban'][id1]['score_id2'])
                embed = discord.Embed(title="VICTORY", description="", color=0x00ff00)
                embed.add_field(name="\0", value=f"Résultat du match entre {member1} et {member2} a été approuvé")
                await member.send(embed=embed)
                await ctx.send("Le résultat a bien était prit en compte !")
                # -----------------------------------------------
                if load['id_ban'][id1]['score_id1'] < load['id_ban'][id1]['score_id2']:
                    banned['loose'] += 1
                    confirm['win'] += 1
                else:
                    banned['win'] += 1
                    confirm['loose'] += 1
                joueur_trouve = 0
                for key in load['players'].keys():
                    if load[load['players'][key]][key]['win'] == banned['win'] and load[load['players'][key]][key][
                        'poule'] == banned['poule']:
                        await ctx.send(f"Le joueur {banned} a un nouveau match avec {key}")
                        joueur_trouve = 1
                        banned['disponible'] = False
                        load[load['players'][key]][key]['disponible'] = False
                if joueur_trouve == 0:
                    await ctx.send(
                        f"Aucun match n'a était trouvé pour {banned} vous êtes donc mis en attente pour l'instant")
                joueur_trouve = 0
                for key in load['players'].keys():
                    if load[load['players'][key]][key]['win'] == confirm['win'] and load[load['players'][key]][key][
                        'poule'] == confirm['poule']:
                        await ctx.send(f"Le joueur {confirm} a un nouveau match avec {key}")
                        joueur_trouve = 1
                        confirm['disponible'] = False
                        load[load['players'][key]][key]['disponible'] = False
                if joueur_trouve == 0:
                    await ctx.send(
                        f"Aucun match n'a était trouvé pour {confirm} vous êtes donc mis en attente pour l'instant")
                # -----------------------------------------------
                del load['id_ban'][id1]
            elif arg1 == "n":
                del load['id_ban'][id1]
                embed = discord.Embed(title="CA TOURNE MAL EXPLICATION !!!!", description="Refus de défaite",
                                      color=0xff0000)
                embed.add_field(name="\0", value=f"Refus du résultat du match entre : {member1} et {member2}")
                await member.send(embed=embed)
                await ctx.send("Le résultat du dernier match a donc était éffacé, l'information remontera à un "
                               "administrateur")
            else:
                await ctx.send("Veuillez saisir un deuxième paramètre parmis les caractères 'y' ou 'n'")
        else:
            await ctx.send(f"{member2} n'était pas votre adversaire !")
    else:
        await ctx.send("La personne mentionnée n'a pas donné de résultat récemment")
    with open('register.json', "w") as f:
        json.dump(load, f, ensure_ascii=False, indent=4)
    print("Commande result_confirm")


@bot.command()
async def score_player(ctx, arg1, arg2):
    with open('register.json') as f:
        load = json.load(f)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            embed = discord.Embed(title="Score de " + arg2, description="", color=0x990099)
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
async def register(ctx, membre: discord.Member, arg1, arg2):
    res = 2
    with open('register.json') as load:
        load = json.load(load)
    id = str(membre.id)
    if id != "803313379992272967" and id != "466005935404351488" and id != "414476886501228556":
        if id in load['id']:
            await ctx.send("Désolé mais vous ne pouvez pas enregistrer plus de 1 participant")
        else:
            if ctx.author != membre:
                await ctx.send(
                    "Mais attends ... Tu essayerais pas de gruger le système pour confirmer toi-même le résultat ?? O_O (je te vois...)")
            else:
                res = add_account(arg1, arg2, load, id)
    else:
        res = add_account(arg1, arg2, load, id)
    if res == 0:
        await ctx.send(f"Le participant {arg2} de la classe {arg1} est enregistré")
    elif res == 1:
        await ctx.send(f"Une erreur s'est produite car le participant {arg2} pour la classe {arg1} doit déjà exister")
    else:
        pass
    print("Commande register")


@bot.command()
async def modif_class(ctx, arg1, arg2, arg3):
    with open('register.json') as load:
        load = json.load(load)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            temp = load[arg1.lower()][arg2.lower()]
            if arg3.lower() in load:
                load[arg3.lower()][arg2.lower()] = temp
                with open('register.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
                await ctx.send(
                    f"Le changement de la classe {arg1} pour la classe {arg3} du joueur {arg2} a bien était éffectué")
            else:
                await ctx.send("Veuillez renseigner une classe d'arrivé existante :)")
        else:
            await ctx.send(f"Aucun joueur de ce nom n'a été trouvé dans la classe {arg1}")
    else:
        await ctx.send("La classe d'origine du joueur n'existe pas")
    print("Commande modif_class")


@bot.command()
async def modif_player(ctx, arg1, arg2, arg3):
    with open('register.json') as load:
        load = json.load(load)
    if arg1.lower() in load:
        if arg2.lower() in load[arg1.lower()]:
            if arg2.lower() == arg3.lower():
                await ctx.send("Les deux noms sont identiques, donc le changement est inutile (toutes les chaines "
                               "sont converties à leur équivalent en minuscule)")
            else:
                temp = load[arg1.lower()][arg2.lower()]
                del load[arg1.lower()][arg2.lower()]
                load[arg1.lower()][arg3.lower()] = temp
                with open('register.json', "w") as f:
                    json.dump(load, f, ensure_ascii=False, indent=4)
                await ctx.send(
                    f"Le changement de prénom de {arg2} pour {arg3} dans la classe {arg1} a bien été éffectué")
        else:
            await ctx.send(f"Aucun joueur ne s'appelle {arg2} dans la classe {arg1}")
    else:
        await ctx.send("La classe du joueur n'existe pas")
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
                            value="**__" + load['players'][key] + "__"
                                                                  "\n"
                                                                  "\n**",
                            inline=False)
        await ctx.send(embed=embed)


@bot.command()
async def delete_class(ctx, arg):
    if str(ctx.author) == "Mabule#2890" or "oitzyhrr#1141" or "Toooom#2689":
        with open('register.json') as load:
            load = json.load(load)
        if arg.lower() in load:
            player_list = []
            for player in load[arg.lower()].keys():
                if player != 'score':
                    player_list.append(player)
            del load[arg.lower()]
            for player in list(load['players'].keys()):
                if player in player_list:
                    del load['players'][player]
            with open('register.json', "w") as f:
                json.dump(load, f, ensure_ascii=False, indent=4)
            await ctx.send(f"L'effacement de la classe {arg.lower()} s'est bien éffectué")
        else:
            await ctx.send("La classe renseignée n'existe pas ¯\_(ツ)_/¯")


bot.run(token)
