import os

import discord
from discord.ext.commands import *
from discord.ext import commands
import subprocess
import re
from auth import DISCORD_TOKEN

bot = commands.Bot(command_prefix="IMPERIAL")

@bot.event
async def on_message(message):
  roles = [role.name for role in message.author.roles]
  print(roles)

  restart_search = re.search('RESTART: (.+)',message.content)
  if restart_search:
      subprocess.call(['bash','acceptAmendment.sh',restart_search.group(1),'&'])
      exit()
      
  test1_search = re.search('TEST1',message.content)
  if test1_search:
    await message.reply(content="I can be updated now")
    return

  if message.content.startswith("OFFICIAL PROPOSAL:"):

    # Check if author is part of the Imperial Senate
    if 'ImperialSenator' not in roles and 'Emperor' not in roles:
      # Reject the Message
      await message.reply(content="You are not an Imperial Senator, so your proposal is immediately rejected.")
      return

def isSenator(user):
    return 'ImperialSenator' in user.roles

def isEmperor(user):
    return 'Emperor' in user.roles

async def getSenateSupportCount(reaction):
    # Assume reaction is upvote
    users = await reaction.users().flatten()
    votes = filter(isSenator,users)
    return len(votes)

def getTotalSenators(reaction):
    senators = filter(isSenator,reaction.message.channel.members)
    return len(senators)

async def getEmperorSupport(reaction):
    users = await reaction.users().flatten()
    votes = filter(isEmperor,users)
    return len(votes)>0

@bot.event
async def on_reaction_add(reaction, user):
  if reaction.message.content.startswith("OFFICIAL PROPOSAL:"):
    # Check if author is part of the Imperial Senate
    roles = [role.name for role in reaction.message.author.roles]
    print(roles)
    if 'ImperialSenator' in roles or 'Emperor' in roles:
      byteString = b'\xe2\xac\x86\xef\xb8\x8f'
      actualString = bytes(str(reaction.emoji),'utf-8')
      if actualString == byteString:
        # Check if there is a super majority of senators who have voted
        # Or if emperor + simple majority
        senatorSupportCount = await getSenateSupportCount(reaction)
        totalSenators = getTotalSenators(reaction)
        emperorSupport = await getEmperorSupport(reaction)
        await reaction.message.reply(content=f"Senate support: {senatorSupportCount}\nTotal senators: {totalSenators}\nEmperor support: {emperorSupport}")
      else:
        await reaction.message.reply(content=reaction.emoji)

bot.run(DISCORD_TOKEN)
