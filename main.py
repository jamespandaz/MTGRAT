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
playerList = [] # intiallise player list (hope you dont have to restart the bot!!!)
match = elo.ELOMatch()
matchPlayers = 0
gameStartTime = 0
gameEndTime = 0

# -- PLAYER CLASS -- ##
class Player:
    def __init__(self, userID, username, elo, matchesPlayed, matchesWon, rank):
        self.username = username
        self.userID = userID
        self.elo = elo
        self.matchesPlayed = matchesPlayed
        self.matchesWon = matchesWon
        self.rank = rank

## -- ACUTAL FUNCTIONS FOR COMMANDS -- ##
def reportPlacing(player, place, playerList):
    for each in playerList:
        if player == each.userID:
            match.addPlayer(each.username, place, each.elo)

def addPlayer(player, playerList):
    playerList.append(Player(player.id, player.name, 1500, 0, 0, ''))

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

def getRank(ctx, player, playerList):
    rank = ''
    print(player)
    for each in playerList:
        if player.userID == each.userID:
            if int(each.elo) > 2700:
                rank = "The One Ring"
            elif int(each.elo) > 2500:
                rank = "Black Lotus"
            elif int(each.elo) > 2300:
                rank = "Sol Ring"
            elif int(each.elo) > 2000:
                rank = "The Ur-Dragon"
            elif int(each.elo) > 1800:
                rank = "Yuriko, the Tiger's Shadow"
            elif int(each.elo) > 1500:
                rank = "Krenko, Mob Boss"
            elif int(each.elo) > 1200:
                rank = "Nekusar, the Mindrazer"
            elif int(each.elo) > 1000:
                rank = "Rin and Seri, Inseparable"
            elif int(each.elo) > 800:
                rank = "Rakdos, Lord of Riots"
            elif int(each.elo) > 600:
                rank = "Drizzt Do'Urden"
            else:
                rank = "i couldnt be bothered to think of more names, this elo is so low i didnt think anyone would see this"
        print(str(rank))
        player.rank = rank
        return
            

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
        getRank(ctx, each, playerList)
        playerListMessage += str(each.rank)
        playerListMessage += "\n"
        playerRanking += 1
    
    return playerListMessage
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

## -- COMMANDS -- ##
@bot.command()
async def register(ctx):
    for each in playerList:
        if ctx.author.id == each.userID:
            await ctx.send("You have already registered!")
            return
    addPlayer(ctx.author, playerList)
    await ctx.send(ctx.author.name + ' has been added to the leaderboard!')

@bot.command()
async def setelo(ctx, player, elo):
    if ctx.author.name == "poshpanda__":
        for each in playerList:
            if each.username == player:
                each.elo = elo
                await ctx.send(player + "'s elo has been set to " + str(elo))
    else:
        await ctx.send("Nice try bucko. I see what ya tryna do there.")

@bot.command()
async def setgameswon(ctx, player, matchesWon):
    if ctx.author.name == "poshpanda__":
        for each in playerList:
            if each.username == player:
                each.matchesWon = matchesWon
                await ctx.send(player + "'s matches won has been set to " + str(matchesWon))
    else:
        await ctx.send("Nice try bucko. I see what ya tryna do there.")

@bot.command()
async def setgamesplayed(ctx, player, matchesPlayed):
    if ctx.author.name == "poshpanda__":
        for each in playerList:
            if each.username == player:
                each.matchesPlayed = matchesPlayed
                await ctx.send(player + "'s matches played has been set to " + str(matchesPlayed))
    else:
        await ctx.send("Nice try bucko. I see what ya tryna do there.")

@bot.command()
async def leaderboard(ctx):   
    await ctx.send(getLeaderboard(ctx, playerList))

@bot.command()
async def startgame(ctx):
    match = elo.ELOMatch()
    await ctx.send("Game has been started! Have fun (I don't recall saying good luck)")

@bot.command()
async def reportplacing(ctx, place):
    reportPlacing(ctx.author.id, place, playerList)
    if place == '1':
        for each in playerList:
            if ctx.author.id == each.userID:
                each.matchesWon += 1
                each.matchesPlayed += 1
    else:
        for each in playerList:
            if ctx.author.id == each.userID:
                each.matchesPlayed += 1

    await ctx.send(ctx.author.name + " has reported " + place)

@bot.command()
async def endgame(ctx):
    await ctx.send(endGame(ctx, match))
    match.clearMatch()
    await ctx.send("Game has been ended! f10 + n noob!")

@bot.command()
async def myprofile(ctx):
    message = ''
    for each in playerList:
        if ctx.author.id == each.userID:
            message += "**My Profile** \n"
            message += "Username: " + str(each.username) + "\n"
            message += "Matches Won: " + str(each.matchesWon) + "\n"
            message += "Matches Played: " + str(each.matchesPlayed) + "\n"
            message += "ELO: " + str(each.elo) + "\n"
            getRank(ctx, each, playerList)
            message += "Rank: " + str(each.rank) + "\n"
            if each.matchesPlayed == 0:
                message += "Win Rate: 0%" + "\n"
            else:
                message += "Win Rate: " + str(100*(int(each.matchesWon)/int(each.matchesPlayed)))[:5] + "%" + "\n"
            await ctx.send(message)

# -- SILLY LITTLE COMMANDS -- #
@bot.command()
async def yourmum(ctx):
    await ctx.send("https://media.tenor.com/usLxd9BU6ugAAAAM/walmuartdiscord.gif")

@bot.command()
async def bozo(ctx):
   randomplayer = random.choice(ctx.guild.members)
   await ctx.send(randomplayer.mention + "has been selected as the Bozo!!!! :D")

@bot.command()
async def isjackallergictobees(ctx):
    await ctx.send("Yes")

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
