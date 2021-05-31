import os
import logging as log
import discord
from discord.ext.commands import *
from discord.ext import commands
import subprocess
import traceback
import string
import unicodedata
import re
import confusables
from auth import DISCORD_TOKEN
from trim import trim_nl
import json

# TODO: show typing when in progress

extensions = []

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

def readBans():
  try:
    with open('bans', 'r') as f:
      return(json.load(f))
  except:
    print('Error with reading bans')
    return {}

@bot.event
async def on_message(message):
  if message.channel.name != 'the-empire':
    return
  await bot.process_commands(message)
  if await check_bans(message):
      return
  await verify_role(message)

@bot.event
async def on_message_edit(before, after):
  if before.channel.category.name != 'THE EMPIRE':
    return
  await check_bans(after)

async def verify_role(message):
  roles = [role.name for role in message.author.roles]
  if 'Emperor' in roles:
    await message.add_reaction(u"\U0001F396")
  if 'ImperialSenator' in roles:
    await message.add_reaction(u"\U0001FA99")
  if 'Jester' in roles:
    await message.add_reaction(u"\U0001f921")

def normalize(message):
    msg2 = ''
    prev_c = '\x00'
    for c in message:
        c = unicodedata.normalize('NFKD', c)[0]
        if c in string.punctuation or c in string.whitespace:
            continue
        if c == '@': c = 'a'
        c = c.lower()
        if prev_c == c:
            continue
        prev_c = c
        msg2 += c
    return msg2

def get_confusables(message):
    msg2 = normalize(message)
    return [m.lower() for m in confusables.normalizes(msg2)]

async def check_bans(message):
    if message.author.id == bot.user.id:
        return False
    bans = readBans()
    nmsg = normalize(message.content)
    for ban in bans.values():
        patt = re.compile(confusables.confusable_regex(ban['word']))
        if patt.search(nmsg):
            print('Banned: ' + message.content)
            msg = f"<@{message.author.id}> This message uses forbidden language."
            await message.reply(content=msg)
            await message.delete()
            return True
    return False

@bot.event
async def on_error(evt_type, *args, **kwargs):
    if evt_type == 'on_message':
        await args[0].reply('An error has occurred... :disappointed:')
        await args[0].reply(traceback.format_exc())
    log.error(f'Ignoring exception at {evt_type}')
    log.error(traceback.format_exc())


@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, MissingPermissions):
        await ctx.send('You do not have permission to do that! ¯\_(ツ)_/¯')
    elif isinstance(err, MissingRequiredArgument):
        await ctx.send(':bangbang: Missing arguments to command');
    elif isinstance(err, BotMissingPermissions):
        await ctx.send(trim_nl(f''':cry: I can\'t do that. Please ask server ops
        to add all the permission for me!

        ```{str(err)}```'''))
    elif isinstance(err, DisabledCommand):
        await ctx.send(':skull: Command has been disabled!')
    elif isinstance(err, CommandNotFound):
        await ctx.send(f'Invalid command passed. Use {bot.command_prefix}help.')
    elif isinstance(err, NoPrivateMessage):
        await ctx.send(':bangbang: This command cannot be used in PMs.')
    else:
        await ctx.send('An error has occurred... :disappointed:')
        await ctx.send(''.join(traceback.format_exception(type(err), err,
                err.__traceback__)))
        log.error(f'Ignoring exception in command {ctx.command}')
        log.error(''.join(traceback.format_exception(type(err), err,
                err.__traceback__)))

if __name__ == '__main__':
    for extension in os.listdir('cogs'):
        if extension.endswith('.py'):
            extension = extension[:-3]
        else:
            continue
        print(f'Loading cog {extension}')
        bot.load_extension('cogs.' + extension)

    print("Starting bot...")
    bot.run(DISCORD_TOKEN)
