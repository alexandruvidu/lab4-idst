#!./.venv/bin/python

#   Copyright 2021 Alexandru Vidu

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


import discord
import code
import os
import inspect
import random
import argparse

from discord.ext import commands
from discord.player import AudioSource

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

bot = commands.Bot(command_prefix='!')
currentdir = os.getcwd()

@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')


@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    await bot.process_commands(msg)


@bot.event
async def on_voice_state_update(member, before, after):
    voice_status = member.guild.voice_client
    if voice_status is None:
        return
    if len(voice_status.channel.members) == 1:
        voice_status.stop()
        await voice_status.disconnect()
   



@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))


@bot.command(brief='Play a song from file')
async def play(ctx, song: str):
    if song in os.listdir(currentdir):
        if ctx.author.voice is None:
            await ctx.send("User is not in a voice channel")
        else:
            if ctx.voice_client is not None:
                if ctx.voice_client.is_playing():
                    await ctx.send("Bot is already playing")
                else:
                    ctx.voice_client.play(discord.FFmpegPCMAudio(song))       
            else:
                if ctx.voice_client is None:
                    await ctx.author.voice.channel.connect()
                    ctx.voice_client.play(discord.FFmpegPCMAudio(song))
                    await ctx.send(f"Bot connected, playing {song}")
    else:
        await ctx.send("Song not found")


@bot.command(brief='Show a list of all songs available to play')
async def list(ctx):
    await ctx.send("Songs available to play:")
    for file in os.listdir(currentdir):
        if file.endswith(".mp3"):
            await ctx.send(file)


@bot.command(brief='Disconnect the bot')
async def scram(ctx):
    if ctx.voice_client is None:
        await ctx.send("Bot is not connected")
    else:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Bot disconnected")




@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))

@play.error
async def play_error(ctx, error):
    await ctx.send(str(error))

@list.error
async def list_error(ctx, error):
    await ctx.send(str(error))

@scram.error
async def scram_error(ctx, error):
    await ctx.send(str(error))

################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', nargs='?')
    args = parser.parse_args()

    if args.token is not None:
        token = args.token
    elif 'BOT_TOKEN' in os.environ:
        token = os.environ['BOT_TOKEN']
    else:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)

    bot.run(token)
