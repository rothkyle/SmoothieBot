import discord
import os
import requests
import json
import random
from discord.ext import commands
from keep_alive import keep_alive
from datetime import datetime
import pytz
from datetime import timedelta
import asyncio

client = commands.Bot(command_prefix="%")
streams = os.getenv('streams')
intents=intents=discord.Intents.all()
random.seed()

@client.event
async def on_ready():
  print("Bot is up and running")
  await check()

@client.event
async def on_member_join(member):
  #read file for messages
  file = open("welcome_messages.txt", "r+")
  #readlines makes a list
  messages = file.readlines()
  #strip \n from all values in messages[]
  messages.rstrip('\n')
  #retrieve channel id
  channel_id = messages[0]
  print("here")
  print(channel_id)
  print(member)
  #say hi to new member
  await client.get_channel(channel_id).send(f"Oi {member.mention}")
  #send random message
  await client.get_channel(channel_id).send(messages[random.randrange(1, len(messages))])
  print(f"{member} has joined the server")
  #assign role to new member
  #role = discord.utils.get(member.guild.roles, id=771767637432336434)
  #await client.add_roles(member, role)


@client.command()
async def welcomehere(ctx):
  if str(ctx.author) == "Sanic#8139":
    #open messages text file to set line 0 to new channel id
    print("Changed welcome channel to " + ctx.channel)
    file = open("welcome_messages.txt", "r+")
    list_of_lines = file.readlines()
    list_of_lines[0] = str(ctx.channel.id) + '\n'
    file = open("welcome_messages.txt", "w")
    file.writelines(list_of_lines)
    file.close()
    print()
  else:
    await ctx.author.send("Only Kyle can do that!")

  

@client.command()
async def weather(ctx, city):
	#request
	print("Retrieving...")
	response = requests.get(
	    "http://api.openweathermap.org/data/2.5/weather?q=" + city +
	    "&units=imperial&appid=4c0715acb4fc81b82bace4942a843378&lang=en")
	#status check and output
	if (response.status_code == 200):
		print(response.content)
		#makes a key
		json_data = json.loads(response.text)
		#uses key to create easy weather data
		weather_feels_like = str(json_data["main"]["feels_like"])
		weather_humidity = str(json_data["main"]["humidity"])
		weather_description = str(json_data["weather"][0]["description"])
		weather_description = weather_description.title()
		weather_country = str(json_data["sys"]["country"])
		weather_city = str(json_data["name"])
		weather_clouds = str(json_data["clouds"]["all"])
		city = weather_city
		response.status_code = 0
		print("Request successful for " + city + "!")
		#makes embed in discord server
		embed = discord.Embed(title="Weather",
    description="Weather in " + city + ", " +
    weather_country,
    color=discord.Color.red())
		embed.add_field(name="Feels like:",
    value=weather_feels_like + "ºF",
    inline=True)
		embed.add_field(name="Humidity:",
    value=weather_humidity + "%",
    inline=True)
		embed.add_field(name="Description:",
    value=weather_description,
    inline=True)
		embed.add_field(name="Cloudiness:",
    value=weather_clouds + "%",
    inline=True)
		await ctx.send(embed=embed)
		#await ctx.send("Feels like " + weather_feels_like + "ºF\nHumidity: " + weather_humidity + "%\nDescription: " + weather_clouds)
		print(response.status_code)
	else:
		#if something goes wrong finding the city through the api
		print(response.content)
		print("Something went wrong retrieving data from weather api for " +
		      city + ".")
		await ctx.send("Couldn't find " + city + ".")


@client.command()
async def ball(ctx):
	#request
	print("Retrieving...")
	response = requests.get(
	    "https://8ball.delegator.com/magic/JSON/randomstuff")
	print(response.content)
	json_data = json.loads(response.text)
	#use key to answer
	answer = str(json_data["magic"]["answer"])
	await ctx.send(answer)


@client.command()
async def hello(ctx):
	await ctx.send('oi punk :snake:')


@client.command()
async def flip(ctx):
	side = random.randint(1, 2)
	if (side == 1):
		await ctx.send("Heads")
	else:
		await ctx.send("Tails")


#Counter

@client.command()
async def lfg(ctx, goal, game, numHours):
  goal_actual = int(goal)
  game_actual = game
  denver = pytz.timezone('America/Denver') 
  denver_time = datetime.now(denver)
  goalTime = denver_time + timedelta(hours = float(numHours))
  goalString = str(goalTime)
  # write formatted goal to file
  formattedGoal = goalString[0:19]
  #embed
  embed = discord.Embed(title=("LFG for " + game_actual),
  description="People playing:",
  color=discord.Color.blue())
  embed.add_field(name="Players:", value="none", inline=True)
  embed.add_field(name="Goal Time:", value=str(formattedGoal), inline=False)
  message = await ctx.send("React to this message if you want to play " + game + ". We need " + goal + " people. React with ✅ to join and 🚫 to leave.")
  in_embed = await ctx.send(embed=embed)
  messageid = message.id
  channel_id = message.channel.id
  print("Channel id: " + str(channel_id))
  await message.add_reaction("✅")
  await message.add_reaction("🚫")

  #store lfg message information in text file
  nums = [0]
  files = -1
  #makes list of all file names
  f = open("file_names.txt", "r+")
  for line in f:
    fileNames = line.rstrip('\n')
    nums.append(int(fileNames))
  #assign new file a name
  for x in range(0, 100):
    checker = 0
    for val in nums:
      if (val == x):
        checker += 1
    if checker == 0:
      files = x
      f.write(str(files) + "\n")
      break
  for line in f:
    fileNames = line.rstrip('\n')
    nums.append(fileNames)
  print("NAME OF NEW FILE: " + str(files))
  f = open(str(files) + ".txt", "w")
  embed_id = in_embed.id
  guild = ctx.guild.id
  guildname = ctx.guild
  #message id line 1
  f.write(str(messageid) + "\n")
  #channel id line 2
  f.write(str(channel_id) + "\n")
  #emebed_id line 3
  f.write(str(embed_id) + "\n")
  #game_actual line 4
  f.write(str(game_actual) + "\n")
  #goal_actual line 5
  f.write(str(goal_actual) + "\n")
  #guild id line 6
  f.write(str(guild) + "\n")
  #guild name line 7
  f.write(str(guildname) + "\n")
  #goal time line 8
  f.write(str(formattedGoal) + "\n")
  f.close()
  print("Created counter for " + game_actual + " in " + message.guild.name)

#reaction checker
@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot == False:
    f = open("file_names.txt", "r")
    messageid = 0
    fileNames = []
    file_data = []
		#retrieve file names from folder
    for x in f:
      file = x.rstrip('\n')
      fileNames.append(file + ".txt")
    f.close()
		#check if message id's match
    for x in fileNames:
      global fileNameTrue
      fileNameTrue = x
      f = open(x, "r+")
      messageid = int(f.readline().rstrip('\n'))
      #creates list if message id match is found
      if (int(messageid) == int(payload.message_id)):
        count = 0
        global realFileName
        realFileName = x
        p = open(x, "r+")
        for x in p:
          file = x.rstrip('\n')
          file_data.append(file)
        #assigning variables from list
        messageid = int(file_data[0])
        embed_id = int(file_data[2])
        game_actual = file_data[3]
        goal_actual = int(file_data[4])
        guild_id = int(file_data[5])
        guild = file_data[6]
        goal_time = file_data[7]
        names = []
        channel = client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(messageid)
        in_embed = await channel.fetch_message(embed_id)
        guild = client.get_guild(guild_id)
        print(str(guild))
        #retrieve player ids from files
        for x in range(8, len(file_data)):
          playerid = file_data[x]
          playerid.rstrip('\n')
          member_obj = await client.fetch_user(playerid)
          names.append(member_obj)
        count = len(file_data) - 8
        global send_out
        #print(file_data)
        break
    if(payload.message_id == messageid):
      if str(payload.emoji.name) == "✅":
        if payload.member not in names:
          send_out = ""
          #retrieve member id from person who reacted
          names.append(payload.member)
          member = str(payload.member.id)
          #write id to file
          p.write(member + "\n")
          count += 1
          for member in names:
            print(str(member))
            send_out += (member.mention + "\n")
          des = str("People playing: " + str(count))
          new_info = discord.Embed(title=("LFG for " + str(game_actual)), description=des, color=discord.Color.blue())
          new_info.add_field(name="Players:", value=send_out, inline=True)
          new_info.add_field(name="Goal Time", value=goal_time, inline=False)
          await in_embed.edit(embed=new_info)
          p.close()
          await msg.remove_reaction("✅", payload.member)
          #met goal
          if (count == goal_actual):
            send_out = ""
            print("Goal has been reached.")
            await channel.send("We now have " + str(goal_actual) + " for " + str(game_actual) + "!")
            for member in names:
              send_out += (member.mention + "\n")
            await channel.send(send_out)
            names.clear()
            os.remove(fileNameTrue)
            print("File count subtracted")
            #remove name of file from list
            n = open("file_names.txt", "r+")
            global fileNameList
            fileNameTrue = fileNameTrue.replace('.txt', '')
            fileNameList = []
            print(fileNameTrue)
            #copies all number that dont match to file name to list then deletes and
            #rewrites whole file
            for num in n:
              fileName = num.rstrip('\n')
              if (fileName != fileNameTrue):
                fileNameList.append(fileName)
            n.truncate(0)
            n.close()
            n = open("file_names.txt", "a")
            for name in fileNameList:
              n.write(str(name) + "\n")
            n.close()
          #not met goal
          else:
            print("Detected reaction from " + str(payload.member) + ". There are is now ", count, " out of ", goal_actual, " people ready to play " + game_actual + ".")
        else:
          print(payload.member.name + " already in queue.")
          p.close()
      #remove from lfg
      elif str(payload.emoji.name) == "🚫":
        if payload.member in names:
          send_out = ""
          count -= 1
          names.remove(payload.member)
          print(str(payload.member) + " has left the lfg")
          des = str("People playing: " + str(count))
          if names == []:
            send_out = "none"
          else:
            for member in names:
              send_out += (member.mention + "\n")
          #embed
          new_info = discord.Embed(title=("LFG for " + str(game_actual)),description=des, color=discord.Color.blue())
          new_info.add_field(name="Players:", value=send_out, inline=True)
          new_info.add_field(name="Goal Time", value=goal_time, inline=False)
          await in_embed.edit(embed=new_info)
          #remove id from file
          fileInfo = []
          n = open(realFileName, "r+")
          for line in n:
            information = line.rstrip('\n')
            if (str(information) != str(payload.member.id)):
              fileInfo.append(str(information))
          n.truncate(0)
          n.close()
          n = open(realFileName, "a")
          for line in fileInfo:
            n.write(str(line) + "\n")
          n.close()
        await msg.remove_reaction("🚫", payload.member)


@client.command()
async def check():
  denver = pytz.timezone('America/Denver') 
  denver_time = datetime.now(denver)
  #formattedDenver = denver_time.strftime("%m-%d-%Y %H:%M:%S")
  goalTime = denver_time + timedelta(hours = 1)
  goalString = str(goalTime)
  # write formatted goal to file
  formattedGoal = goalString[0:19]
  print(formattedGoal)
  # this is for file extraction
  extractedNew = datetime.strptime(formattedGoal, "%Y-%m-%d %H:%M:%S")
  print(extractedNew)
  await asyncio.sleep(60)
  await check()
  

#@client.command()
#async def zoop(ctx):
# playerid = "279056911926689793"
#discordFetched = await client.fetch_user(playerid)
#await ctx.send(discordFetched.mention)
#channel_id = 810776540601647107
#message_id = 857162619857010699
#channel = client.get_channel(channel_id)
#in_embed = await channel.fetch_message(message_id)
#new_info = discord.Embed(
#title = ("zoop"),
#description = "wowie",
#color = discord.Color.blue()
#)
#send_out = member.mention list of all players    REMEMBER
#new_info.add_field(name = "Players:", value = send_out, inline = True)
#await in_embed.edit(embed = new_info)

keep_alive()
client.run(os.getenv('daKey'))
