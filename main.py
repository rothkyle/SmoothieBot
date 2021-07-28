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
import math

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


async def in_bank(member):
  with open("bank.json", "r") as file:
    try:
      bank = json.load(file)
    except:
      print("There are no members in the bank")
  if member not in bank:
    return False
  return True


async def return_card(card):
  suit = math.floor(int(card) / 13)
  number = int(card) % 13
  suit_name = ""
  number_name = str(number)
  if suit == 0:
    suit_name = "Hearts"
  elif suit == 1:
    suit_name = "Spades"
  elif suit == 2:
    suit_name = "Clubs"
  elif suit == 3:
    suit_name = "Diamonds"
  
  if number == 1:
    number_name = "Ace"
  elif number == 11:
    number_name = "Jack"
  elif number == 12:
    number_name = "Queen"
  elif number == 13:
    number_name = "King"
  return number_name, suit_name


async def random_card(deck):
  deck_length = len(deck)
  index = random.randint(0,deck_length-1)
  return index


@client.command()
async def game(ctx, action : str, amount : int=0):
  action = action.lower()
  member = str(ctx.message.author.id)
  sender = ctx.message.author
  game = ""
  with open("games.json","r") as file:
    try:
      games = json.load(file)
    except:
      await member.send("**No games found**")
      return
  with open("bank.json", "r") as file:
    try:
      bank = json.load(file)
    except:
      print("ERROR: There are no members in the bank")
  # check if member is in a game
  for game in games:
    if member in games[game]['members']:
      game_id = game
  if game == "":
    await member.send("**You are not in a game**")
    return
  members_obj = []
  for member_id in games[game]['members']:
    player_obj = await client.fetch_user(int(member_id))
    members_obj.append(player_obj)
  game_name = games[game_id]['game']
  members_array = list(games[game_id]['members'].keys())
  member_name = ctx.message.author.name
  # different actions
  async def next_turn():
    turn = int(games[game_id]['turn'])
    total_players = len(members_array)
    turn += 1
    # new round
    if turn == total_players:
      # DETERMINE WHO WINS HERE
      turn = 0
      start = int(games[game_id]['start']) + 1 if int(games[game_id]['start']) + 1 != total_players else 0
      start2 = int(games[game_id]['start']) + 2 if int(games[game_id]['start']) + 2 != total_players else 0
      big = await client.fetch_user(int(members_array[start]))
      small = await client.fetch_user(int(members_array[start2]))
      bankrupt = []
      for member in games[game_id]['members']:
        games[game_id]['members'][member]['debt'] = '0'
        games[game_id]['members'][member]['hand'] = []
        if int(bank[member][0]) != 0:
          games[game_id]['members'][member]['status'] = 'Playing'
        else:
          bankrupt.append(member.name)
          games[game_id]['members'].pop(member)
          total_players -= 1
      for player in members_obj:
        await player.send(f"**Round over! PERSON WON!!!**")
        if bankrupt != []:
          for member in bankrupt:
            await player.send(f"**{member} wen't bankrupt :(**")
        if(total_player >= 2):
          await player.send(f"**The new big blind is {big.name} and the new small blind is {small.name}"**)
        else:
          await player.send(f"**Game over! Not enough people to play poker!**)
          games.pop(game_id)


    games[game_id]['turn'] = str(turn)

  if action == 'start':
    # next(iter(games[game_id]['members'])) gets first index of dictionary 'members'
    if member == members_array[0]:
      if len(games[game_id]['members'][member]['hand']) == 0 and len(games[game_id]['members']) > 1:
        
        # pick community cards
        for x in range(3):
          index = await random_card(games[game_id]['deck'])
          games[game_id]['community_cards'].append(games[game_id]['deck'][index])
          card = games[game_id]['deck'].pop(index)
        
        for player in members_obj:
          # sending messages to all players
          await player.send(f"**{member_name} has started the {game_name} game!**")

          # give players starting hand card1
          index = await random_card(games[game_id]['deck'])
          games[game_id]['members'][str(player.id)]['hand'].append(games[game_id]['deck'][index])
          card = games[game_id]['deck'].pop(index)
          card1 = await return_card(card)

          # give players starting hand card2
          index = await random_card(games[game_id]['deck'])
          games[game_id]['members'][str(player.id)]['hand'].append(games[game_id]['deck'][index])
          card = games[game_id]['deck'].pop(index)
          card2 = await return_card(card)

          await player.send(f"You drew a {card1[0]} of {card1[1]} and a {card2[0]} of {card2[1]}!")
        # update hands and deck
      else: await sender.send("*You need at least 2 players in the lobby or the game has already started*")
    else: await sender.send("*Only the owner of the game can do that*")
  # checks if it is member's turn

  elif member != members_array[int(games[game_id]['turn'])]:
    await sender.send("*It is not your turn*")

  elif action == 'raise':
    # check if raise is possible with current money
    member_money = int(bank[member][0]) - int(games[game_id]['members'][member]['debt'])
    if amount > 0 and member_money - amount >= 0:
      # valid raise
      for player in members_obj:
        await player.send(f"*{member_name} has raised the bet by ${amount}!*")
        player_debt = int(games[game_id]['members'][str(player.id)]['debt'])
        player_debt += amount
        games[game_id]['members'][str(player.id)]['debt'] = str(player_debt)
    elif member_money - amount < 0:
      sender.send(f"*You can't raise ${amount}, you currently have ${member_money} to raise if you subtract the cost to call*")
    else:
      sender.send("*You are alreadt all-in. Try using '%game check' instead.*")

  elif action == 'call':
    member_money = int(bank[member][0])
    member_debt = int(games[game_id]['members'][member]['debt'])
    if member_money == 0:
      await sender.send("*You are already all-in. Try using '%game check' instead.*")
    elif member_money > member_debt:
      games[game_id]['members'][member]['debt'] = '0'
      for player in members_obj:
        await player.send(f"*{member_name} has called the bet of ${member_debt}*")
    else:
      games[game_id]['members'][member]['debt'] = '0'
      for player in members_obj:
        await player.send(f"*{member_name} has called the bet with ${member_money} and is now all-in!*")


  # dump new info
  with open("games.json","w") as file:
    json.dump(games, file)

  


@client.command()
async def test(ctx):
  embed = discord.Embed(title="Title", description="Desc", color=discord.Color.gold()) #creates embed
  file = discord.File("owen.png", filename="image.png")
  embed.set_image(url="attachment://image.png")
  await ctx.send(file=file, embed=embed)


@client.command(brief="Create a poker game")
async def poker(ctx):
  with open("games.json", "r") as file:
    try:
      games = json.load(file)
    except:
      games = dict()

  with open("bank.json", "r") as file:
    try:
      bank = json.load(file)
    except:
      print("There are no members in the bank")
      await ctx.send("**Something went wrong.**")
  
  owner = str(ctx.message.author.id)

  # check if owner is already in a game
  for game in games:
    for member in games[game]['members']:
      if member == owner:
        await ctx.message.author.send(f"**Can't participate in 2 games at once. You are currently in a {games[game]['game']} game.**")
        return
  
  if owner in bank:
    if int(bank[owner][0]) >= 100:
      embed = discord.Embed(title=("POKER: REACT WITH ✅ TO PLAY"), description="People playing: 1", color=discord.Color.blue())
      embed.add_field(name="Players:", value=ctx.message.author.mention, inline=False)
      in_embed = await ctx.send(embed=embed)
      await in_embed.add_reaction("✅")
      denver = pytz.timezone('America/Denver')
      denver_time = datetime.now(denver)
      goalTime = denver_time + timedelta(hours=2)
      goalString = str(goalTime)
      # write formatted goal to file
      formattedGoal = goalString[0:19]
      # information about the game
      new_poker = {
        'game': 'poker',
        'community_cards':[],
        'pot': '0',
        'members': {owner: {'status': 'Playing', 'hand': [], 'debt': '0'}},
        'deck': ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52'],
        'start':'0', # index of who started off the round (for big/little blind)
        'turn': '0', # index of whos turn it currently is
        'end_time': formattedGoal, # 2 hours after game is made
      }
      # member info
      games[str(in_embed.id)] = new_poker
      # dump new poker info
      with open("games.json", "w") as file:
        json.dump(games, file)
    else:
      await ctx.send("**You need 100 or more credits to create a poker game.**")
  else:
    await ctx.send("**You dont have money set up! Every hour money is updated and your bank account will be created.**")
    

@client.command(brief="Returns your total money")
async def bank(ctx):
  with open("bank.json", "r") as file:
    try:
      bank = json.load(file)
    except:
      print("There are no members in the bank")
  member = str(ctx.message.author.id)
  if member not in bank:
    await ctx.send("**You dont have money set up! Every hour money is updated and your bank account will be created.**")
  else:
    await ctx.send(f"**You currently have ${bank[member][0]} in your bank account.**")



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


@client.command(brief="Add a welcome message to the server", description = "Multiple word messages and links are supported. Using '=' in the message will @ the person who joined.")
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
      message = messages[random.randrange(1, len(messages))]
      message = message.replace('=', member.mention)
      await channel.send(message)
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
  await ctx.send(f"*{answer}*")


@client.command()
async def hello(ctx):
  await ctx.send('oi punk :snake:')


@client.command(brief="Flip a coin")
async def flip(ctx):
  side = random.randint(1, 2)
  if (side == 1):
    await ctx.send("*Heads*")
  else:
    await ctx.send("*Tails*")


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
    message_id = str(payload.message_id)
    with open("lfg.json", "r") as file:
      all_lfg = json.load(file)
    if message_id in all_lfg:
      # retrieve lfg info
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
      try:
        msg = await channel.fetch_message(int(message_id))
      except:
        print(f"Message for the {lfg_name} lfg in {guild_name} could not be found.")
        all_lfg.pop(message_id)
        with open("lfg.json", "w") as file:
          json.dump(all_lfg, file)
        return
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
      return
    member = str(payload.member.id)
    if str(payload.emoji.name) == "✅":
      with open("bank.json", "r") as file:
        try:
          bank = json.load(file)
        except:
          print("There are no members in the bank")
        if member not in bank:
          await payload.member.send("**You can't play becayse you dont have a bank account set up! Every hour money is updated and your bank account will be created.**")
          return
        else:
          await payload.member.send(f"**You currently have ${bank[member][0]} in your bank account.**")
      with open("games.json", "r") as file:
        games = json.load(file)
      for game in games:
        if game == message_id and member not in games[message_id]['members'] and len(games[message_id]['members']) <= 12:
          # match found
          try:
            in_embed = await client.get_channel(payload.channel_id).fetch_message(int(message_id))
          except:
            print(f"Message for a game could not be found.")
            games.pop(message_id)
            with open("games.json", "w") as file:
              json.dump(games, file)
            return
          send_out = ""
          # create send_out
          player_info = {
            'status': 'Playing',
            'hand': [],
            'debt': '0'
          }
          games[message_id]['members'][member] = player_info
          for member in games[message_id]['members']:
            member_obj = await client.fetch_user(int(member))
            send_out += (member_obj.mention + '\n')
          # embed
          des = "People playing: " + str(len(games[message_id]['members']))
          new_info = discord.Embed(title=("POKER: REACT WITH ✅ TO PLAY"), description=des, color=discord.Color.blue())
          new_info.add_field(name="Players:", value=send_out, inline=False)
          await in_embed.edit(embed=new_info)
          # dump new info
          with open("games.json", "w") as file:
            json.dump(games, file)
        




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
    
    repeat_members = []
    # adds members who are not in bank to bank
    for guild in client.guilds:
      for member in guild.members:
        if str(member.id) not in bank:
          bank[str(member.id)] = ["5000"]
        elif member.id not in repeat_members:
          #add money to existing members
          money = int(bank[str(member.id)][0])
          money += 100
          bank[str(member.id)][0] = str(money)
        repeat_members.append(member.id)
    
    all_lfg["time"] = str(extracted_new_day + timedelta(hours=1))

    with open("lfg.json", "w") as file:
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
