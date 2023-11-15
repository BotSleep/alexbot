from typing import Any, Optional, Union, NamedTuple
import discord
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.ext import commands
from discord import app_commands
import os
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji
from dotenv import load_dotenv
import random
import json
import asyncio
from fuzzywuzzy import fuzz

load_dotenv()
counts = {}
bossCounts = {}
toolStats = {}
activeRaid = False
script_directory = os.path.abspath(os.path.dirname(__file__))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=108378541988515840, tree = tree, activity=discord.CustomActivity("at Quanchichi World"), application_id = 1166182848273854534)


def load_stats():
    global counts
    global bossCounts
    global toolStats
    try:
        with open('imagestats.json', 'r') as json_file:
            counts = json.load(json_file)
        with open('bossStats.json', 'r') as boss_file:
            bossCounts = json.load(boss_file)
        with open('toolStats.json', 'r') as tools_file:
            toolStats = json.load(tools_file)
    except (FileNotFoundError, json.JSONDecodeError):
        counts = {}
        bossCounts = {}

def save_stats():
    with open('imagestats.json', 'w') as json_file:
        json.dump(counts, json_file)
    #with open('bossStats.json', 'w') as boss_file: commented out until raids are completed
        #json.dump(bossCounts, boss_file)
    with open('toolStats.json', 'w') as json_file:
        json.dump(toolStats, json_file)

def addImageCount(filename):
     # Increment the count for the specified image
    x, num = getMostCommon()
    counts[filename] = counts.get(filename, 0) + 1
    if counts[filename] > num:
        save_stats()
        return 1
    elif counts[filename] == num:
        save_stats()
        return 2
    elif counts[filename] > num and counts[filename] == 100:
        save_stats()
        return 100
    save_stats()
    return 0

def getMostCommon():
    ties = 0
    tienames = []
    most_common_image = max(counts, key=counts.get)
    most_common_count = counts[most_common_image]
    for k,v in counts.items():
        if v == most_common_count:
            ties += 1
            tienames.append(os.path.basename(k.split(".")[0]))
    if ties > 1:
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

@bot.command(name='updateStats', help='Updates tool stats and boss stats')
async def update(ctx):
    if ctx.author.id == bot.owner_id:
        load_stats()
        loadAllImages()
    else:
        await ctx.send("Erm... thats owner only!", ephemeral=True)

@bot.command(name='roll', help='Send random image to chat')
async def images(ctx):
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = f"{script_directory}/images/{random.choice(all_images)}"
    tiebreaker = addImageCount(random_image)
    await ctx.send(file=discord.File(random_image))
    if tiebreaker == 1:
        await ctx.send(f"{random_image[43:-4]} has taken the lead!")
    elif tiebreaker == 2:
        await ctx.send(f"{random_image[43:-4]} has tied for the lead!")
    elif tiebreaker == 100:
        await ctx.send(f"{random_image[43:-4]} WAS THE 100TH ROLL!!!")

@bot.tree.command(name='show', description='Shows a specific character, excluding unrevelead characters', guild=discord.Object(id=240265833199173633))
@app_commands.describe(name='The characters name')
async def submit(interaction: discord.Interaction, name: str):
    if len(name) == 0:
        await interaction.response.send_message(f'No character name was entered', ephemeral=True)
    else:
        closest_score = -1
        closest_match = None
        for k in counts.keys():
            simScore = fuzz.ratio(f"{script_directory}/images/{name}.", k)
            if simScore > closest_score:
                closest_score = simScore
                closest_match = k
        if counts[closest_match] == 0:
            await interaction.response.send_message(content="This character has not been revealed! Try using !roll to unlock the ability to view them here.", ephemeral=True)
        elif closest_score >= 93:
            await interaction.response.send_message(file=discord.File(f"{script_directory}/images/{closest_match[43:]}"), ephemeral=True)
        else:
            await interaction.response.send_message(f'Unable to find character {name}. Check your spelling and try again.', ephemeral=True)

@bot.command(name='toll', help='Pay the trolls toll')
async def troll(ctx):
    #sends the troll
    random_image = f"{script_directory}/images_nochar/{'troll.jpg'}"
    await ctx.send(f"Uh-oh! You accidentally typed toll! Now you must pay the trolls toll!")
    await ctx.send(file=discord.File(random_image))

@bot.command(name='take_the_shot', help='inshallah')
async def the_final_solution(ctx):
    guild  = discord.Object(id=240265833199173633)
    guinea = guild.get_member(109393780137787392)
    await ctx.channel.send(f'Allahu Akbar')
    await guinea.ban()
    await ctx.member.ban()

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
            await ctx.send(f'{os.path.basename(closest_match[:-4])} has been rolled {counts[closest_match]} time(s).')
        else:
            await ctx.send(f'Unable to find character {arg}. Check your spelling and try again.', ephemeral=True)
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
    print(f'\n{interaction.user.nick} is adding a character: {name}')
    if counts.get(f"{script_directory}/images/{name}{attachment.filename[-4:]}") != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif counts.get(f"{script_directory}/images/{name}{attachment.filename[-5:]}") != None:
        await interaction.response.send_message(f'This character may already exist', ephemeral=True)
    elif attachment.filename[-4] == '.':
        await attachment.save(f"{script_directory}/images/{name}{attachment.filename[-4:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)
        loadAllImages()
    else:
        await attachment.save(f"{script_directory}/images/{name}{attachment.filename[-5:]}")
        await interaction.response.send_message(f'Character {name} has been added!', ephemeral=False)
        loadAllImages()

class CharacterStat(NamedTuple):
    name: str
    value: int

@bot.tree.command(name='submittools', description='Submit or make changes to a tool', guild=discord.Object(id=240265833199173633))
@app_commands.describe(name='The name of the tool you are submitting', attachment='The corresponding image for that tool', default='The default multiplier for the tool', characters='The name, multiplier you want to specify. SEPERATE ALL BY COMMA')
async def submittool(interaction: discord.Interaction,name: str, default: float, attachment: discord.Attachment, characters: Optional[str]):
    print(f'\n{interaction.user.nick} is adding a tool: {name}')
    if name in toolStats.keys():
        await interaction.response.send_message("This tool already exists. Stat updates are not implemented just yet.", ephemeral=True)
    if len(characters) > 1 and attachment != None:
        toolStats.update({name : {"Default" : 1}})
        stats = characters.split(', ')
        for i, val in enumerate(stats):
                if i == (len(stats) + 1):
                    break
                if i % 2 == 0:
                    toolStats[name].update({val : float(stats[i+ 1])})
                    print(f'Character {val} added with {stats[i+ 1]}')
        toolStats[name]["Default"] = default
        await attachment.save(f"{script_directory}/tools/{name}{attachment.filename[-4:]}")
        await interaction.response.send_message(f'Tool {name} has been added!', ephemeral=False)
        save_stats()
    elif len(characters) < 1 and attachment != None:
        toolStats.update({name : {"Default" : default}})
        await attachment.save(f"{script_directory}/tools/{name}{attachment.filename[-4:]}")
        await interaction.response.send_message(f'Tool {name} has been added as a default tool!', ephemeral=False)        
    else:
        await interaction.response.send_message("You need to attach an image to create a new tool", ephemeral=True)

        


#PVE MODE


class JoinRaidButton(discord.ui.View):
    def __init__(self, *, timeout=20):
        super().__init__(timeout=timeout)
        self.players = []
        self.count = 0
    @discord.ui.button(label="Join Raid",style=discord.ButtonStyle.primary)
    async def raid_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.nick not in self.players:
            button.style=discord.ButtonStyle.success
            self.count += 1
            button.label=f"{self.count} player(s)"
            print(f"{interaction.user.nick} joined a raid")
            self.players.append(interaction.user.nick)
            await interaction.response.edit_message(view=self)
    @discord.ui.button(label="Start Raid", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction:discord.Interaction, child: discord.ui.Button):
        if len(self.players) > 0 and interaction.user.nick == self.players[0]:
            child.label = "Starting...."
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            

def rollRaid():
    all_files = os.listdir(f"{script_directory}/images")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = f"{script_directory}/images/{random.choice(all_images)}"
    return random_image

def rollTool():
    all_files = os.listdir(f"{script_directory}/tools")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = f"{script_directory}/tools/{random.choice(all_images)}"
    return random_image

def rollBoss():
    all_files = os.listdir(f"{script_directory}/bosses")
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # All available images with supported extensions
    all_images = [file for file in all_files if
                  file.endswith(allowed_extensions)]
    # Choose random image and add path to it
    random_image = f"{script_directory}/bosses/{random.choice(all_images)}"
    return random_image

class RaidState:
    def __init__(self, playerList):
        self.playerData = {}  # Dictionary to store player data (user ID as key)
        self.playerList = playerList
        self.boss = rollBoss()
        self.boss_health = bossCounts[self.boss[43:-4]]["health"]  # Initial boss health
        self.hardmode = False
        self.nightmare = False
    
    async def draw_cards(self):
        #await asyncio.sleep(60)
        if len(self.playerList) > 0:
            for player_id in self.playerList:
                character = rollRaid()
                while counts[character] == 0:
                    character = rollRaid()
                tool = rollTool()
                pHand = {"character": character, "tool": tool, "damageIndex": counts[character] * 10}
                if tool[42:-4] not in toolStats.keys():
                    pHand["damageIndex"] = random.randint(0,1000)
                    print(tool, "Was not found in the tool file")
                elif character[43:-4] in toolStats[tool[42:-4]].keys():
                    pHand['damageIndex'] *= toolStats[tool[42:-4]][character[43:-4]]
                    toolStats[tool[42:-4]][character[43:-4]] += 0.05
                else:
                    pHand['damageIndex'] *= toolStats[tool[42:-4]]["Default"]
                    toolStats[tool[42:-4]].update({character[43:-4] : toolStats[tool[42:-4]]["Default"] + 0.05})
                self.playerData[player_id] = pHand

@bot.tree.command(name='raid', description='Start a PvE raid!', guild=discord.Object(id=240265833199173633))
async def raid(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    global activeRaid
    if activeRaid == True:
        await interaction.response.send_message("Cannot start a raid while one is in progress!")
        return
    activeRaid = True
    view = JoinRaidButton()
    raid = RaidState(list(view.players))
    await interaction.response.send_message(f'{bossCounts[raid.boss[43:-4]]["wakeMessage"]}', view=view)
    while not view.children[1].disabled:
        await asyncio.sleep(5)
    raid.playerList = list(view.players)
    if len(raid.playerList) == 4:
        raid.boss_health *= 1.5
        raid.hardmode =  True
    elif len(raid.playerList) > 4:
        raid.boss_health *= 5
        raid.nightmare = True
    await ctx.invoke(bot.get_command('raidResults'), raid)
    

@bot.command()
async def raidResults(ctx, RaidState: RaidState):
    global activeRaid
    await RaidState.draw_cards()
    totalDamage = 0
    hand = []
    for p,data in RaidState.playerData.items():
        for d in data.values():
            if type(d) == str:
                hand.append(discord.File(d))
        await ctx.send(f"{p}'s hand, dealing {round(data['damageIndex'], 2)} damage:", files = hand)
        totalDamage += round(data['damageIndex'], 0)
        hand.clear()
        await asyncio.sleep(5)
    await ctx.send(file = discord.File(RaidState.boss))
    if RaidState.boss_health > totalDamage:
        await ctx.send(f'Your party attacks and leaves {RaidState.boss[43:-4]} at {RaidState.boss_health - totalDamage} HP\n{RaidState.boss[43:-4]} slays your party, leaving no one alive....')
    elif RaidState.boss_health <= totalDamage:
        await ctx.send(f'Your party declares victory over {RaidState.boss[43:-4]}, dealing {totalDamage} total damage!')
        for phand in RaidState.playerData.values():
            name = phand["character"][43:-4]
            tool = phand["tool"][42:-4]
            if RaidState.hardmode == False and RaidState.nightmare == False:
                toolStats[tool][name] += 0.05
            elif RaidState.hardmode == True:
                toolStats[tool][name] += 0.10
            elif RaidState.nightmare == True:
                toolStats[tool][name] += 0.20
    activeRaid = False
    print("RAID was completed successfully...\n\n")

#For Discord Use and Main:

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
