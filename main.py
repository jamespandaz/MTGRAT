# This example requires the 'members' and 'message_content' privileged intents to function.
import discord
from discord.ext import commands
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
playerList = [] # intiallise player list (hope you dont have to restart the bot!!!)
match = elo.ELOMatch()
matchPlayers = 0
gameStartTime = 0
gameEndTime = 0

# -- PLAYER CLASS -- ##
class Player:
    def __init__(self, userID, username, elo):
        self.username = username
        self.userID = userID
        self.elo = elo

## -- ACUTAL FUNCTIONS FOR COMMANDS -- ##
def reportPlacing(player, place, playerList):
    for each in playerList:
        if player == each.userID:
            match.addPlayer(each.username, place, each.elo)
            print(each)

def addPlayer(player, playerList):
    playerList.append(Player(player.id, player.name, 1500))

def endGame(ctx, match):
    message = ''
    match.calculateELOs()
    for each in match.players:
        message += str(ctx.guild.get_member_named(each.name).mention)
        message += " has had an ELO change of: "
        message += str(match.getELOChange(each.name))
        message += "\n"

    for currentPlayers in match.players:
        for each in playerList:
            if currentPlayers.name == each.username:
                each.elo = match.getELO(currentPlayers.name)
    
    return message
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

## -- COMMANDS -- ##
@bot.command()
async def register(ctx):
    addPlayer(ctx.author, playerList)
    await ctx.send(ctx.author.name + ' has been added to the leaderboard!')
    
# TODO add a silly little ranking system in here with stupid made up ranks like in cs?
@bot.command()
async def leaderboard(ctx): # TODO prob could put this into a function or maybe not cos like lmao variable scopes
    leaderboard = sorted(playerList, key=lambda x: x.elo, reverse=True)
    playerListMessage = ''
    playerRanking = 1
    for each in leaderboard:
        playerListMessage += str(playerRanking)
        playerListMessage += ". "
        playerListMessage += str(ctx.guild.get_member_named(each.username).global_name)
        playerListMessage += " | ELO:  "
        playerListMessage += str(each.elo)
        playerListMessage += "\n"
    
    await ctx.send(playerListMessage)

@bot.command()
async def startgame(ctx):
    match = elo.ELOMatch()
    await ctx.send("Game has been started! Have fun (I don't recall saying good luck)")

@bot.command()
async def reportplacing(ctx, place):
    print(ctx.author)
    reportPlacing(ctx.author.id, place, playerList)
    await ctx.send(ctx.author.name + " has reported " + place)

@bot.command()
async def endgame(ctx):
    await ctx.send(endGame(ctx, match))
    match.clearMatch()
    await ctx.send("Game has been ended! f10 + n noob!")

# TODO add a myprofile command with stats on how many times placings have been achieved? and things such as matches played, win, yada yada yada

# -- SILLY LITTLE COMMANDS -- #
@bot.command()
async def yourmum(ctx):
    await ctx.send("https://media.tenor.com/usLxd9BU6ugAAAAM/walmuartdiscord.gif")

@bot.command()
async def bozo(ctx):
   await ctx.send("Jack has been selected as the Bozo!!!! :D")

@bot.command()
async def helpmeratman(ctx):
    await ctx.send("\
1. run !register to register yourself to the leaderboard (only need to do this once) \n \
2. run !startgame to start a game (only one person needs to do this) \n \
3. run !reportplacing <place> to report your place in the game (eg. !reportgame 2 to report 2nd place) \n \
4. run !endgame to end the game and update the leaderboard (only one person needs to run this) \n \
Use !bozo to select a bozo \n \
Use !leaderboard to see the leaderboard \n")

bot.run(token['DEV_BOT_TOKEN'])
