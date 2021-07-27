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
import youtube_dl
import validators

streams = os.getenv('streams')
random.seed()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="%", intents = intents)


@client.event
async def on_ready():
  print("Bot is up and running")
  asyncio.create_task(check())
  #asyncio.create_task(currency_update())


@client.command()
async def poker(ctx):
  


@client.command(brief="Set the text channel where welcome messages are sent")
async def welcomehere(ctx):
  if ctx.message.author.guild_permissions.administrator:
    #open messages text file to set line 0 to new channel id
    #insert channel id into json
    with open("welcome.json", "r") as file:
      try:
        welcome = json.load(file)
      except:
        welcome = dict()
    #set channel id of server
    welcome[str(ctx.guild.id)] = [str(ctx.channel.id)]
    
    with open("welcome.json", "w") as file:
      json.dump(welcome, file)
  else:
    try:
      await ctx.message.delete()
    except:
      print("Not enough permissions to delete messages")
    await ctx.author.send("You don't have enough permissions to do that.")


@client.command(brief="Add a welcome message to the server", description = "Multiple word messages and links are supported.")
async def addwelcome(ctx, *, message):
  if ctx.message.author.guild_permissions.administrator:
    with open("welcome.json", "r") as file:
        try:
          welcome = json.load(file)
        except:
          welcome = dict()
    
    guild_id = str(ctx.guild.id)
    if guild_id not in welcome:
      await ctx.send("**You must first set the text channel for welcome messages with '%welcomehere'**")
    else:
      await ctx.send("**Welcome message added!**")
      welcome[guild_id].append(message)

    with open("welcome.json", "w") as file:
      json.dump(welcome, file)
  else:
    try:
      await ctx.message.delete()
    except:
      print("Not enough permissions to delete messages")
    await ctx.author.send("You don't have enough permissions to do that.")


@client.command(brief="Delete welcome message from server (see %welcomemessages)")
async def delwelcome(ctx, number : int):
  if ctx.message.author.guild_permissions.administrator:
    if number <= 0:
      await ctx.send(f"**Message {number} does not exist**")
      return
    with open("welcome.json", "r") as file:
        try:
          welcome = json.load(file)
        except:
          welcome = dict()
    
    guild_id = str(ctx.guild.id)

    # check if server has welcome messages set up
    if guild_id not in welcome:
      await ctx.send("**There are no welcome messages for this server**")
    else:
      try:
        welcome[guild_id].pop(number)
        # deletes server from json if there are no messages
        if len(welcome[guild_id]) == 1:
          welcome.pop(guild_id)
      except:
        await ctx.send(f"**Message {number} does not exist**")
        return

    with open("welcome.json", "w") as file:
      json.dump(welcome, file)
  else:
    # user doesn't have enough permissions
    try:
      await ctx.message.delete()
    except:
      print("Not enough permissions to delete messages")
    await ctx.author.send("You don't have enough permissions to do that.")


@client.command(brief="Send all welcome messages for this server to user")
async def welcomemessages(ctx):
  if ctx.message.author.guild_permissions.administrator:
    with open("welcome.json", "r") as file:
        try:
          welcome = json.load(file)
        except:
          welcome = dict()
    
    guild_id = str(ctx.guild.id)

    # check if server has welcome messages set up
    if guild_id not in welcome:
      await ctx.send("**There are no welcome messages for this server**")
    else:
      outgoing = f"**\nWelcome messages for {ctx.guild.name}:**\n"
      for message in range(1, len(welcome[guild_id])):
        outgoing += "(" + str(message) + ") " + welcome[guild_id][message] + '\n'
      outgoing += "\n*You can reference the numbers to the left of the message to remove them using %delwelcome 'number here'*"
      await ctx.author.send(outgoing)
  else:
    try:
      await ctx.message.delete()
    except:
      print("Not enough permissions to delete messages")
    await ctx.author.send("You don't have enough permissions to do that.")


@client.event
async def on_member_join(member):
  guild_id = member.guild.id
  with open("welcome.json", "r") as file:
    try:
      welcome = json.load(file)
    except:
      print("No welcome messages.")
  
  if str(guild_id) in welcome:
    # send message
    messages = welcome[str(guild_id)]
    channel = client.get_channel(int(welcome[str(guild_id)][0]))
    try:
      await channel.send(messages[random.randrange(1, len(messages))])
    except:
      print("No server messages")


@client.command(brief="Makes bot join voice")
async def join(ctx):
  user = ctx.message.author
  voice_channel = user.voice.channel
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if voice == None: #if bot not in channel or not in author channel
    await voice_channel.connect()
  else:
    if ctx.voice_client.channel != ctx.author.voice.channel:
      await ctx.voice_client.disconnect()
      await voice_channel.connect()
    else:
      await ctx.send("**Already in current channel.**")


@client.command(brief="Makes bot leave voice")
async def leave(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice != None:
    await ctx.voice_client.disconnect()
  else:
    await ctx.send("**I am not in a channel.**")


@client.command(brief="Play audio from inputted link to youtube video")
async def play(ctx, url : str):
  song_there = os.path.isfile("song.webm")
  try:
    if song_there:
      os.remove("song.webm")
  except PermissionError:
    await ctx.send("Wait for the current playing music to end or use the 'stop' command")
    return

  #join command with no sends
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  voice_channel = ctx.message.author.voice.channel
  if voice == None: #if bot not in channel or not in author channel
    await voice_channel.connect()
  else:
    if ctx.voice_client.channel != ctx.author.voice.channel:
      await ctx.voice_client.disconnect()
      await voice_channel.connect()
  
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  ydl_opts = {
    'format': '251',
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
  for file in os.listdir("./"):
    if file.endswith(".webm"):
      os.rename(file, "song.webm")
  voice.play(discord.FFmpegOpusAudio("song.webm"))


@client.command(brief="Pause audio")
async def pause(ctx):
  voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
  if voice.is_playing:
    voice.pause()
  else:
    await ctx.send("**No audio playing.**")


@client.command(brief="Resume audio")
async def resume(ctx):
  voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
  if voice.is_paused:
    voice.resume()
  else:
    await ctx.send("**Audio is already playing.**")


@client.command(brief="Retrieve weather for an inputted city")
async def weather(ctx, city):
    #request
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&units=imperial&appid=4c0715acb4fc81b82bace4942a843378&lang=en")
    #status check and output
    if (response.status_code == 200):
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
    else:
      #if something goes wrong finding the city through the api
      print("Couldnt find " + city)
      await ctx.send("Couldn't find " + city + ".")


@client.command(brief="What will the 8 ball say?")
async def ball(ctx):
  #request
  response = requests.get("https://8ball.delegator.com/magic/JSON/randomstuff")
  json_data = json.loads(response.text)
  #use key to answer
  answer = str(json_data["magic"]["answer"])
  await ctx.send(answer)


@client.command()
async def hello(ctx):
  await ctx.send('oi punk :snake:')


@client.command(brief="Flip a coin")
async def flip(ctx):
  side = random.randint(1, 2)
  if (side == 1):
    await ctx.send("**Heads**")
  else:
    await ctx.send("**Tails**")


@client.command(brief="Create a customizable 'looking for group' message", description="Create a customizable 'looking for group' message. First type '%lfg' followed by the number of people needed, the event name of the lfg, the number of hours you want the lfg to last, and true/false if the lfg is scheduled or not. Scheduled means that at the end of the inputted time, the message will send. If it isn't scheduled, the notification message will send immediately when the goal is met. The number of hours and scheduled are set to 12 and false respectively by default, so these are not necessary to create an lfg message.")
async def lfg(ctx, goal : str, game : str, numHours : float=12, scheduled: bool=False):
  if numHours <= 200.00 and numHours > 0.00 and int(goal) > 1:
    denver = pytz.timezone('America/Denver')
    denver_time = datetime.now(denver)
    goalTime = denver_time + timedelta(hours=float(numHours))
    goalString = str(goalTime)
    # write formatted goal to file
    formattedGoal = goalString[0:19]
    #embed
    embed = discord.Embed(title=("LFG for " + game), description="People playing: 1", color=discord.Color.blue())
    embed.add_field(name="Players:", value=ctx.message.author.mention, inline=True)
    embed.add_field(name="Goal Time:", value=formattedGoal, inline=False)
    message = await ctx.send("**React to this message if you want to play " + game + ". We need " + goal + " people. React with ✅ to join and 🚫 to leave.**")
    in_embed = await ctx.send(embed=embed)
    messageid = message.id
    channel_id = message.channel.id
    embed_id = in_embed.id
    guild_id = ctx.guild.id
    guild_name = ctx.guild
    await message.add_reaction("✅")
    await message.add_reaction("🚫")
    #store lfg message information in dict then json
    lfg_dict = {
      'message_id':str(messageid),
      'channel_id':str(channel_id),
      'embed_id':str(embed_id),
      'lfg_name':str(game),
      'goal':str(goal),
      'guild_id':str(guild_id),
      'guild_name':str(guild_name),
      'goal_time':str(formattedGoal),
      'members':[str(ctx.message.author.id)],
      'scheduled':str(scheduled)
    }
    # extract lfg json
    with open("lfg.json", "r") as file:
      try:
        all_lfg = json.load(file)
      except:
        all_lfg = dict()
    # update lfg json

    all_lfg[str(messageid)] = lfg_dict

    # write to json file
    with open("lfg.json", "w") as file:
      json.dump(all_lfg, file)
    print("Created counter for " + game + " in " + message.guild.name)
  else:
    if int(goal) < 2:
      await ctx.author.send("You can only create an lfg with a goal of 2 or greater.")
    else:
      await ctx.author.send("You can only set an lfg timer for >0 to 200 hours")
  try:
    await ctx.message.delete()
  except:
    print("Not enough permissions to delete lfg call.")


#reaction checker
@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot == False:
    with open("lfg.json", "r") as file:
      all_lfg = json.load(file)
    if str(payload.message_id) in all_lfg:
      # retrieve lfg info
      message_id = str(payload.message_id)
      embed_id = int(all_lfg[message_id]['embed_id'])
      lfg_name = all_lfg[message_id]['lfg_name']
      goal = int(all_lfg[message_id]['goal'])
      guild_name = all_lfg[message_id]['guild_name']
      goal_time = str(all_lfg[message_id]['goal_time'])
      members_list = all_lfg[message_id]['members']
      scheduled = bool(all_lfg[message_id]['scheduled'])
      members = []
      # retrieve member objects from member ids
      for player_id in members_list:
        member_obj = await client.fetch_user(int(player_id))
        members.append(member_obj)
      count = len(members_list)
      member = payload.member
      # fetch lfg objects
      channel = client.get_channel(payload.channel_id)
      msg = await channel.fetch_message(int(message_id))
      in_embed = await channel.fetch_message(embed_id)
      send_out = ""
      
      if str(payload.emoji.name) == "✅" and count < goal:
        if member not in members:
          all_lfg[message_id]['members'].append(str(member.id))
          members.append(member)
          count += 1
          for person in members:
            send_out += (person.mention + "\n")
          des = str("People playing: " + str(count))
          new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.blue())
          new_info.add_field(name="Players:", value=send_out, inline=True)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
          await in_embed.edit(embed=new_info)

          #met goal
          if (count == goal):
            print(f"Goal has been reached for {goal} in {guild_name}.")
            if not scheduled:          
              for person in members:
                await person.send(f"Your group for {lfg_name} in {guild_name} is ready!")
              all_lfg.pop(message_id)
              print("Removed lfg from database.")
          #not met goal
          else:
            print("Detected reaction from " + str(payload.member) + ". There are is now ", count, " out of ", goal, " people ready to play " + lfg_name + ".")
          
          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        else:
          print(payload.member.name + " already in queue.")
        await msg.remove_reaction("✅", payload.member)

        #remove from lfg
      elif str(payload.emoji.name) == "🚫":
        if member in members:
          count -= 1
          members.remove(member)
          all_lfg[message_id]['members'].remove(str(member.id))
          print(str(payload.member) + " has left the lfg")
          des = str("People playing: " + str(count))
          if members == []:
            send_out = "N/A"
          else:
            for person in members:
              send_out += (person.mention + "\n")
          #embed
          new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.blue())
          new_info.add_field(name="Players:", value=send_out, inline=True)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
          await in_embed.edit(embed=new_info)

          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        await msg.remove_reaction("🚫", payload.member)


@client.command(brief="Retrieves runes for a LoL champ")
async def runes(ctx, champion : str, role : str):
  if role == "mid": role = "middle"
  elif role == "jg": role = "jungle"
  elif role == "sup": role = "support"
  elif role == "ad": role = "adc"
  print(f"Searching u.gg for {champion} in {role}...")
  URL = "https://u.gg/lol/champions/" + champion + "/build?role=" + role + "&rank=overall"
  valid=validators.url(URL)
  if valid:
    await ctx.send("https://u.gg/lol/champions/" + champion + "/build?role=" + role + "&rank=overall")
  else:
    await ctx.send("**You did something wrong**")


async def check():
  denver = pytz.timezone('America/Denver')
  denver_time = datetime.now(denver)
  formatted_denver = denver_time.strptime(str(denver_time)[0:19], "%Y-%m-%d %H:%M:%S")
  with open("lfg.json", "r") as file:
    try:
      all_lfg = json.load(file)
    except:
      await asyncio.sleep(60)
      await check()
  to_delete = []
  #update balances for every player
  new_day = all_lfg["time"]
  extracted_new_day = datetime.strptime(new_day, "%Y-%m-%d %H:%M:%S")
  if (formatted_denver >= extracted_new_day):
    with open("bank.json", "r") as file:
      try:
        bank = json.load(file)
      except:
        print("No players stored in bank")
        bank = dict()
    
    new_players = []
    # adds members who are not in bank to bank
    for guild in client.guilds:
      for member in guild.members:
        if member not in bank:
          bank[str(member.id)] = ["100"]
          new_players.append(member.id)
        elif member not in new_players:
          #add money to existing players
          money = int(bank[str(member.id)][0])
          money += 50
          bank[str(member.id)][0] = str(money)
    
    all_lfg["time"] = str(extracted_new_day + timedelta(hours=24))

    with open("all_lfg.json", "w") as file:
      json.dump(all_lfg, file)

    with open("bank.json", "w") as file:
      json.dump(bank, file)


  # check all times in lfg json
  for file in all_lfg:
    if file == "time":
      continue
    curr_time = all_lfg[file]['goal_time']
    extracted_new = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
    if (formatted_denver >= extracted_new):  # goal time is passed
      print("Deleting file " + file.rstrip('\n')  + " due to time passing")
      # retrieve lfg information
      lfg_name = all_lfg[file]['lfg_name']
      goal = int(all_lfg[file]['goal'])
      channel = client.get_channel(int(all_lfg[file]['channel_id']))
      in_embed = await channel.fetch_message(int(all_lfg[file]['embed_id']))
      members = all_lfg[file]['members']
      scheduled = bool(all_lfg[file]['scheduled'])
      guild = all_lfg[file]['guild_name']
      count = len(members)
      names = []
      send_out = ""
      # create message send out
      for player_id in members:
        member_obj = await client.fetch_user(int(player_id))
        if scheduled and count == goal:
          await member_obj.send(f"**Your scheduled event for {lfg_name} in {guild} is ready to start!**")
        elif scheduled and count != goal:
          await member_obj.send(f"**Your scheduled event for {lfg_name} in the '{guild}' server has failed to meet its goal, but you only need {goal - count} more!**")
        names.append(member_obj)
      if names == []:
        send_out = "N/A"
      else:
        for member in names:
          send_out += (member.mention + "\n")
      # update embed
      des = str("People playing: " + str(count))
      new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.red())
      new_info.add_field(name="Players:", value=send_out, inline=True)
      new_info.add_field(name="Goal Time:", value="Times up!", inline=False)
      await in_embed.edit(embed=new_info)
      # queue file for deletion
      to_delete.append(file)
  for file in to_delete:
    all_lfg.pop(file)
  with open("lfg.json", "w") as file:
    json.dump(all_lfg, file)
  await asyncio.sleep(60)
  await check()
"""
async def currency_update():
  #for guild in client.guilds:
  #  for member in guild.members:
  #    print(member)
  await asyncio.sleep(3600)
  await currency_update()
"""
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
