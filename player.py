import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('discord_token')  # Bot token from the .env file

# Define bot intents for handling message content
intents = discord.Intents.default()
intents.message_content = True

# Initialize the Discord client with the specified intents
client = discord.Client(intents=intents)

# Dictionary to store active voice clients for each guild
voice_clients = {}

# yt-dlp options for extracting audio from YouTube URLs
yt_dlp_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ytdl = yt_dlp.YoutubeDL(yt_dlp_opts)

# FFMPEG options for audio playback
ffmpeg_options = {'options': '-vn'}

@client.event
async def on_ready():
    print(f'{client.user} is now running!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore messages from the bot itself

    if message.content.startswith("?play"):
        try:
            # Join the voice channel of the message author
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(f"Error connecting to voice channel: {e}")

        try:
            # Extract and play audio from the provided URL
            url = message.content.split(" ", 1)[1]
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
            voice_clients[message.guild.id].play(player)
        except IndexError:
            await message.channel.send("Please provide a valid URL.")
        except Exception as e:
            print(f"Error playing audio: {e}")

    elif message.content.startswith("?pause"):
        try:
            voice_clients[message.guild.id].pause()
        except KeyError:
            await message.channel.send("Bot is not connected to a voice channel.")
        except Exception as e:
            print(f"Error pausing audio: {e}")

    elif message.content.startswith("?resume"):
        try:
            voice_clients[message.guild.id].resume()
        except KeyError:
            await message.channel.send("Bot is not connected to a voice channel.")
        except Exception as e:
            print(f"Error resuming audio: {e}")

    elif message.content.startswith("?stop"):
        try:
            await voice_clients[message.guild.id].disconnect()
            del voice_clients[message.guild.id]
        except KeyError:
            await message.channel.send("Bot is not connected to a voice channel.")
        except Exception as e:
            print(f"Error stopping audio: {e}")

# Run the bot using the provided TOKEN
client.run(TOKEN)
