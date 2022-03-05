# TODO add database integration, add queue time holding for a time of {customizable} mins, add time spent in battle room


import datetime

import discord
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv
import time
import math
import databaseFunctions as db

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

guildInfo = {}


@client.event
async def on_message(message):
    botPrefix = db.get_bot_prefix(message.guild.id)

    if message.author.id == client.user.id or not message.content.startswith(botPrefix):
        return

    # Removes the botprefix from start of the message, then splits them into separate args
    args = message.content[len(botPrefix):].lower().split()

    if args[0] == "help":
        await message.channel.send(
            """Command List: 
            {{}} are for required parameters
            [] are for optional parameters
            
            {0}help : Shows all available commands
            {0}set voiceid {{voice channel id}} : Sets voice channel id
            {0}set textid {{text channel id}} : Sets text channel id
            {0}set prefix {{prefix}} : Sets bot prefix
            {0}set savetime {{time in minutes}} : Sets the time that a player's queue time will be retained for in minutes
            {0}get voiceid : Gets current voice channel id
            {0}get textid : Gets current text channel id
            {0}get prefix : Gets current bot prefix (most useful command ever)
            {0}get savetime: Gets the time that a player's queue time will be retained for in minutes
            {0}list {{player name}} [number of queues to list] DEFAULT 10 : Lists player's queue times with dates.""".format(
                botPrefix))
    elif args[0] == "set":
        if len(args) >= 2:
            if args[1] == "voiceid":
                if len(args) == 3:

                    if args[2].isnumeric():
                        channel = client.get_channel(int(args[2]))
                        if channel:
                            if channel.type[0] == "voice":
                                db.set_voice_id(message.guild.id, int(args[2]))
                                await message.channel.send("Voice id is now {0}".format(int(args[2])))
                            else:
                                await message.channel.send(
                                    "Please provide a voiceid and not a textid. Type {0}help for more information".format(
                                        botPrefix))
                        else:
                            await message.channel.send(
                                "Invalid id, no channel with this id exists. Type {0}help for more information".format(
                                    botPrefix))
                    else:
                        await message.channel.send(
                            "The voiceid must be an integer. Type {0}help for more information".format(botPrefix))
                else:
                    await message.channel.send(
                        "Please provide a voiceid. Type {0}help for more information".format(botPrefix))
            elif args[1] == "textid":
                if len(args) == 3:
                    if args[2].isnumeric():
                        channel = client.get_channel(int(args[2]))
                        if channel:
                            if channel.type[0] == "text":
                                db.set_text_id(message.guild.id, int(args[2]))
                                await message.channel.send("Text id is now {0}".format(int(args[2])))
                            else:
                                await message.channel.send(
                                    "Please provide a textid and not a voiceid. Type {0}help for more information".format(
                                        botPrefix))
                        else:
                            await message.channel.send(
                                "Invalid id, no channel with this id exists. Type {0}help for more information".format(
                                    botPrefix))
                    else:
                        await message.channel.send(
                            "The textid must be an integer. Type {0}help for more information".format(botPrefix))
                else:
                    await message.channel.send(
                        "Please provide a textid. Type {0}help for more information".format(botPrefix))
            elif args[1] == "prefix":
                if len(args) >= 3:
                    db.set_bot_prefix(message.guild.id, args[2])
                    await message.channel.send(
                        "Bot prefix is now {0}".format(
                            args[2]))
                else:
                    await message.channel.send(
                        "Please provide a prefix to set. Type {0}help for more information".format(
                            botPrefix))
            elif args[1] == "savetime":
                if len(args) == 3:
                    if args[2].isnumeric():
                        if int(args[2]) >= 0:
                            db.set_queue_save_time_id(message.guild.id, int(args[2]))
                            await message.channel.send(
                                "Savetime is now {0} minutes".format(
                                    args[2]))
                        else:
                            await message.channel.send(
                                "The savetime must be an integer larger or equal to zero. Type {0}help for more information".format(
                                    botPrefix))
                    else:
                        await message.channel.send(
                            "The savetime must be an integer. Type {0}help for more information".format(botPrefix))
                else:
                    await message.channel.send(
                        "Please provide a savetime. Type {0}help for more information".format(botPrefix))
            else:
                await message.channel.send(
                    "Unkown paramater. Type {0}help for more information".format(
                        botPrefix))
        else:
            await message.channel.send(
                "Please provide a parameter for the id you want to set, it may be voiceid or textid. Type {0}help for more information".format(
                    botPrefix))
    elif args[0] == "get" and len(args) == 2:
        if len(args) >= 2:
            if args[1] == "voiceid":
                await message.channel.send("Current voiceid is {0}".format(db.get_voice_id(message.guild.id)))
            elif args[1] == "textid":
                await message.channel.send("Current textid is {0}".format(db.get_text_id(message.guild.id)))
            elif args[1] == "prefix":
                await message.channel.send("Current prefix is {0}".format(db.get_bot_prefix(message.guild.id)))
            elif args[1] == "savetime":
                await message.channel.send(
                    "Current savetime is {0} minutes".format(db.get_queue_save_time(message.guild.id)))
        else:
            await message.channel.send(
                "Please provide a parameter for what you want to get. Type {0}help for more information".format(
                    botPrefix))
    elif args[0] == "list":
        if len(args) >= 2:
            memberId = find_member_id_by_name(message.guild, args[1])
            if memberId:
                if len(args) >= 3:
                    if args[2].isnumeric() and int(args[2]) > 0:
                        await message.channel.send(
                            create_member_queue_list_message(message.guild.id, memberId, int(args[2])))
                    else:
                        await message.channel.send(
                            "Please provide a positive integer for the amount of queues to list. Type {0}help for more information".format(
                                botPrefix))
                else:
                    await message.channel.send(create_member_queue_list_message(message.guild.id, memberId))
            else:
                await message.channel.send(
                    "Please provide a valid member name. Type {0}help for more information".format(botPrefix))
        else:
            await message.channel.send(
                "Please provide a player name to list queues for. Type {0}help for more information".format(botPrefix))
    else:
        await message.channel.send("Unknown command. Type {0}help for more information.".format(botPrefix))


@client.event
async def on_ready():
    print("Logged in as {0}".format(client.user))

    guildInfo.clear()
    for guild in client.guilds:
        # Checks to see if there is a preferences entry in the database for the guild, and if there isn't one creates one
        db.create_default_preferences_if_not_in_db(guild.id)

        update_list(guild)


@client.event
async def on_guild_join(guild):
    db.create_default_preferences_if_not_in_db(guild.id)


@tasks.loop(seconds=1)
async def queue_message_loop():
    for guild in client.guilds:
        textChannelId = db.get_text_id(guild.id)

        if not textChannelId:
            continue

        textChannel = client.get_channel(textChannelId)

        if guild.id not in guildInfo.keys() or not textChannel:
            continue

        remove_expired_queue_entries(guild.id)

        lastMessage = textChannel.last_message

        firstMsg = True

        if lastMessage is None:
            await textChannel.send(content=create_current_queue_message(guild.id))
        elif lastMessage is not None and lastMessage.author.id != client.user.id:
            await textChannel.send(content=create_current_queue_message(guild.id))
        else:
            await lastMessage.edit(content=create_current_queue_message(guild.id))

        async for msg in textChannel.history(limit=20):
            if firstMsg:
                firstMsg = False
                continue
            else:
                if msg.author.id == client.user.id:
                    await msg.delete()


@client.event
async def on_voice_state_update(member, before, after):
    voiceChatId = db.get_voice_id(member.guild.id)

    if not voiceChatId:
        return

    if after.channel is not None and after.channel.id == voiceChatId:
        update_list(after.channel.guild)
    elif before.channel is not None and before.channel.id == voiceChatId:
        update_list(before.channel.guild)


def update_list(guild):
    guildId = guild.id

    voiceChatId = db.get_voice_id(guild.id)

    # Checks to see if voicechat exists, if so initializes a variable
    if not voiceChatId:
        return

    voiceChat = client.get_channel(voiceChatId)

    # Checks if dict has already been created for the current guild the list is being updated for
    if guildId not in guildInfo.keys():
        # This creates a dictionary which will be used to hold member_name and the value
        guildInfo[guildId] = {}

    # Iterates through all members in the guildInfo to check if anyone has left, it uses a copy of the guildInfo as otherwise the dictionary will change size during the iteration and a runtime error will happen
    for memberId, memberInfo in guildInfo[guildId].items():
        # Checks if the current key being checked is in the dictionary, if not this means that this player has now left, and so this entry will be removed
        memberIdInList = False
        for i in range(0, len(voiceChat.members)):
            if memberId == voiceChat.members[i].id:
                memberIdInList = True

        if not memberIdInList:
            # If they are not in the memberlist and also don't have a last seen entry sets last_seen entry
            if not memberInfo["last_seen"]:
                memberInfo["last_seen"] = time.time()
            # The code for members leaving is in the queue message loop as times since queue departure has to be checked

    # Then does stuff for all the members in the voice channel
    for member in voiceChat.members:
        # If there already isn't an entry for this member then that means that this member has just joined, otherwise does nothing as the member is still in the voice channel
        if member.id not in guildInfo[guildId].keys():
            guildInfo[guildId][member.id] = {"time_joined": time.time(), "last_seen": None}
            print("Member {0} has joined at {1}".format(member.name, time.ctime(time.time())))
        # Otherwise, sets the last_seen for all other members to none so that we know they're still in the voice channel
        else:
            guildInfo[guildId][member.id]["last_seen"] = None


def find_member_id_by_name(guild, memberName):
    for member in guild.members:
        if member.name.lower() == memberName:
            return member.id
    return None


def remove_expired_queue_entries(guildId):
    for memberId, memberInfo in guildInfo[guildId].copy().items():
        # If member has not been in queue for more than savetime minutes, their entry gets popped
        if memberInfo["last_seen"] and time.time() - memberInfo["last_seen"] > db.get_queue_save_time(guildId) * 60:
            # Removes the time entry for this member so that when the code runs again it will know that the player has already left
            guildInfo[guildId].pop(memberId)

            # time.time() gives the current time and when subtracted from the value, it gives the time elapsed since they joined and mod 60 gives the seconds
            timeElapsed = time.time() - memberInfo["time_joined"]

            db.write_member_info(guildId, memberId, time.time(), timeElapsed)

            print("Member {0} has left after {1} minutes and {2} seconds in the queue.\n".format(
                client.get_user(memberId),
                int(timeElapsed / 60),
                int(timeElapsed % 60)))


def create_current_queue_message(guildId):
    memberDict = guildInfo[guildId]
    message = ""
    counter = 1
    for memberId, memberInfo in memberDict.items():
        memberName = client.get_user(memberId).name
        hours = int((time.time() - memberInfo["time_joined"]) / 3600)
        minutes = int((time.time() - memberInfo["time_joined"]) % 3600 / 60)
        seconds = int((time.time() - memberInfo["time_joined"]) % 3600 % 60)

        message += "    {0}. {1}".format(counter, memberName)

        for i in range(0, 14 - int(math.log(counter, 10)) - len(memberName)):
            message += " "

        message += "{0}h {1}m {2}s".format(hours, minutes, seconds)
        for i in range(0, 8 - number_length_minus_one(hours, 10) - number_length_minus_one(minutes,
                                                                                           10) - number_length_minus_one(
            seconds, 10)):
            message += " "

        if memberInfo["last_seen"]:
            timeLeftBeforeRemoval = db.get_queue_save_time(guildId) * 60 - (time.time() - memberInfo["last_seen"])
            message += "(Currently not in queue, entry will be removed in {0}m {1}s)".format(
                int(timeLeftBeforeRemoval / 60), int(timeLeftBeforeRemoval % 60))
        message += "\n"
        counter += 1
    return "```List of users in the queue: \n" + message + "```"


def create_member_queue_list_message(guildId, memberId, queueCountToList=10):
    message = ""
    counter = 1
    memberName = client.get_user(memberId).name
    rowList = db.get_queue_times(guildId, memberId, queueCountToList)

    for row in rowList:
        timeInQueue = row["time_in_queue"]
        joinTime = row["timestamp"]

        hours = int(timeInQueue / 3600)
        minutes = int(timeInQueue % 3600 / 60)
        seconds = int(timeInQueue % 3600 % 60)

        message += "{0}.".format(counter)
        for i in range(0, 4 - number_length_minus_one(counter, 10)):
            message += " "

        message += "{1}h {2}m {3}s".format(counter, hours, minutes, seconds)

        for i in range(0, 8 - number_length_minus_one(hours, 10) - number_length_minus_one(minutes,
                                                                                           10) - number_length_minus_one(
            seconds, 10)):
            message += " "
        # TODO find shit for time.time() library timezone whatever thingy you know
        message += "Date: {0} UTC\n".format(time.ctime(joinTime - 10800))

        counter += 1
    return f"```Listing last {len(rowList)} queue times for {memberName}:\n" + message + "```"


def number_length_minus_one(x, base):
    if x == 0:
        return 0
    counter = 0

    while True:
        if x / base >= 1:
            x /= base
            counter += 1
        else:
            break
    return counter


queue_message_loop.start()
load_dotenv(".env")
client.run(os.getenv("TOKEN"))
