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

streams = os.getenv('streams')
intents = discord.Intents()
intents.members = True
random.seed()
client = commands.Bot(command_prefix="%", intents = intents)


@client.event
async def on_ready():
  print("Bot is up and running")
  await check()

@client.command()
async def welcomehere(ctx):
  print(ctx.author)
  if str(ctx.author) == "Sanic#8139":
    #open messages text file to set line 0 to new channel id
    print("Changed welcome channel to " + ctx.channel)
    file = open("welcome_messages.txt", "r+")
    list_of_lines = file.readlines()
    list_of_lines[0] = str(ctx.channel.id) + '\n'
    file.close()
    file = open("welcome_messages.txt", "w")
    file.writelines(list_of_lines)
    file.close()
    print()
  else:
    await ctx.author.send("Only Kyle can do that!")

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
  await client.get_channel(channel_id).send(messages[random.randrange(1, len(messages) - 1)])
  print(f"{member.name} has joined the server")
  #assign role to new member
  #role = discord.utils.get(member.guild.roles, id=771767637432336434)
  #await client.add_roles(member, role)

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
    print("Retrieving...")
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&units=imperial&appid=4c0715acb4fc81b82bace4942a843378&lang=en")
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
      print("Something went wrong retrieving data from weather api for " + city + ".")
      await ctx.send("Couldn't find " + city + ".")


@client.command(brief="What will the 8 ball say?")
async def ball(ctx):
  #request
  print("Retrieving...")
  response = requests.get("https://8ball.delegator.com/magic/JSON/randomstuff")
  print(response.content)
  json_data = json.loads(response.text)
  #use key to answer
  answer = str(json_data["magic"]["answer"])
  await ctx.send(answer)


@client.command()
async def hello(ctx):
  await ctx.send('oi punk :snake:')

@client.command(brief="Flip a coin")
async def flip(ctx):
  print("Coin flipping...")
  side = random.randint(1, 2)
  if (side == 1):
    await ctx.send("**Heads**")
    print("Heads!")
  else:
    await ctx.send("**Tails**")
    print("Tails!")

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
  await ctx.send("https://u.gg/lol/champions/" + champion + "/build?role=" + role + "&rank=overall")


async def check():
  denver = pytz.timezone('America/Denver')
  denver_time = datetime.now(denver)
  formattedDenver = denver_time.strptime(str(denver_time)[0:19], "%Y-%m-%d %H:%M:%S")
  with open("lfg.json", "r") as file:
    try:
      all_lfg = json.load(file)
    except:
      await asyncio.sleep(60)
      await check()
  # check all times in lfg json
  to_delete = []
  for file in all_lfg:
    curr_time = all_lfg[file]['goal_time']
    extractedNew = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
    if (formattedDenver >= extractedNew):  # goal time is passed
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
