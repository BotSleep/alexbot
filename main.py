import discord
from discord.ext import commands
import os
import asyncio
import dotenv
from dotenv import load_dotenv
import random
import json
#import sqlite3

load_dotenv()

counts = {}
script_directory = os.path.abspath(os.path.dirname(__file__))

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_stats():
    global counts
    try:
        with open('imagestats.json', 'r') as json_file:
            counts = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        counts = {}

# Save stats to the JSON file
def save_stats():
    with open('imagestats.json', 'w') as json_file:
        json.dump(counts, json_file)

def addImageCount(filename):
     # Increment the count for the specified image
    counts[filename] = counts.get(filename, 0) + 1
    save_stats()

def getMostCommon():
    most_common_image = max(counts, key=counts.get)
    most_common_count = counts[most_common_image]
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

@bot.command(name='stats')
async def stats(ctx):
    character, count = getMostCommon()
    await ctx.send(f'{character.rstrip(".jpgne")} is the most common roll with {count} rolls.')

if __name__ == "__main__":
    load_stats()
    bot.run(DISCORD_TOKEN)
