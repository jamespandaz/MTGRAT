# This example requires the 'members' and 'message_content' privileged intents to function.
import discord
from discord.ext import commands
from peewee import SqliteDatabase, Model, CharField, IntegerField
import random
import yaml
import elo

DESCRIPTION = '''Magic The Gathering: Ranking Automation Tool Bot (MTGRAT Bot)'''

with open('config.yml', 'r', encoding='utf-8') as file:
    token = yaml.safe_load(file)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=DESCRIPTION, intents=intents)
db = SqliteDatabase('mtgrat.db')

## -- VARIABLES INIT PROB A BAD IDEA -- ##
playerList = [] # intiallise player list (hope you dont have to restart the bot!!!)
match = elo.ELOMatch()
matchPlayers = 0
packsOpened = 0 # maybe pickle this as well so it doesnt reset on restart

# -- PLAYER CLASS -- ##
#TODO: maybe add an elo history so player can call !elohistory to see a graph of their elo over time

class Player(Model):
    username = CharField()
    userID = IntegerField()
    elo = IntegerField()
    matchesPlayed = IntegerField()
    matchesWon = IntegerField()
    rank = CharField()

    class Meta:
        database = db

    def __str__(self):
        return str(self.username) + " " + str(self.userID) + " " + str(self.elo) + " " + str(self.matchesPlayed) + " " + str(self.matchesWon) + " " + str(self.rank)


# -- MATCH CLASS --##
#TODO: maybe add a match history and can call !matchhistory to see the last 10 games or something
#TODO: could maybe add commander info so we can see what decks are winning the most/wins over time

# -- MATCH CLASS --##
#TODO: maybe add a match history and can call !matchhistory to see the last 10 games or something
#TODO: could maybe add commander info so we can see what decks are winning the most/wins over time

## -- ACUTAL FUNCTIONS FOR COMMANDS -- ##
def reportPlacing(player, place):
    thisPlayer = Player.get(Player.userID == player)
    match.addPlayer(thisPlayer.username, place, thisPlayer.elo)

def addPlayer(player):
    newPlayer = Player(username=player.name, userID=player.id, elo=1500, matchesPlayed=0, matchesWon=0, rank='')
    newPlayer.save()

def endGame(ctx, match):
    message = ''
    match.calculateELOs()
    for each in match.players:
        message += str(ctx.guild.get_member_named(each.name).mention)
        message += " has had an ELO change of: "
        message += str(match.getELOChange(each.name))
        message += "\n"

    for currentPlayers in match.players:
        thisPlayer = Player.get(Player.username == currentPlayers.name)
        thisPlayer.elo = match.getELO(currentPlayers.name)
        thisPlayer.save()

    return message

def getRank(ctx, player):
    print(player)
    thisPlayer = player
    if int(thisPlayer.elo) > 1800:
        rank = "Felidar Retreat"
    elif int(thisPlayer.elo) > 1750:
        rank = "The One Ring"
    elif int(thisPlayer.elo) > 1700:
        rank = "Black Lotus"
    elif int(thisPlayer.elo) > 1650:
        rank = "Sol Ring"
    elif int(thisPlayer.elo) > 1600:
        rank = "The Ur-Dragon"
    elif int(thisPlayer.elo) > 1550:
        rank = "Yuriko, the Tiger's Shadow"
    elif int(thisPlayer.elo) > 1500:
        rank = "Krenko, Mob Boss"
    elif int(thisPlayer.elo) > 1450:
        rank = "Nekusar, the Mindrazer"
    elif int(thisPlayer.elo) > 1400:
        rank = "Rin and Seri, Inseparable"
    elif int(thisPlayer.elo) > 1350:
        rank = "Rakdos, Lord of Riots"
    elif int(thisPlayer.elo) > 1300:
        rank = "Drizzt Do'Urden"
    elif int(thisPlayer.elo) > 1250:
        rank = "Salruf, Realm Eater"
    elif int(thisPlayer.elo) > 1200:
        rank = "Basic Land (it's a cool printing at least)"
    elif int(thisPlayer.elo) > 1150:
        rank = "Plains"
    else:
        rank = "i couldnt be bothered to think of more names, this elo is so low i didnt think anyone would see this"
    print(str(rank))
    thisPlayer.rank = rank
    thisPlayer.save()
    return
            
#TODO: maybe everytime leaderboard gets called it saves the leaderboard to a file so it gets backed up incase of a crash
def getLeaderboard(ctx, playerList):
    leaderboard = sorted(playerList, key=lambda x: int(x.elo), reverse=True)
    playerListMessage = ''
    playerRanking = 1
    for each in leaderboard:
        playerListMessage += str(playerRanking)
        playerListMessage += ". "
        playerListMessage += str(ctx.guild.get_member_named(each.username).global_name)
        playerListMessage += " | ELO:  "
        playerListMessage += str(each.elo)
        playerListMessage += " | Rank: "
        getRank(ctx, each)
        playerListMessage += str(each.rank)
        playerListMessage += "\n"
        playerRanking += 1
    
    return playerListMessage
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    db.connect()
    print("Database is connected!")

## -- COMMANDS -- ##
@bot.command()
async def createtables(ctx):
    if ctx.author.name == "poshpanda__":
        db.create_tables([Player])
        await ctx.send("Tables have been created")
    else:
        await ctx.send("Nice try bucko. I see what ya tryna do there.")

@bot.command()
async def amiin(ctx):
    player = Player.get(Player.userID == ctx.author.id)
    await ctx.send(player.__str__())

@bot.command()
async def register(ctx):
    addPlayer(ctx.author)
    await ctx.send(ctx.author.name + ' has been added to the leaderboard!')

@bot.command()
async def startgame(ctx):
    match = elo.ELOMatch()
    await ctx.send("Game has been started! Have fun (I don't recall saying good luck)")

@bot.command()
async def reportplacing(ctx, place):
    reportPlacing(ctx.author.id, place)
    if place == '1':
        thisPlayer = Player.get(Player.userID == ctx.author.id)
        thisPlayer.matchesWon += 1
        thisPlayer.matchesPlayed += 1
    else:
        thisPlayer = Player.get(Player.userID == ctx.author.id)
        thisPlayer.matchesPlayed += 1

    thisPlayer.save()
    await ctx.send(ctx.author.name + " has reported " + place)

@bot.command()
async def endgame(ctx):
    await ctx.send(endGame(ctx, match))
    match.clearMatch()
    await ctx.send("Game has been ended! UNPLUG YO CONTROLLER DAWG")

@bot.command()
async def myprofile(ctx):
    message = ''
    thisPlayer = Player.get(Player.userID == ctx.author.id)
    message += "**My Profile** \n"
    message += "Username: " + str(thisPlayer.username) + "\n"
    message += "Matches Won: " + str(thisPlayer.matchesWon) + "\n"
    message += "Matches Played: " + str(thisPlayer.matchesPlayed) + "\n"
    message += "ELO: " + str(thisPlayer.elo) + "\n"
    getRank(ctx, thisPlayer)
    message += "Rank: " + str(thisPlayer.rank) + "\n"
    if thisPlayer.matchesPlayed == 0:
        message += "Win Rate: 0%" + "\n"
    else:
        message += "Win Rate: " + str(100*(int(thisPlayer.matchesWon)/int(thisPlayer.matchesPlayed)))[:5] + "%" + "\n"
    
    await ctx.send(message)

@bot.command()
async def leaderboard(ctx):
    playerList = Player.select()
    await ctx.send(getLeaderboard(ctx, playerList))

# -- SILLY LITTLE COMMANDS -- #
@bot.command()
async def yourmum(ctx):
    await ctx.send("https://media.tenor.com/usLxd9BU6ugAAAAM/walmuartdiscord.gif")

#TODO: Make sure you test this, update it doesnt work lmao
@bot.command()
async def openpack(ctx):
    packsOpened += 1
    await ctx.send("It's rippin time, imma rip all over the whole room")
    await ctx.send("Total amount of packs ripped: " + str(packsOpened))

@bot.command()
async def bozo(ctx):
   randomplayer = random.choice(ctx.guild.members)
   await ctx.send(randomplayer.mention + "has been selected as the Bozo!!!! :D")

@bot.command()
async def isjackallergictobees(ctx):
    await ctx.send("No")

@bot.command()
async def helpmeratman(ctx):
    await ctx.send("\
1. run !register to register yourself to the leaderboard (only need to do this once) \n \
2. run !startgame to start a game (only one person needs to do this, and you can only have one match running at once) \n \
3. run !reportplacing <place> to report your place in the game (eg. !reportgame 2 to report 2nd place, everyone needs to do this) \n \
4. run !endgame to end the game and update the leaderboard (only one person needs to run this) \n \
Use !bozo to select a bozo \n \
Use !leaderboard to see the leaderboard \n\
Use !myprofile to see your profile \n")

bot.run(token['DEV_BOT_TOKEN'])
