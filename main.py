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
#import youtube_dl
import validators
from riotwatcher import LolWatcher, ApiError
import cassiopeia as lol
import string
from discord_components import *

streams = os.getenv('streams')
random.seed()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="%", case_insensitive = True, intents = intents)
client.remove_command("help")
riot_key = os.getenv('riot_key')
lol.set_riot_api_key(riot_key)
lol.set_default_region("NA")
lol_watcher = LolWatcher(riot_key)
twitch_client = os.getenv('twitch_client')
twitch_oauth = os.getenv('twitch_oauth')
TWITCH_API_ENDPOINT = 'https://api.twitch.tv/helix/streams?user_login={}'
TWITCH_HEADERS = {
    'Client-Id': twitch_client,
    'Authorization': 'Bearer ' + twitch_oauth,
    'Accept': 'application/vnd.twitchtv.v5+json',
}
disabled_buttons = [
  [
    Button(style=3, label="Join", disabled=True),
    Button(style=4, label="Leave", disabled=True),
  ]
]

@client.event
async def on_ready():
  DiscordComponents(client)
  print("Bot is up and running")
  print(f"Smoothie Bot is currently in {len(client.guilds)} servers!")
  asyncio.create_task(buttoner())
  asyncio.create_task(check())

@client.group(invoke_without_command=True)
async def help(ctx):
  e = discord.Embed(title="Help", description="Use %help <command> for extended\n information on a command", color=ctx.author.color)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)

  e.add_field(name="**Commands:**", value="`•lfg\n •stream\n •welcome\n •weather\n •flip\n •ball\n •lolstat\n •runes\n •hello \n`")
  e.add_field(name="**Links:**", value="[Add Smoothie](https://discord.com/api/oauth2/authorize?client_id=810761971979911188&permissions=1073899584&scope=bot)\n [Vote for Smoothie](https://top.gg/bot/810761971979911188/vote)", inline=False)
  e.set_footer(text="Created by Sanic#8139")
  await ctx.send(embed=e)
  await log(f"{ctx.message.author} requested help information in {ctx.guild.name}")

@help.command()
async def lfg(ctx):
  e = discord.Embed(title="LFG Help", description="**Description:**\nCreate a customizable \"looking for group\" message. First type \"%lfg\" followed by the event name of the lfg, the number of people needed, the number of hours you want the lfg to last (decimals supported), and true/false if the lfg is scheduled or not. Scheduled means that at the end of the inputted time, the players will be notified the lfg is ready. If it isn't scheduled, the notification message will send immediately when the goal is met. The timer is set to 30 minutes and scheduled are set to false by default, so these are not necessary to create an lfg message.", color=ctx.author.color)
  e.set_thumbnail(url="https://lfgroup.gg/wp-content/uploads/2020/05/lfg-banner-transparent.png")
  e.add_field(name="**Syntax**", value="`%lfg <name> <goal> <hours> <scheduled(true/false)>`\n *The hoursand scheduled fields are optional*")
  await ctx.send(embed=e)

@help.command()
async def stream(ctx):
  e = discord.Embed(title="**Stream Help**", description="The stream command uses different actions to function\n\n**Actions:**", color=ctx.author.color)
  e.add_field(name="Channel", value="Sets the text channel where stream notifications will be sent to. You must type this in the desired text channel.", inline=False)
  e.add_field(name="Add", value="Add a Twitch streamer to your server's notifications. You must type their username exactly. You can find this in the url of their stream.", inline=False)
  e.add_field(name="Del", value="Deletes a streamer from your server's notifications.", inline=False)
  e.add_field(name="Display", value="Displays all streamers with notifications for your server.", inline=False)
  e.set_thumbnail(url="https://lfgroup.gg/wp-content/uploads/2020/05/lfg-banner-transparent.png")
  e.add_field(name="**Syntax**", value="`%stream <action> <username>`\n *The channel and display actions do not require the username field*", inline=False)
  await ctx.send(embed=e)

@help.command()
async def welcome(ctx):
  e = discord.Embed(title="**Welcome Help**", description="The welcome command uses different actions to function\n\n**Actions:**",color=ctx.author.color)
  e.add_field(name="Channel", value="Set the channel where welcome messages are sent to. You must type this in the desired text channel.", inline=False)
  e.add_field(name="Add", value="Add a welcome message to your server. Multiple word messages and links are supported. Using an \"=\" symbol in the message will @ the person who joined. Having multiple welcome messages will make it so a random welcome message is sent when a member joins your server.", inline=False)
  e.add_field(name="Del", value="Uses indexes from the display action to delete different messages. To be clear, use the display action to determine which index each welcome message is assigned to. You may have to use the display function again as index will be reassigned after deleting a message.", inline=False)
  e.add_field(name="Display", value="Displays a numbered list of all welcome messages for your server.", inline=False)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)
  e.add_field(name="**Syntax**", value="`%welcome <action> <message/index>`\n *The message and index fields are only required for the add/del actions*", inline=False)
  await ctx.send(embed=e)

@help.command()
async def weather(ctx):
  e = discord.Embed(title="**Weather Help**", description="The weather command retrieves weather information for an inputted city.",color=ctx.author.color)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)
  e.add_field(name="**Syntax**", value="`%weather <city>`", inline=False)
  await ctx.send(embed=e)

@help.command()
async def flip(ctx):
  e = discord.Embed(title="**Flip Help**", description="The flip command will flip a coin. The command will output Heads or Tails.",color=ctx.author.color)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)
  e.add_field(name="**Syntax**", value="`%flip`", inline=False)
  await ctx.send(embed=e)

@help.command()
async def lolstat(ctx):
  e = discord.Embed(title="**LoLStat Help**", description="The lolstat command will get ranked solo/duo stats for a League of Legends player for the current season.",color=ctx.author.color)
  e.set_thumbnail(url="https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png")
  e.add_field(name="**Syntax**", value="`%lolstat <summoner>`", inline=False)
  await ctx.send(embed=e)

@help.command()
async def ball(ctx):
  e = discord.Embed(title="**Ball Help**", description="What will the 8 ball say? Acts as a normal 8 ball.",color=ctx.author.color)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)
  e.add_field(name="**Syntax**", value="`%ball`", inline=False)
  await ctx.send(embed=e)

@help.command()
async def runes(ctx):
  e = discord.Embed(title="**Runes Help**", description="The runes command will send a link to the runepage for a champion in a role for League of Legends. You don't need to include punction for void champions and can use simple role names like \"jg\" or \"sup\" for the role.",color=ctx.author.color)
  e.set_thumbnail(url="https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png")
  e.add_field(name="**Syntax**", value="`%runes <champion> <role>`", inline=False)
  await ctx.send(embed=e)

@help.command()
async def hello(ctx):
  e = discord.Embed(title="**Hello**", description="Hello",color=ctx.author.color)
  bot_pic_url = (await client.fetch_user("810761971979911188")).avatar_url
  e.set_thumbnail(url=bot_pic_url)
  e.add_field(name="**Hello**", value="`Hello`", inline=False)
  await ctx.send(embed=e)

async def log(text : str):
  with open('logs.txt', 'a') as file:
    file.write(text + '\n')
  print(text)


async def twitch_is_online(username):
  url = TWITCH_API_ENDPOINT.format(username)
  reqSession = requests.Session()
  req = reqSession.get(url, headers=TWITCH_HEADERS)
  json_data = req.json()
  return json_data['data']


@client.command()
async def status(ctx):
  if str(ctx.message.author) == "Sanic#8139":
    info = f"***{len(client.guilds)} servers***\n\n"
    sanic = await client.fetch_user("279056911926689793")
    for guild in client.guilds:
      info += f"**{guild.name}** ({guild.member_count} players)\n"
    await sanic.send(info)


@client.command()
@commands.guild_only()
async def stream(ctx, action : str="", username : str=""):
  if ctx.message.author.guild_permissions.administrator:
    if action == "":
      await ctx.send("You must use an action with the stream command. Use `%help stream` for more information.")
      return
    username = username.lower()
    with open("streams.json", "r") as streams_file:
      try:
        streams = json.load(streams_file)
      except:
        print('streams.json empty or cannot be loaded')
        streams = dict()
        streams['streamers_all'] = {}
    guild = str(ctx.guild.id)

    # set text channel where stream notifs are sent
    if action == 'channel':
      guild_info = {
        'channel': str(ctx.channel.id),
        'streamers': []
      }
      streams[guild] = guild_info
      await ctx.send(f"Stream notifications will be sent to **{ctx.channel.name}**")
    
    if guild not in streams:
      await ctx.send("You must set the text channel where notifications will be sent with \"%stream channel\" in the desired text channel.")
      return
    
    # add streamer to checker
    elif action == 'add':
      if username in streams[guild]['streamers']:
        await ctx.send("Streamer already added.")
      else:
        streams[guild]['streamers'].append(username)
        # update streamers_all in streams.json
        if username not in streams['streamers_all']:
          streamer_info = {
            'status': 'offline',
            'quantity': '1'
          }
          streams['streamers_all'][username] = streamer_info
        else:
          # adds quantity to streamers_all
          streams['streamers_all'][username]['quantity'] = str(int(streams['streamers_all'][username]['quantity']) + 1)
        await ctx.send(f"**{username}** added")
    
    # print all streamer names
    elif action == 'display':
      display_string = ""
      length = len(streams[guild]['streamers'])
      for count,name in enumerate(streams[guild]['streamers']):
        if count == 0:
          display_string += f"Streamer notifications are set up for "
        if count == length - 1:
          display_string += name + "."
        else:
          display_string += name + ", "
      await ctx.send(display_string)
    
    elif action == 'del':
      if username in streams[guild]['streamers']:
        streams[guild]['streamers'].remove(username)
        streams['streamers_all'][username]['quantity'] = str(int(streams['streamers_all'][username]['quantity']) - 1)
        # deletes streamer from streamers_all if no notifications are set up for them anymore
        if streams['streamers_all'][username]['quantity'] == '0':
          streams['streamers_all'].pop(username)
        await ctx.send(f"**{username}** has been removed")
      else:
        await ctx.send(f"**{username}** is not a streamer set up for this server")
    
    with open("streams.json", "w") as file:
      json.dump(streams, file)
  
  else:
    await ctx.send("**Only admins can use the \"%stream\" command**")


@client.command(brief="Get stats for a League of Legends player")
async def lolstat(ctx, *, summoner_name : str=""):
  if summoner_name == "":
    await ctx.send("You must include the summoner name in this command. For example, `%lolstat <summoner>`.")
    return
  # attempt to retrieve summoner from name
  try:
    summoner = lol_watcher.summoner.by_name('na1', summoner_name)
  except ApiError as err:
    if err.response.status_code == 429:
      print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
      print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
      print('Summoner with that ridiculous name not found.')
      await ctx.send("That summoner name doesn't exist")
    else:
      raise
    return
  # check if summoner plays ranked solo
  stats = lol_watcher.league.by_summoner('na1', summoner['id'])
  #matchlist = lol_watcher.match_v5.matchlist_by_puuid('AMERICAS', summoner['puuid'])
  #match = lol_watcher.match_v5.by_id('AMERICAS', matchlist[0])
  #player = lol_watcher.summoner.by_puuid('na1', player_id)['name']
  try:
    curr_match = lol_watcher.spectator.by_summoner('na1', summoner['id'])
    player_list = []
    for player_id in curr_match['participants']:
      player_list.append(player_id['summonerName'])
    length = float(curr_match['gameLength'])/60.00
    #print(curr_match)
    print(f"{length} minutes")
    print(player_list)
  except:
    pass
  ranked_solo = False
  if stats != []:
    for index, mode in enumerate(stats):
      if mode['queueType'] == 'RANKED_SOLO_5x5':
        ranked_solo = True
        mode_index = index
        break
  # display stats from ranked solo
  if ranked_solo:
    solo = stats[mode_index]
    total_games = float(solo['wins']) + float(solo['losses'])
    winrate = round(((float(solo['wins']) / total_games) * 100),2)
    name = solo['summonerName']
    rank = solo['tier'].title() + " " + solo['rank']
    await ctx.send(f"{name} is ranked {rank} with a {winrate}% winrate in Solo/Duo")
    await log(f"{name} is ranked {rank} with a {winrate}% winrate in Solo/Duo")
  else: await ctx.send("This summoner doesn't play Ranked Solo/Duo.")


async def get_thumbnail(title : str):
  title = title.lower()
  urls = {
    "valorant": "https://scontent.fapa1-2.fna.fbcdn.net/v/t1.6435-9/116792312_352845929450554_3400059762308528682_n.jpg?_nc_cat=1&ccb=1-4&_nc_sid=973b4a&_nc_ohc=2fZ6SRkas4QAX_um2IZ&_nc_ht=scontent.fapa1-2.fna&oh=a3f8f42a975dbc4e0447e6f121b8e1c5&oe=613A4BE6",
    "val":"https://scontent.fapa1-2.fna.fbcdn.net/v/t1.6435-9/116792312_352845929450554_3400059762308528682_n.jpg?_nc_cat=1&ccb=1-4&_nc_sid=973b4a&_nc_ohc=2fZ6SRkas4QAX_um2IZ&_nc_ht=scontent.fapa1-2.fna&oh=a3f8f42a975dbc4e0447e6f121b8e1c5&oe=613A4BE6",
    "valo":"https://scontent.fapa1-2.fna.fbcdn.net/v/t1.6435-9/116792312_352845929450554_3400059762308528682_n.jpg?_nc_cat=1&ccb=1-4&_nc_sid=973b4a&_nc_ohc=2fZ6SRkas4QAX_um2IZ&_nc_ht=scontent.fapa1-2.fna&oh=a3f8f42a975dbc4e0447e6f121b8e1c5&oe=613A4BE6",
    "ape leg":"https://emoji.gg/assets/emoji/1650_apex_legends.png",
    "ape":"https://emoji.gg/assets/emoji/1650_apex_legends.png",
    "apex":"https://emoji.gg/assets/emoji/1650_apex_legends.png",
    "apex legends":"https://emoji.gg/assets/emoji/1650_apex_legends.png",
    "league":"https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png",
    "leg":"https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png",
    "league of leg":"https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png",
    "5v5":"https://styles.redditmedia.com/t5_2rfxx/styles/communityIcon_9yj66cjf8oq61.png",
    "rl":"https://logos-world.net/wp-content/uploads/2020/11/Rocket-League-Emblem.png",
    "rocket":"https://logos-world.net/wp-content/uploads/2020/11/Rocket-League-Emblem.png",
    "rocket league":"https://logos-world.net/wp-content/uploads/2020/11/Rocket-League-Emblem.png",
    "split":"https://lookingforclan.com/sites/default/files/styles/icon/public/2021-07/splitgate-logo.png.jpg?itok=Bp6Ul-Q3",
    "splitgate":"https://lookingforclan.com/sites/default/files/styles/icon/public/2021-07/splitgate-logo.png.jpg?itok=Bp6Ul-Q3",
    "split gate":"https://lookingforclan.com/sites/default/files/styles/icon/public/2021-07/splitgate-logo.png.jpg?itok=Bp6Ul-Q3"
  }
  if title in urls: return urls[title]
  else: return "https://lfgroup.gg/wp-content/uploads/2020/05/lfg-banner-transparent.png"


@client.command()
@commands.guild_only()
async def welcome(ctx, *, action):
  if ctx.message.author.guild_permissions.administrator:
    if action == "":
      await ctx.send("You must use an action with the welcome command. Use `%help welcome` for more information.")
    action = action.split()
    with open("welcome.json", "r") as file:
      try:
        welcome = json.load(file)
      except:
        welcome = dict()

    if action[0] == 'channel':
      #open messages text file to set line 0 to new channel id
      #insert channel id into json
      #set channel id of server
      if str(ctx.guild.id) not in welcome:
        await ctx.send(f"**Welcome channel set to {ctx.channel.name}**")
        welcome[str(ctx.guild.id)] = [str(ctx.channel.id)]
      else:
        await ctx.send(f"**{ctx.channel.name} is already the welcome channel**")
      
      with open("welcome.json", "w") as file:
        json.dump(welcome, file)

    if action[0] == 'add':
      guild_id = str(ctx.guild.id)
      if guild_id not in welcome:
        await ctx.send("**You must first set the text channel for welcome messages with \"%welcome channel\"**")
      else:
        await ctx.send("**Welcome message added!**")
        message = ""
        for index,word in enumerate(action):
          if index != 0:
            message += word
        welcome[guild_id].append(message)

      with open("welcome.json", "w") as file:
        json.dump(welcome, file)

    if action[0] == 'del':
      try:
        number = int(action[1])
      except:
        await ctx.send("Invalid number")
      if number <= 0:
        await ctx.send(f"**Message {number} does not exist**")
        return
      
      guild_id = str(ctx.guild.id)

      # check if server has welcome messages set up
      if guild_id not in welcome:
        await ctx.send("**There are no welcome messages for this server**")
      else:
        try:
          welcome[guild_id].pop(number)
          with open("welcome.json", "w") as file:
            json.dump(welcome, file)
          await ctx.send(f"**Message {number} deleted**")
        except:
          await ctx.send(f"**Message {number} does not exist**")
          return
          
    if action[0] == 'display':
      guild_id = str(ctx.guild.id)

      # check if server has welcome messages set up
      if guild_id not in welcome:
        await ctx.send("**There are no welcome messages for this server**")
      else:
        outgoing = f"**\nWelcome messages for {ctx.guild.name}:**\n"
        for message in range(1, len(welcome[guild_id])):
          outgoing += "(" + str(message) + ") " + welcome[guild_id][message] + '\n'
        outgoing += "\n*You can reference the indexes to the left of the message to remove them using %welcome del <index>*"
        await ctx.send(outgoing)
  else:
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
      message = messages[random.randrange(1, len(messages))]
      message = message.replace('=', member.mention)
      await channel.send(message)
      await log(f"Welcome message \"{message}\" sent to {member.guild.name}")
    except:
      print("No server messages")

"""
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
"""

@client.command(brief="Retrieve weather for an inputted city")
async def weather(ctx, *, city : str=""):
  if city == "":
    await ctx.send("You must input a city to use the weather command. For example, `%weather <city>`.")
    return
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
    weather_low = str(json_data["main"]["temp_min"])
    weather_high = str(json_data["main"]["temp_max"])
    weather_wind = str(json_data["wind"]["speed"])
    city = weather_city
    response.status_code = 0
    #makes embed in discord server
    embed = discord.Embed(title="Weather",
    description="Weather in " + city + ", " +
    weather_country,
    color=discord.Color.teal())
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
    embed.add_field(name="High:",
    value=weather_high + "ºF",
    inline=True)
    embed.add_field(name="Low:",
    value=weather_low + "ºF",
    inline=True)
    embed.add_field(name="Wind Speed:",
    value=weather_wind + " mph",
    inline=True)
    await ctx.send(embed=embed)
    await log(f"Found weather for {city}")
    #await ctx.send("Feels like " + weather_feels_like + "ºF\nHumidity: " + weather_humidity + "%\nDescription: " + weather_clouds)
  else:
    #if something goes wrong finding the city through the api
    print("Couldn't find " + city)
    await ctx.send("Couldn't find " + city + ".")


@client.command(brief="What will the 8 ball say?")
async def ball(ctx):
  ball_messages = ["It is certain", "It id decidedly so", "Without a doubt", "Yes, definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good", "Signs point to yes", "Yarp", "Narp", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
  message = random.choice(ball_messages)
  await log(f"{ctx.message.author} shook the 8 ball")
  await ctx.send(f"*{message}*")


@client.command()
async def hello(ctx):
  await ctx.send('oi punk :snake:')
  await log(f"Said hi to {ctx.message.author}")


@client.command(brief="Flip a coin")
async def flip(ctx):
  await log(f"{ctx.message.author} flipped the coin")
  side = random.randint(1, 2)
  if (side == 1):
    await ctx.send("*Heads*")
  else:
    await ctx.send("*Tails*")


@client.command()
@commands.guild_only()
async def lfg(ctx, game : str="", goal : str='0', numHours : float=.5, scheduled: bool=False):
  if game == "":
    await ctx.send("You have no game inputted. Use the `%help lfg` command to learn how to create an lfg message.")
    return
  if numHours <= 200.00 and numHours > 0.00 and int(goal) > 1:
    # create buttons
    buttons = [
      [
        Button(style=3, label="Join"),
        Button(style=4, label="Leave"),
      ]
    ]
    #Button(label="Add Me", style=ButtonStyle.URL, url="https://discord.com/api/oauth2/authorize?client_id=810761971979911188&permissions=1073899584&scope=bot")
    # extract lfg json
    with open("lfg.json", "r") as file:
      try:
        all_lfg = json.load(file)
      except:
        all_lfg = dict()
    
    # check if user owns more than 1 lfg
    owner = str(ctx.message.author.id)
    for lfg in all_lfg:
      if lfg == 'time': continue
      if all_lfg[lfg]['owner'] == owner:
        await ctx.send("You can't own more than 1 lfg at a time.")
        return

    if len(game) == 22:
      try:
        role_id = game[3:21]
        print(role_id)
        role = ctx.guild.get_role(int(role_id))
        game = role.name
      except:
        print(role_id + " doesn't exist")
    # add scheduled information to game
    if scheduled: game = game + " (scheduled)"
    # get current time
    denver = pytz.timezone('America/Denver')
    denver_time = datetime.now(denver)
    goal_datetime = denver_time + timedelta(hours=float(numHours))
    time_left = str(goal_datetime-denver_time)[0:19]
    goal_time = str(goal_datetime.ctime())[0:len(goal_datetime.ctime()) - 8]
    length = len(goal_time)
    hour_int = int(goal_time[11:length - 3])
    if hour_int >= 12: cycle = " pm"
    else: cycle = " am"
    hour_int = hour_int % 12
    if hour_int == 0: hour_int = 12
    goal_time = goal_time.replace(goal_time[11:length - 3], str(hour_int), 1)
    goal_time += cycle
    # write formatted goal to file
    #embed
    embed = discord.Embed(title=(f"LFG: {int(goal) - 1} more needed for {game}"), description=f"People playing: 1/{goal}", color=discord.Color.dark_blue())
    embed.set_thumbnail(url=await get_thumbnail(game.replace(" (scheduled)", "")))
    #embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    embed.add_field(name="Players:", value=ctx.message.author.mention, inline=False)
    #embed.add_field(name = chr(173), value = chr(173), inline=False)
    embed.add_field(name="Ends In:", value="~" + time_left, inline=False)
    embed.add_field(name="Goal Time:", value=goal_time, inline=False)
    embed.set_footer(text="Click the buttons below to join or leave this lfg.")
    in_embed = await ctx.send(components=buttons, embed=embed)
    channel_id = ctx.message.channel.id
    embed_id = in_embed.id
    guild_id = ctx.guild.id
    guild_name = ctx.guild
    #store lfg message information in dict then json
    lfg_dict = {
      'channel_id':str(channel_id),
      'embed_id':str(embed_id),
      'lfg_name':str(game),
      'goal':str(goal),
      'owner':owner,
      'guild_id':str(guild_id),
      'guild_name':str(guild_name),
      'goal_time':goal_time,
      'goal_datetime':str(goal_datetime)[0:19],
      'time_left':"~" + time_left,
      'members':[owner],
      'scheduled':str(scheduled)
    }
    # update lfg json

    all_lfg[str(embed_id)] = lfg_dict

    # write to json file
    with open("lfg.json", "w") as file:
      json.dump(all_lfg, file)
    await log(f"{ctx.message.author} created an LFG for {game} in {ctx.message.guild.name} for {numHours} hours with a goal of {goal} people.")
  else:
    if int(goal) < 2:
      await ctx.send("You can only create an lfg with a goal of 2 or greater.")
    else:
      await ctx.send("You can only set an lfg timer for >0 to 200 hours")


async def buttoner():
  while True:
    res = await client.wait_for('button_click')
    if res.message.embeds != []:
      await res.respond(type=5) # thinking message
      message_id = str(res.message.id)
      with open("lfg.json", "r") as file:
        all_lfg = json.load(file)
      if message_id in all_lfg:
        embed_id = message_id
        # retrieve lfg info
        lfg_name = all_lfg[embed_id]['lfg_name']
        goal = int(all_lfg[embed_id]['goal'])
        guild_name = all_lfg[embed_id]['guild_name']
        goal_time = str(all_lfg[embed_id]['goal_time'])
        members_list = all_lfg[embed_id]['members']
        scheduled = True if all_lfg[embed_id]['scheduled'] == 'True' else False
        time_left = all_lfg[embed_id]['time_left']
        members = []
        # retrieve member objects from member ids
        for player_id in members_list:
          member_obj = await client.fetch_user(int(player_id))
          members.append(member_obj)
        count = len(members_list)
        member = res.author
        # fetch lfg objects
        channel = client.get_channel(res.channel_id)
        try:
          in_embed = await channel.fetch_message(int(embed_id))
        except:
          await log(f"Message for the {lfg_name} LFG in {guild_name} could not be found.")
          all_lfg.pop(embed_id)
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
          return
        send_out = ""
        if res.component.label == "Join" and count == goal:
          await res.respond(content=f"Sorry! The LFG for {lfg_name} is full.")
        elif res.component.label == "Join":
          if member not in members:
            all_lfg[embed_id]['members'].append(str(member.id))
            members.append(member)
            count += 1
            remaining = goal - count
            for person in members:
              send_out += (person.mention + "\n")
            des = f"People playing: {count}/{goal}"
            await res.respond(content=f"You have joined the LFG for **{lfg_name}**")
            await log(f"Detected reaction from {res.author}. There are is now {count} out of {goal} people ready to play {lfg_name}.")
            #met goal
            if (count == goal):
              new_info = discord.Embed(title=(f"LFG: {remaining} more needed for {lfg_name}"), description=des, color=discord.Color.green())
              new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
              new_info.add_field(name="Players:", value=send_out, inline=False)
              new_info.add_field(name="Ends In:", value=time_left, inline=False)
              new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
              new_info.set_footer(text="Goal met!")
              await in_embed.edit(components=disabled_buttons, embed=new_info)
              await log(f"Goal has been reached for {goal} in {guild_name}.")
              if not scheduled:          
                for person in members:
                  await person.send(f"Your group for {lfg_name} in {guild_name} is ready!\nPeople playing:\n{send_out}")
                all_lfg.pop(embed_id)
                await log(f"Removed {lfg_name} LFG in {guild_name} from database.")
            else:
              new_info = discord.Embed(title=(f"LFG: {remaining} more needed for {lfg_name}"), description=des, color=discord.Color.dark_blue())
              new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
              new_info.add_field(name="Players:", value=send_out, inline=False)
              new_info.add_field(name="Ends In:", value=time_left, inline=False)
              new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
              new_info.set_footer(text="LFG expired.")
              await in_embed.edit(embed=new_info)
            
            # dump new info into lfg json
            with open("lfg.json", "w") as file:
              json.dump(all_lfg, file)
          else:
            await log(f"{res.author.name} already in LFG.")
            await res.respond(content="You are already in the LFG.")

          #remove from lfg
        elif res.component.label == "Leave":
          if member in members:
            count -= 1
            remaining = goal - count
            members.remove(member)
            all_lfg[embed_id]['members'].remove(str(member.id))
            await log(f"{res.author} has left the LFG for {lfg_name}.")
            await res.respond(content=f"You have left the LFG for **{lfg_name}**")
            des = f"People playing: {count}/{goal}"
            if members == []:
              send_out = "N/A"
            else:
              for person in members:
                send_out += (person.mention + "\n")
            #embed
            new_info = discord.Embed(title=f"LFG: {remaining} more needed for {lfg_name}", description=des, color=discord.Color.dark_blue())
            new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
            new_info.add_field(name="Players:", value=send_out, inline=False)
            new_info.add_field(name="Ends In:", value=time_left, inline=False)
            new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
            new_info.set_footer(text="Click the buttons below to join or leave this LFG.")
            await in_embed.edit(embed=new_info)

            # dump new info into lfg json
            with open("lfg.json", "w") as file:
              json.dump(all_lfg, file)
          else:
            await log(f"{res.author.name} can't leave an LFG if already in LFG.")
            await res.respond(content="You can't leave an LFG if alredy in LFG.")

"""
@client.command(brief="Create a customizable \"looking for group\" message. Type \"%help lfg\"", description="Create a customizable \"looking for group\" message. First type \"%lfg\" followed by the event name of the lfg, the number of people needed, the number of hours you want the lfg to last, and true/false if the lfg is scheduled or not. Scheduled means that at the end of the inputted time, the players will be notified the lfg is ready. If it isn't scheduled, the notification message will send immediately when the goal is met. The timer is set to 30 minutes and scheduled are set to false by default, so these are not necessary to create an lfg message.")
async def lfg(ctx, game : str="", goal : str=0, numHours : float=.5, scheduled: bool=False):
  if game == "":
    await ctx.send("Use the \"%help lfg\" command to learn how to create an lfg message!")
    return
  if numHours <= 200.00 and numHours > 0.00 and int(goal) > 1:
    # extract lfg json
    with open("lfg.json", "r") as file:
      try:
        all_lfg = json.load(file)
      except:
        all_lfg = dict()
    
    # check if user owns more than 1 lfg
    owner = str(ctx.message.author.id)
    for lfg in all_lfg:
      if lfg == 'time': continue
      if all_lfg[lfg]['owner'] == owner:
        await ctx.send("You can't own more than 1 lfg at a time.")
        return

    if len(game) == 22:
      try:
        role_id = game[3:21]
        print(role_id)
        role = ctx.guild.get_role(int(role_id))
        game = role.name
      except:
        print(role_id + " doesn't exist")
    # add scheduled information to game
    if scheduled: game = game + " (scheduled)"
    # get current time
    denver = pytz.timezone('America/Denver')
    denver_time = datetime.now(denver)
    goal_datetime = denver_time + timedelta(hours=float(numHours))
    time_left = str(goal_datetime-denver_time)[0:19]
    goal_time = str(goal_datetime.ctime())[0:len(goal_datetime.ctime()) - 8]
    length = len(goal_time)
    hour_int = int(goal_time[11:length - 3])
    if hour_int >= 12: cycle = " pm"
    else: cycle = " am"
    hour_int = hour_int % 12
    if hour_int == 0: hour_int = 12
    goal_time = goal_time.replace(goal_time[11:length - 3], str(hour_int), 1)
    goal_time += cycle
    # write formatted goal to file
    #embed
    embed = discord.Embed(title=(f"LFG: {int(goal) - 1} more needed for {game}"), description=f"People playing: 1/{goal}", color=discord.Color.green())
    #embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    embed.set_thumbnail(url=await get_thumbnail(game.replace(" (scheduled)", "")))
    embed.add_field(name="Players:", value=ctx.message.author.mention, inline=False)
    #embed.add_field(name = chr(173), value = chr(173), inline=False)
    embed.add_field(name="Ends In:", value="~" + time_left, inline=False)
    embed.add_field(name="Goal Time:", value=goal_time, inline=False)
    embed.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
    in_embed = await ctx.send(embed=embed)
    channel_id = ctx.message.channel.id
    embed_id = in_embed.id
    guild_id = ctx.guild.id
    guild_name = ctx.guild
    await in_embed.add_reaction("✅")
    await in_embed.add_reaction("🚫")
    #store lfg message information in dict then json
    lfg_dict = {
      'channel_id':str(channel_id),
      'embed_id':str(embed_id),
      'lfg_name':str(game),
      'goal':str(goal),
      'owner':owner,
      'guild_id':str(guild_id),
      'guild_name':str(guild_name),
      'goal_time':goal_time,
      'goal_datetime':str(goal_datetime)[0:19],
      'time_left':"~" + time_left,
      'members':[owner],
      'scheduled':str(scheduled)
    }
    # update lfg json

    all_lfg[str(embed_id)] = lfg_dict

    # write to json file
    with open("lfg.json", "w") as file:
      json.dump(all_lfg, file)
    await log(f"{ctx.message.author} created an LFG for {game} in {ctx.message.guild.name} for {numHours} hours with a goal of {goal} people.")
  else:
    if int(goal) < 2:
      await ctx.send("You can only create an lfg with a goal of 2 or greater.")
    else:
      await ctx.send("You can only set an lfg timer for >0 to 200 hours")
  """
"""
  try:
    await ctx.message.delete()
  except:
    print("Not enough permissions to delete lfg call.")
  """

"""

#reaction checker
@client.event
async def on_raw_reaction_add(payload):
  if payload.member.bot == False:
    message_id = str(payload.message_id)
    with open("lfg.json", "r") as file:
      all_lfg = json.load(file)
    if message_id in all_lfg:
      embed_id = message_id
      # retrieve lfg info
      lfg_name = all_lfg[embed_id]['lfg_name']
      goal = int(all_lfg[embed_id]['goal'])
      guild_name = all_lfg[embed_id]['guild_name']
      goal_time = str(all_lfg[embed_id]['goal_time'])
      members_list = all_lfg[embed_id]['members']
      scheduled = True if all_lfg[embed_id]['scheduled'] == 'True' else False
      time_left = all_lfg[embed_id]['time_left']
      members = []
      # retrieve member objects from member ids
      for player_id in members_list:
        member_obj = await client.fetch_user(int(player_id))
        members.append(member_obj)
      count = len(members_list)
      member = payload.member
      # fetch lfg objects
      channel = client.get_channel(payload.channel_id)
      try:
        embed_obj = await channel.fetch_message(int(embed_id))
      except:
        print(f"Message for the {lfg_name} lfg in {guild_name} could not be found.")
        all_lfg.pop(embed_id)
        with open("lfg.json", "w") as file:
          json.dump(all_lfg, file)
        return
      in_embed = await channel.fetch_message(int(embed_id))
      send_out = ""
      
      if str(payload.emoji.name) == "✅" and count < goal:
        if member not in members:
          all_lfg[embed_id]['members'].append(str(member.id))
          members.append(member)
          count += 1
          remaining = goal - count
          for person in members:
            send_out += (person.mention + "\n")
          des = f"People playing: {count}/{goal}"
          new_info = discord.Embed(title=(f"LFG: {remaining} more needed for {lfg_name}"), description=des, color=discord.Color.green())
          new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
          new_info.add_field(name="Players:", value=send_out, inline=False)
          new_info.add_field(name="Ends In:", value=time_left, inline=False)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
          new_info.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
          await in_embed.edit(embed=new_info)
          await log(f"Detected reaction from {payload.member}. There are is now {count} out of {goal} people ready to play {lfg_name}.")
          #met goal
          if (count == goal):
            await log(f"Goal has been reached for {goal} in {guild_name}.")
            if not scheduled:          
              for person in members:
                await person.send(f"**Your group for {lfg_name} in {guild_name} is ready!\nPeople playing:\n{send_out}**")
              await in_embed.delete()
              all_lfg.pop(embed_id)
              await log(f"Removed {lfg_name} lfg in {guild_name} from database.")
          
          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        else:
          print(f"{payload.member.name} already in queue.")
        if count != goal:
          await embed_obj.remove_reaction("✅", payload.member)

        #remove from lfg
      elif str(payload.emoji.name) == "🚫":
        if member in members:
          count -= 1
          remaining = goal - count
          members.remove(member)
          all_lfg[embed_id]['members'].remove(str(member.id))
          await log(f"{payload.member} has left the lfg for {lfg_name}.")
          des = f"People playing: {count}/{goal}"
          if members == []:
            send_out = "N/A"
          else:
            for person in members:
              send_out += (person.mention + "\n")
          #embed
          new_info = discord.Embed(title=f"LFG: {remaining} more needed for {lfg_name}", description=des, color=discord.Color.green())
          new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
          new_info.add_field(name="Players:", value=send_out, inline=False)
          new_info.add_field(name="Ends In:", value=time_left, inline=False)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
          new_info.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
          await in_embed.edit(embed=new_info)

          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        await embed_obj.remove_reaction("🚫", payload.member)
"""

@client.command(brief="Retrieves runes for a LoL champ")
async def runes(ctx, champion : str="", role : str=""):
  if champion == "":
    await ctx.send("You must include a champion for the runes command. For example, `%runes <champion> <role>`.")
    return
  if role == "":
    await ctx.send("You must include a role for the runes command. For example, `%runes <champion> <role>`.")
    return
  if role == "mid": role = "middle"
  elif role == "jg": role = "jungle"
  elif role == "sup": role = "support"
  elif role == "ad": role = "adc"
  await log(f"Searching u.gg for {champion} in {role}...")
  URL = "https://u.gg/lol/champions/" + champion + "/build?role=" + role + "&rank=overall"
  valid=validators.url(URL)
  if valid:
    await ctx.send("https://u.gg/lol/champions/" + champion + "/build?role=" + role + "&rank=overall")
  else:
    await ctx.send("**You did something wrong**")


async def check():
  with open("streams.json", "r") as file:
    try:
      streams = json.load(file)
    except:
      print('streams.json empty or cannot be loaded')
      streams = dict()
  with open("welcome.json", "r") as file:
    try:
      welcome = json.load(file)
    except:
      print('welcome.json empty or cannot be loaded')
      welcome = dict()
  bot_guilds = []
  for guild in client.guilds:
    bot_guilds.append(str(guild.id))
  
  # time stuff for lfg
  denver = pytz.timezone('America/Denver')
  denver_time = datetime.now(denver)
  curr_time = str(denver_time.ctime())[0:len(denver_time.ctime()) - 8]
  length = len(curr_time)
  hour_int = int(curr_time[11:length - 3])
  if hour_int >= 12: cycle = " pm"
  else: cycle = " am"
  hour_int = hour_int % 12
  if hour_int == 0: hour_int = 12
  curr_time = curr_time.replace(curr_time[11:length - 3], str(hour_int), 1)
  curr_time += cycle


  # check each guild's stream info
  if streams != {}:
    # make new random query
    letters = string.ascii_letters
    letters = ''.join(random.choice(letters) for i in range(6))
    query = "?random=" + letters
    # check each streamer's status
    for streamer in streams['streamers_all']:
      streamer_info = await twitch_is_online(streamer)
      if streams['streamers_all'][streamer]['status'] == 'offline' and streamer_info != []:
        streams['streamers_all'][streamer]['status'] = 'online'
        # streamer has become online
        #create embed
        embed = discord.Embed(title=streamer_info[0]['title'], url=f"https://www.twitch.tv/{streamer}", color=discord.Color.dark_purple())
        embed.add_field(name="Playing:", value=f"{streamer_info[0]['game_name']}", inline=True)
        embed.add_field(name="Started at:", value=curr_time, inline=True)
        embed.set_author(name=streamer.title())
        pic = streamer_info[0]['thumbnail_url'].replace('{width}', '1600').replace('{height}', '900') + query
        print(f"{streamer} is now live!")
        embed.set_image(url=pic)
        embed.set_footer(text=f"Click the title to watch!")
        # send out stream update
        for guild in streams:
          if guild == 'streamers_all': continue
          if streams == 'streamers_all': continue
          # check each server info for streamer
          if streamer in streams[guild]['streamers']:
            try:
              channel = client.get_channel(int(streams[guild]['channel']))
            except:
              print(f"Channel cannot be found. Skipping {channel}...")
              continue
            await channel.send(f"@everyone **{streamer.title()} is now live!**", embed=embed)
      elif streams['streamers_all'][streamer]['status'] == 'online' and streamer_info == []:
        streams['streamers_all'][streamer]['status'] = 'offline'
        print(f"{streamer} is now offline")
  with open("streams.json", "w") as file:
    json.dump(streams, file)
          
  formatted_denver = denver_time.strptime(str(denver_time)[0:19], "%Y-%m-%d %H:%M:%S")
  with open("lfg.json", "r") as file:
    try:
      all_lfg = json.load(file)
    except:
      await asyncio.sleep(60)
      await check()
  to_delete = []

  # check all times in lfg json
  for file in all_lfg:
    if file == "time":
      continue
    goal_datetime = all_lfg[file]['goal_datetime']
    goal_time = all_lfg[file]['goal_time']
    extracted_new = datetime.strptime(goal_datetime, "%Y-%m-%d %H:%M:%S")
    time_left = "~" + str(extracted_new-formatted_denver)[0:19]
    members = all_lfg[file]['members']
    count = len(members)
    lfg_name = all_lfg[file]['lfg_name']
    goal = int(all_lfg[file]['goal'])
    remaining = goal - count
    names = []
    if (formatted_denver >= extracted_new):  # goal time is passed
      filename = file.rstrip('\n')
      print(f"Deleting file {filename} due to time passing")
      # retrieve lfg information
      try:
        channel = client.get_channel(int(all_lfg[file]['channel_id']))
        in_embed = await channel.fetch_message(int(all_lfg[file]['embed_id']))
      except:
        # catch
        to_delete.append(file)
        continue
      scheduled = True if all_lfg[file]['scheduled'] == 'True' else False
      guild = all_lfg[file]['guild_name']
      send_out = ""
      # create list of member objects
      for player_id in members:
        member_obj = await client.fetch_user(int(player_id))
        names.append(member_obj)
      # create send out message
      if names == []:
        send_out = "N/A"
      else:
        for member in names:
          send_out += (member.mention + "\n")
      # update embed
      des = str(f"People playing: {count}/{goal}")
      new_info = discord.Embed(title=f"LFG: {remaining} more needed for {lfg_name}", description=des, color=discord.Color.red())
      new_info.add_field(name="Players:", value=send_out, inline=False)
      new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
      # scheduled lfg
      if scheduled:
        new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
        if count == goal:
          for member_obj in names:
            await member_obj.send(f"**Your scheduled event for {lfg_name} in \"{guild}\" is ready to start!\nPlayers:**\n{send_out}")
          new_info.set_footer(text="Goal met!")
        else:
          for member_obj in names:
            await member_obj.send(f"**Your scheduled event for {lfg_name} in the \"{guild}\" server has failed to meet its goal, but you only need {goal - count} more!\nPlayers:**\n{send_out}")
          new_info.set_footer(text="LFG expired.")
        await in_embed.edit(components=disabled_buttons, embed=new_info)
      else:
        for member_obj in names:
          await member_obj.send(f"**Your LFG for {lfg_name} in the \"{guild}\" server has failed to meet its goal, but you only need {goal - count} more!\nPlayers:**\n{send_out}")
        new_info.set_thumbnail(url=await get_thumbnail(lfg_name))
        new_info.set_footer(text="LFG expired.")
        await in_embed.edit(components=disabled_buttons, embed=new_info)
      # queue file for deletion
      to_delete.append(file)
    # update time in lfg time left
    else:
      count = len(members)
      send_out = ""
      names = []
      channel = client.get_channel(int(all_lfg[file]['channel_id']))
      in_embed = await channel.fetch_message(int(all_lfg[file]['embed_id']))
      goal = all_lfg[file]['goal']
      for player_id in members:
        member_obj = await client.fetch_user(int(player_id))
        names.append(member_obj)
      if names == []:
        send_out = "N/A"
      else:
        for member in names:
          send_out += (member.mention + "\n")
      des = str(f"People playing: {count}/{goal}")
      new_info = discord.Embed(title=f"LFG: {remaining} more needed for {lfg_name}", description=des, color=discord.Color.dark_blue())
      new_info.set_thumbnail(url=await get_thumbnail(lfg_name.replace(" (scheduled)", "")))
      new_info.add_field(name="Players:", value=send_out, inline=False)
      new_info.add_field(name="Ends In:", value=time_left, inline=False)
      new_info.add_field(name="Goal Time:", value=goal_time, inline=False)
      new_info.set_footer(text="Click the buttons below to join or leave this lfg.")
      await in_embed.edit(embed=new_info)
      all_lfg[file]['time_left'] = str(time_left)

  for file in to_delete:
    all_lfg.pop(file)
  with open("lfg.json", "w") as file:
    json.dump(all_lfg, file)
  await asyncio.sleep(60)
  #await check()
  await asyncio.create_task(check())

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
