# This example requires the 'members' and 'message_content' privileged intents to function.
import discord
from discord.ext import commands
import random
import yaml
import elo

description = '''Magic The Gathering: Ranking Automation Tool Bot (MTGRAT Bot)'''

with open('config.yml', 'r') as file:
    token = yaml.safe_load(file)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)
## -- VARIABLES INIT PROB A BAD IDEA -- ## 
playerList = [] # intiallise player list (hope you dont have to restart the bot!!!
match = elo.ELOMatch()
matchPlayers = 0

# -- PLAYER CLASS -- ##
class Player:
    def __init__(self, userID, username, elo):
        self.username = username
        self.userID = userID
        self.elo = elo

## -- ACUTAL FUNCTIONS FOR COMMANDS -- ##
def reportGame(player, place, playerList):
    for each in playerList:
        if player.id == each.userID:
            match.addPlayer(each.username, place, each.elo)
            print(each)

def addPlayer(player, playerList):
    playerList.append(Player(player.id, player.name, 1500))

def endGame(match, ctx):
    message = ''
    match.calculateELOs()
    for each in match.players:
        each.getELO(each.name)
        message += each.name
        message += " has had an ELO change of: "
        message += each.getELOChange(each.name)
        message += "\n"
    ctx.send()
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def addplayer(ctx):
    addPlayer(ctx.author, playerList)
    await ctx.send(ctx.author.name + ' has been added to the leaderboard!')

@bot.command()
async def leaderboard(ctx):
    playerListMessage = ''
    for each in playerList:
        playerListMessage += each.username
        playerListMessage += str(each.elo)
        playerListMessage += "\n"
    
    await ctx.send(playerListMessage)
@bot.command()
async def startgame(ctx):
    match = elo.ELOMatch()
    await ctx.send("Game has been started! Have fun (I don't recall saying good luck)")

@bot.command()
async def reportgame(ctx, place):
    if matchPlayers == 1: ## TODO FIRST TIME FIX VARIABLE
        endGame(match, ctx)
    else:
        reportGame(ctx.author, place, playerList)
        await ctx.send(ctx.author.name + " has reported " + place)
        matchPlayers += 1

bot.run(token['BOT_TOKEN'])