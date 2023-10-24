import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import json
from fuzzywuzzy import fuzz

load_dotenv()
counts = {}
script_directory = os.path.abspath(os.path.dirname(__file__))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=108378541988515840, tree = tree, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)

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

def loadAllImages():
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    for i in all_images:
        if f"{script_directory}/images/{i}" not in counts.keys():
            counts.update({f"{script_directory}/images/{i}":0})
            print(i)
    save_stats()

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
async def stats(ctx, *, arg = 'All'):
    if arg != 'All':
        closest_score = -1
        closest_match = None
        for k in counts.keys():
            simScore = fuzz.ratio(f"{script_directory}/images/{arg}.", k)
            if simScore > closest_score:
                closest_score = simScore
                closest_match = k
        if closest_score >= 93:
            await ctx.send(f'{closest_match} has been rolled {counts[closest_match]} time(s).')
        else:
            await ctx.send(f'Unable to find character {arg}. Check your spelling and try again.', ephemeral=True)
        '''jpg = counts.get(f"{script_directory}/images/{arg}.jpg")
        png = counts.get(f"{script_directory}/images/{arg}.png")
        jpeg = counts.get(f"{script_directory}/images/{arg}.jpeg")
        if jpg != None:
            await ctx.send(f'{arg} has been rolled {jpg} time(s).')
        elif png != None:
            await ctx.send(f'{arg} has been rolled {png} time(s).')
        elif jpeg != None:
            await ctx.send(f'{arg} has been rolled {jpeg} time(s).')
        else:
            await ctx.send(f'Unable to find character {arg}. Check your spelling/capitalization and try again.', ephemeral=True)
            '''
    else:
        character, count = getMostCommon()
        if type(character) is list:
            names = ", ".join(character)
            await ctx.send(f'There is a tie between {names} with {count} rolls.')
        else:
            await ctx.send(f'{character.split(".")[0]} is the most common roll with {count} rolls.')

@bot.tree.command(name='submit', description='Submit a character', guild=discord.Object(id=240265833199173633))
@app_commands.describe(attachment='The file to upload', name='The characters name')
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, name: str):
    if counts.get(f"{script_directory}/images/{name}{attachment.filename[-4:]}") != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif counts.get(f"{script_directory}/images/{name}{attachment.filename[-5:]}") != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif attachment.filename[-4] == '.':
        await attachment.save(f"{script_directory}/images/{name}{attachment.filename[-4:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)
    else:
        await attachment.save(f"{script_directory}/images/{name}{attachment.filename[-5:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)

@bot.command(name='sync', description='Owner only')
async def sync(ctx):
    if ctx.author.id == bot.owner_id:
        await bot.tree.sync(guild=discord.Object(id=240265833199173633))
        print('Command tree synced.')
    else:
        await ctx.send('You must be the owner to use this command!')

@bot.event
async def on_ready():
    print("Bot ready")
    await bot.tree.sync(guild=discord.Object(id=240265833199173633))

if __name__ == "__main__":
    load_stats()
    loadAllImages()
    bot.run(DISCORD_TOKEN)
