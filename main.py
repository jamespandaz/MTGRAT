import discord
import elo
import logging
import yaml

def main():
    with open('config.yml', 'r') as file:
        token = yaml.safe_load(file)

    playerList = [] # intiallise player list (hope you dont have to restart the bot!!!
    class Player:
        def __init__(self, userID, username, elo):
            self.username = username
            self.userID = userID
            self.elo = elo

    class MyClient(discord.Client):
         

        async def on_ready(self): # logs in and then prints that its gucci to run
            print(f'Logged on as {self.user}!')

        async def on_message(self, message): # what happens on a message
            print(f'Message from {message.author}: {message.content}')

            if message.author.id == self.user.id: # bot cant trigger itself and cause spam
                return
            
            match message.content: # match message content to a command
                case '!addplayer':
                    addPlayer(message.author, playerList)
                    print(playerList)
                    await message.channel.send(message.author.name + 'has been added to the leaderboard!')
                    playerList.append(Player(message.author.id, message.author.name, 1500))

                case '!playerlist':
                    playerListMessage = ''
                    for each in playerList:
                        playerListMessage += each.name
                        playerListMessage += "\n"
                    await message.channel.send(playerListMessage)
                
                case '!mystats':
                    if message.author.id in playerList.Player.userID:
                        await message.channel.send()

                case _:
                    pass

    intents = discord.Intents.default() ## intents which idk what really does but i guess we will find out
    intents.message_content = True
    intents.typing = False
    intents.presences = False

    client = MyClient(intents=intents)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    client.run(token['BOT_TOKEN'], log_handler=handler)

def addPlayer(player, playerList):
    playerList.append(player)

main()