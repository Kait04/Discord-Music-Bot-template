import discord
from discord.ext import commands, tasks
from itertools import cycle
import asyncio
import os
from dotenv import load_dotenv
import youtube_dl
import random

load_dotenv()
DISCORD_TOKEN = os.getenv("INSERT YOUR TOKEN")

intents = discord.Intents().all()
client = discord.Client(intents = intents)
bot = commands.Bot(command_prefix = 'v', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

bot_status = cycle(["Made by Kaito山下", "Work in Progress"])


@tasks.loop(seconds=3)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(bot_status)))

@bot.event
async def on_ready():
    change_status.start()
    print("-----")
    print("Bot is Online")
    print("-----")

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ''

    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name="join")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} you're not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()

@bot.command(name="play")
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    
    if voice_channel is None:
        # If the bot is not connected to a voice channel, attempt to join the channel of the command invoker
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name}, you are not connected to a voice channel.")
            return
        else:
            channel = ctx.message.author.voice.channel
            voice_channel = await channel.connect()

    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop = bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable = r"C:\Code\discordbot\ffmpeg-2023-03-05-git-912ac82a3c-full_build\bin\ffmpeg.exe", source = filename))
    await ctx.send(f"**Now Playing:** {filename}")

@bot.command(name="pause")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot has paused the music or it's not playing anything")

@bot.command(name="resume")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot is not playing a song")

@bot.command(name="disconnect")
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot hasn't joined a voice channel")

@bot.command(name="stop")
async def stop(ctx):
    voice_client = ctx.messsage.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything")

@bot.command(name="ping", help="Displays Bot's Latency")
async def ping(ctx):
    bot_latency = round(bot.latency * 1000)
    await ctx.send(f"I have a latency of {bot_latency} ms.")

@bot.command(name="8ball", aliases=["eightball", "8 ball", "eight ball"], help="Answers Yes or No Questions")
async def magic_eightball(ctx, question=None):
    if question is None:
        await ctx.send("Please ask a question")
        return
    with open(r"C:\Code\VBrato Experiment\responses.txt") as f:
        random_responses = f.readlines()
        response = random.choice(random_responses)

    await ctx.send(response)

@bot.command(name="test", help="Check if the bot is running")
async def test(ctx):
    with open(r"C:\Code\VBrato Experiment\test.txt") as t:
        random_responses = t.readlines()
        response = random.choice(random_responses)

    await ctx.send(response)

@bot.command(name="about", help = "know more about the bot")
async def embed(ctx):
    embed = discord.Embed(title = "VBrato", url = "https://i1.sndcdn.com/artworks-y6kBrjv4X7TBv46y-qN1bog-t500x500.jpg", description="Hi there, I am VBrato. I am a simple discord music bot made by **Kaito山下#2360**", color=discord.Color.yellow())
    embed.add_field(name="What can I do?", value="For now I can only play music, and interactive commands as I am still a **Work In Progress**", inline = True)
    embed.add_field(name="Know more about the creator!", value="**[Click here](https://kaitoymsht.carrd.co/)**")
    embed.set_footer(text="Information requested by: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run("INSERT YOUR TOKEN")