import asyncio
import discord


channelId = 1334613161348694171
vbdffbfdb = "MTMzNDYxMjM5NjM1ODExMTMyNA.GCp0ZI.eqXvq2rLewAE8BfbZNfrggg24GvH7eYqhtmOjU"
intents = discord.Intents.default()

# inililzing discord client with default intents
client = discord.Client(intents=intents)

# Global message variable to be set externally and bot to be triggered
message = ""
image_path = ""

# event triggered when the bot is ready
@client.event
async def on_ready():
    try:
        channel = client.get_channel(int(channelId))  # find the channel with the channel ID
        if channel:
            await channel.send(message)  # send the message from the global variable
            await channel.send(file=discord.File(image_path))  # send the image
    except Exception as e:
        print(f"Erreur lors de l'envoi du message : {e}")
    finally:
        await client.close()  # close the client after sending the message


async def restart():
    await client.start(vbdffbfdb)
# method to be executed from an external file
def BotRun():

    client.run(vbdffbfdb)
