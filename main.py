import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import dotenv
from dotenv import load_dotenv
import random
import json

load_dotenv()
counts = {}
script_directory = os.path.abspath(os.path.dirname(__file__))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=108378541988515840)

def load_stats():
    global counts
    try:
        with open('imagestats.json', 'r') as json_file:
            counts = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        counts = {}

def save_stats():
    with open('imagestats.json', 'w') as json_file:
        json.dump(counts, json_file)

def addImageCount(filename):
     # Increment the count for the specified image
    counts[filename] = counts.get(filename, 0) + 1
    save_stats()

def getMostCommon():
    ties = 0
    tienames = []
    most_common_image = max(counts, key=counts.get)
    most_common_count = counts[most_common_image]
    for k,v in counts.items():
        if v is most_common_count:
            ties += 1
            tienames.append(os.path.basename(k.split(".")[0]))
            print(f'DEBUG: {os.path.basename(k.split(".")[0])} rolled: {v}')
    if ties > 0:
        return tienames, most_common_count
    else:
        return os.path.basename(most_common_image), most_common_count

@bot.command(name='roll', help='Send random image to chat')
async def images(ctx):
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = f"{script_directory}/images/{random.choice(all_images)}"
    addImageCount(random_image)
    await ctx.send(file=discord.File(random_image))

@bot.command(name='toll', help='Pay the trolls toll')
async def troll(ctx):
    #sends the troll
    random_image = f"{script_directory}/images_nochar/{'troll.jpg'}"
    await ctx.send(f"Uh-oh! You accidentally typed toll! Now you must pay the trolls toll!")
    await ctx.send(file=discord.File(random_image))

@bot.hybrid_command(name='stats', with_app_command=True, help='displays the current most common characters')
async def stats(ctx):
    character, count = getMostCommon()
    if type(character) is list:
        names = ", ".join(character)
        await ctx.send(f'There is a tie between {names} with {count} rolls.')
    else:
        await ctx.send(f'{character.split(".")[0]} is the most common roll with {count} rolls.')

@bot.command(name='sync', description='Owner only')
async def sync(ctx):
    if ctx.author.id == 108378541988515840:
        await bot.tree.sync()
        print('Command tree synced.')
    else:
        await ctx.message('You must be the owner to use this command!')

if __name__ == "__main__":
    load_stats()
    bot.run(DISCORD_TOKEN)
