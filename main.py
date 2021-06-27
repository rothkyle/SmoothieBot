import discord
import os
import requests
import json
import random
from discord.ext import commands
from keep_alive import keep_alive
import asyncio
client = commands.Bot(command_prefix="%")
streams = os.getenv('streams')
@client.event
async def on_ready():
  print("Bot is up and running")

@client.command()
async def weather(ctx, city):
  #request
  print("Retrieving...")
  response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&units=imperial&appid=4c0715acb4fc81b82bace4942a843378&lang=en")
  #status check and output
  if (response.status_code == 200):
    print (response.content)
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
    embed = discord.Embed(
      title = "Weather",
      description = "Weather in " + city + ", " + weather_country,
      color = discord.Color.red()
    )
    embed.add_field(name = "Feels like:", value = weather_feels_like + "ºF", inline = True)
    embed.add_field(name = "Humidity:", value = weather_humidity + "%", inline = True)
    embed.add_field(name = "Description:", value = weather_description, inline = True)
    embed.add_field(name = "Cloudiness:", value = weather_clouds + "%", inline = True)
    await ctx.send(embed = embed)
    #await ctx.send("Feels like " + weather_feels_like + "ºF\nHumidity: " + weather_humidity + "%\nDescription: " + weather_clouds)
    print(response.status_code)
  else:
    #if something goes wrong finding the city through the api
    print (response.content)
    print("Something went wrong retrieving data from weather api for " + city + ".")
    await ctx.send("Couldn't find "+ city + ".")

@client.command()
async def ball(ctx):
  #request
  print("Retrieving...")
  response = requests.get("https://8ball.delegator.com/magic/JSON/randomstuff")
  print (response.content)
  json_data = json.loads(response.text)
  #use key to answer
  answer = str(json_data["magic"]["answer"])
  await ctx.send(answer)
  
@client.command()
async def hello(ctx):
  await ctx.send('oi punk :snake:')
@client.command()
async def flip(ctx):
  side = random.randint(1,2)
  if (side == 1):
    await ctx.send("Heads")
  else:
    await ctx.send("Tails")
#Counter
count = int(0)
goal_actual = int(0)
game_actual = str()
names = []
messageid = int(0)
send_out = str()
channel_id = int(0)
@client.command()
async def lfg(ctx, goal, game):
  names.clear()
  goal_actual = int(goal)
  game_actual = game
  #embed
  embed = discord.Embed(
      title = ("LFG for " + game_actual),
      description = "People playing:",
      color = discord.Color.blue()
    )
  embed.add_field(name = "Players:", value = "none", inline = True)
  message = await ctx.send("React to this message if you want to play " + game + ". We need "+ goal + " people. React with ✅ to join and 🚫 to leave. @here")
  in_embed = await ctx.send(embed = embed)
  messageid = message.id
  channel_id = message.channel.id
  print("Channel id: " + str(channel_id))
  await message.add_reaction("✅")
  await message.add_reaction("🚫")

  #store lfg message information in text file
  nums = [0]
  files = -1
  checker = 0
  #makes list of all file names
  f = open("file_names.txt", "r+")
  for line in f:
    fileNames = line.rstrip('\n')
    nums.append(int(fileNames))
  #assign new file a name
  for x in range(0,100):
    checker = 0
    for val in nums:
      if (val == x):
        checker += 1
    print("CHECKER: "+ str(checker))
    if (checker == 0):
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
  f.close()
  print ("Created counter for " + game_actual + " in " + message.guild.name)


#reaction checker
@client.event
async def on_raw_reaction_add(payload):
  f = open("file_names.txt", "r")
  fileNames = []
  file_data = []
  #retrieve file names from folder
  for x in f:
    file = x.rstrip('\n')
    fileNames.append(file + ".txt")
  #check if message id's match
  for x in fileNames:
    global fileNameTrue
    fileNameTrue = x
    f = open(x, "r+")
    messageid = f.readline().rstrip('\n')
    print("Matching...")
    #creates list if message id match is found
    if (int(messageid) == int(payload.message_id)):
      print("Match found!")
      count = 0
      p = open(x, "r+")
      global file_name
      file_name = p
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
      names = []
      channel = client.get_channel(payload.channel_id)
      msg = await channel.fetch_message(messageid)
      in_embed = await channel.fetch_message(embed_id)
      guild = client.get_guild(guild_id)
      print(str(guild))
      #retrieve player ids from files
      for x in range(7,len(file_data)):
        playerid = file_data[x]
        playerid.rstrip('\n')
        member_obj = await client.fetch_user(playerid)
        names.append(member_obj)
        count += 1
      count = len(file_data) - 7
      global send_out
      #print(file_data)
      break
  if str(payload.emoji.name) == "✅" and int(payload.message_id) == int(messageid):
    if payload.member.bot == False:
      await msg.remove_reaction("✅", payload.member)
      if payload.message_id == messageid and payload.member.bot == False and payload.member not in names:
          send_out = ""
          #retrieve member id from person who reacted
          names.append(payload.member)
          member = str(payload.member.id)
          #write id to file
          file_name.write(member + "\n")
          count += 1
          for member in names:
            print(str(member))
            send_out += (member.mention)
          des = str("People playing: " + str(count))
          new_info = discord.Embed(
          title = ("LFG for " + str(game_actual)),
          description = des,
          color = discord.Color.blue()
          )
          new_info.add_field(name = "Players:", value = send_out, inline = True)
          await in_embed.edit(embed=new_info)
      else:
        print(payload.member.name + " already in queue.")

      #met goal
      if (count == goal_actual):
        send_out = ""
        print("Goal has been reached.")
        await channel.send("We now have " + str(goal_actual) + " for " + str(game_actual) + "!")
        for member in names:
          send_out += (member.mention)
        await channel.send(send_out)
        names.clear()
        os.remove(fileNameTrue)
        print("File count subtracted")
        #remove name of file from list
        n = open("file_names.txt", "r+")
        global fileNameList
        fileNameTrue.replace('.txt', '')
        fileNameList = []
        print(fileNameTrue)
        #copies all number that dont match to file name to list then deletes and
        #rewrites whole file
        for num in n:
          fileName = num.rstrip('\n')
          if(fileName != fileNameTrue):
            print(fileName + " made it")
            fileNameList.append(fileName)
        n.truncate(0)
        n.close()
        n = open("file_names.txt", "a")
        for name in fileNameList:
          n.write(str(name) + "\n")
        n.close()
      #not met goal
      else:
        print("Detected reaction from " + str(payload.member) + ". There are is now " , count ,  " people ready.")
  
  #remove from lfg
  if str(payload.emoji.name) == "🚫" and payload.message_id == messageid:
    if payload.member.bot == False:
      await msg.remove_reaction("🚫", payload.member)
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
        new_info = discord.Embed(
        title = ("LFG for " + str(game_actual)),
        description = des,
        color = discord.Color.blue()
      )
      new_info.add_field(name = "Players:", value = send_out, inline = True)
      await in_embed.edit(embed=new_info)
      await msg.remove_reaction("🚫", payload.member)
    else:
      print(payload.member.name + " can't leave queue while not in queue")

@client.command()
async def info(ctx, file, adsub , stream):
  newList = []
  f = open(str(file), "r+")
  #check if streamer is already in the list
  participating = False
  for x in f:
    if str(stream) in x:
      participating = True
  print("Streamer on list: " + str(participating))
  #close and open file
  f.close()
  if not participating and adsub == "add":
    f = open(str(file), "a")
    f.write(f"{stream}\n")
    f.close()
  #make it remove "stream" from text file
  if participating and adsub == "remove":
    f = open(str(file), "r+")
    #makes list of streams not including removed one
    for line in f:
      if str(stream) not in line:
        newList.append(line)
        print(line)
    f.truncate(0)
    f = open(str(file), "r+")
    for x in newList:
      f.write(f"{x}")
    print("Stream should be removed")
    print(newList)
    f.close()
  #updated streamer list printed
  f = open(str(file), "r+")
  for x in f:
    print(x)
  f.close()

async def checkstreamers():
  await client.wait_until_ready()
  global streamers
  while not client.is_closed():
    try:
      with open("streamers.txt", "a") as f:
        print("yo momma")
        await asyncio.sleep(5)
    except Exception as e:
        print(e)
        await asyncio.sleep(5)

# @client.command()
# async def check(ctx):
#   message = await ctx.send("Woop")
#   message = message.id
#   outfile = open("moo",'wb')
#   dill.dump(message, outfile)
#   outfile.close()
#   infile = open("moo", 'rb')
#   speak = dill.load(infile)
#   await ctx.send(speak)

@client.command()
async def zoop(ctx):
  playerid = "279056911926689793"
  discordFetched = await client.fetch_user(playerid)
  await ctx.send(discordFetched.mention)
  channel_id = 810776540601647107
  message_id = 857162619857010699
  channel = client.get_channel(channel_id)
  in_embed = await channel.fetch_message(message_id)
  new_info = discord.Embed(
    title = ("zoop"),
    description = "wowie",
    color = discord.Color.blue()
  )
  #send_out = member.mention list of all players    REMEMBER
  #new_info.add_field(name = "Players:", value = send_out, inline = True)
  await in_embed.edit(embed = new_info)


@client.command()
async def tester(ctx):
  ctx.send("@Sanic#8139")
  def fileCounter():
    n = open("fileNumbers.txt","r+")
    for line in n:
      global current
      current = int(line)
    n.close()
    int(current)
    return current

  async def fileChanger(adsub):
    if (adsub == "add"):
      new = int(fileCounter()) + 1
      n = open("fileNumbers.txt","r+")
      n.truncate()
      n.write(f"{new}")
      n.close
      print("File count added")
      print("Number of lfg files: " + str(new))

    if (adsub == "subtract"):
      new = int(fileCounter()) - 1
      n = open("fileNumbers.txt","r+")
      n.truncate()
      n.write(f"{new}")
      n.close
      print("File count subtracted")
      print("Number of lfg files: " + str(new))
  await fileChanger("add")

  

keep_alive()
client.run(os.getenv('daKey'))
