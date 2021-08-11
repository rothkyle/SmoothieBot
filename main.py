import discord
import os
import requests
import json
import random
from PIL import Image
from discord.ext import commands
from keep_alive import keep_alive
from datetime import datetime
import pytz
from datetime import timedelta
import asyncio
import youtube_dl
import validators
from pokereval.card import Card
from operator import itemgetter
from pokereval.hand_evaluator import HandEvaluator
from riotwatcher import LolWatcher, ApiError
import cassiopeia as lol
from cassiopeia import Summoner

streams = os.getenv('streams')
random.seed()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="%", intents = intents)
deck_image = Image.open('deck.png')
riot_key = os.getenv('riot_key')
lol.set_riot_api_key(riot_key)
lol.set_default_region("NA")
lol_watcher = LolWatcher(riot_key)


@client.event
async def on_ready():
  print("Bot is up and running")
  #await check()
  asyncio.create_task(check())
  #asyncio.create_task(currency_update())


@client.command()
async def test(ctx):
  denver = pytz.timezone('America/Denver')
  denver_time = datetime.now(denver)
  goal_time = denver_time + timedelta(hours=float(2))
  goal_string = str(goal_time)
  time_left = str(goal_time-denver_time)[0:19]
  # write formatted goal to file
  formattedGoal = goal_string[0:19]
  #embed
  embed = discord.Embed(title=("LFG for game"), description="People playing: 1/5", color=discord.Color.blue())
  embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
  embed.set_thumbnail(url="https://lfgroup.gg/wp-content/uploads/2020/05/lfg-banner-transparent.png")
  embed.add_field(name="Players:", value=ctx.message.author.mention, inline=False)
  embed.add_field(name="Goal Time:", value=formattedGoal, inline=True)
  embed.add_field(name="Time Remaining:", value=time_left, inline=True)
  embed.set_footer(text="React to this message with ✅ or 🚫 to join or leave this lfg.")
  await ctx.send(embed=embed)


@client.command()
async def zoop(ctx, summoner:str):
  player = Summoner(name=summoner)
  good_with = player.champion_masteries.filter(lambda cm: cm.level >= 6)
  print([cm.champion.name for cm in good_with])


@client.command()
async def lolstat(ctx, summoner_name : str):
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
  else: await ctx.send("**This summoner doesn't play Ranked Solo/Duo.**")


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
  }
  if title in urls: return urls[title]
  else: return "https://lfgroup.gg/wp-content/uploads/2020/05/lfg-banner-transparent.png"


async def in_bank(member):
  with open("bank.json", "r") as file:
    try:
      bank = json.load(file)
    except:
      print("There are no members in the bank")
  if member not in bank:
    return False
  return True


async def return_card_name(card : str):
  temp_num = int(card[0:2])
  number = str(temp_num)
  suit = card[2]
  if suit == '1':
    suit = "Hearts"
  elif suit == '2':
    suit = "Spades"
  elif suit == '3':
    suit = "Diamonds"
  elif suit == '4':
    suit = "Clubs"
  
  if number == '14':
    number = "Ace"
  elif number == '11':
    number = "Jack"
  elif number == '12':
    number = "Queen"
  elif number == '13':
    number = "King"
  card_name = number + " of " + suit
  return card_name


async def hand_value(hand : list, community : list):
  hole = []
  # player hand
  for value in hand:
    number = int(value[0:2])
    suit = int(value[2])
    card = Card(number, suit)
    hole.append(card)

  board = []
  # board
  for value in community:
    number = int(value[0:2])
    suit = int(value[2])
    card = Card(number, suit)
    board.append(card)
  
  score = HandEvaluator.evaluate_hand(hole, board)
  return score
  
  
@client.command(brief="Allows you to type to other people in your game")
async def gamechat(ctx, *, message):
  member = str(ctx.message.author.id)
  with open("games.json","r") as file:
    try:
      games = json.load(file)
    except:
      await ctx.message.author.send("**No games found**")
      return
  game_id = ""
  for game in games:
    if member in games[game]['members']:
      game_id = game
  if game_id == "":
    await ctx.message.author.send("**You are not in a game**")
    return
  for member_id in games[game]['members']:
    player_obj = await client.fetch_user(int(member_id))
    await player_obj.send(f"*{ctx.message.author.name}: {message}*")
  

async def random_card(deck):
  deck_length = len(deck)
  index = random.randint(0,deck_length-1)
  return index


async def getCoords(face_num,suit_num):
  if(face_num == 14):
    face_num = 1
  coords = (((face_num-1)*225), ((suit_num-1)*315),((face_num)*225), (((suit_num))*315))
  return coords


async def getCommunity(cards):
  height = 315
  width = 225 * len(cards)

  river_image = Image.new('RGBA', (width, height), (0,0,0, 0))

  for x in range(0, len(cards)):
    card_temp = deck_image.crop(await getCoords(int(cards[x][0:2]), int(cards[x][2])))
    river_image.paste(card_temp,(225*x, 0), mask=card_temp)
  
  river_image.save("community.png", format="png")
  card_temp.close()
  river_image.close()


async def generateHandImage(face_1, suit_1, face_2, suit_2):
  card1_img = deck_image.crop(await getCoords(face_1, suit_1))
  card2_img = deck_image.crop(await getCoords(face_2, suit_2))

  card1_img = card1_img.convert("RGBA")
  card2_img = card2_img.convert("RGBA")


  hand = Image.new('RGBA', (285, 395), (0,0,0, 0))
  hand.paste(card1_img,(0,0), mask=card1_img)
  hand.paste(card2_img, (60, 80),mask=card2_img)
  hand.save("player_hand.png", format="png")
  hand.close()


@client.command(brief="Used to interact with games (use \"%help game\" for more)", description="Poker Actions:\n\nStart: The owner of the game can use this to start the game.\nCheck: Passes your turn.\nRaise: Raises the bet of the current turn. Everyone must pay this amount to keep playing. Use \"%game raise <amount>\".\nCall : Allows you to pay for the previous bet or blind to keep playing.\nFold : Give up on the current round.\nPot  : Display the pot of the current round.\nHand : Display your current hand.\nRiver: Display the current community cards.")
async def game(ctx, action : str, amount : int=0):
  action = action.lower()
  member = str(ctx.message.author.id)
  sender = ctx.message.author
  game = ""
  with open("games.json","r") as file:
    try:
      games = json.load(file)
    except:
      await sender.send("**No games found**")
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
    await sender.send("**You are not in a game**")
    return
  members_obj = []
  for member_id in games[game]['members']:
    player_obj = await client.fetch_user(int(member_id))
    members_obj.append(player_obj)
  # retrieve variables
  game_name = games[game_id]['game']
  members_array = list(games[game_id]['members'].keys())
  member_name = ctx.message.author.name
  owner = await client.fetch_user(int(members_array[0]))
  member_money = int(bank[member][0])
  member_debt = int(games[game_id]['members'][member]['debt'])
  curr_pot = int(games[game_id]['pot'])
  started = False
  total_players = len(members_array)
  turn = int(games[game_id]['turn'])

  for player in members_array:
    if games[game_id]['members'][player]['hand'] != []:
      started = True
  turn_next = (turn + 1) % total_players
  while games[game_id]['members'][members_array[turn_next]]['hand'] == [] and started:
    turn_next = (turn_next + 1) % total_players
  prev_turn = (turn - 1) % total_players
  while games[game_id]['members'][members_array[prev_turn]]['hand'] == [] and started:
    prev_turn = (prev_turn + 1) % total_players
  
  async def next_turn():
    curr_turn = games[game_id]['turn']
    draw = True if games[game_id]['go_to'] == curr_turn else False
    turn = turn_next
    total_players = len(members_array)
    end = True if len(games[game_id]['community_cards']) == 5  and draw else False
    total_playing = 0
    curr_pot = int(games[game_id]['pot'])
    show_hand = True
    for player in members_array:
      if games[game_id]['members'][player]['hand'] != []:
        total_playing += 1
    if total_playing == 1:
      end = True
      draw = True
      show_hand = False
      games[game_id]['community_cards'] = ["064", "084", "094", "104", "114"]
    start = int(games[game_id]['start'])
    if games[game_id]['loop_count'] == '2':
      games[game_id]['loop_count'] = '0'
      draw = True
    # new round
    if draw:
      games
      # pick community cards
      if games[game_id]['community_cards'] == []:
        community_cards = []
        for x in range(3):
          index = await random_card(games[game_id]['deck'])
          games[game_id]['community_cards'].append(games[game_id]['deck'][index])
          card = games[game_id]['deck'].pop(index)
          card_name = await return_card_name(card)
          community_cards.append(card_name)
        
        community = ""
        for card_num, card in enumerate(community_cards):
          if card_num != 2:
            community += card + ", "
          else:
            community += "and a " + card + "!"
        await getCommunity(games[game_id]['community_cards'])
        current_turn_name = await client.fetch_user(int(members_array[turn]))
        # send message to each player
        for player in members_obj:
          file_com = discord.File("community.png", filename="image.png")
          embed = discord.Embed(title="Community cards", color=discord.Color.dark_red())
          embed.set_image(url="attachment://image.png")
          await player.send(f"**The community cards are {community}**")
          await player.send(file=file_com, embed=embed)
          await player.send(f"*It is now {current_turn_name.name}'s turn*")
          
      
      # normal round with card draw
      elif not end:
        index = await random_card(games[game_id]['deck'])
        games[game_id]['community_cards'].append(games[game_id]['deck'][index])
        card = games[game_id]['deck'].pop(index)
        card = await return_card_name(card)
        current_turn_name = await client.fetch_user(int(members_array[turn]))

        #file_img = discord.File("player_hand.png", filename="image.png")
        #embed = discord.Embed(title="Your hand", color=discord.Color.dark_red())
        #embed.set_image(url="attachment://image.png")
        await getCommunity(games[game_id]['community_cards'])
        # send message to each player
        for player in members_obj:
          file_img2 = discord.File("community.png", filename="image.png")
          embed2 = discord.Embed(title="Community cards", color=discord.Color.dark_red())
          embed2.set_image(url="attachment://image.png")
          await player.send(f"**The {card} was drawn for the community cards**")
          #await player.send(file=file_img, embed=embed)
          await player.send(file=file_img2, embed=embed2)
          await player.send(f"*It is now {current_turn_name.name}'s turn*")

      # end of game sequence
      else:
        scores = []
        # get scores of all players
        for player in members_array:
          # creates score for each remaining player in game
          if games[game_id]['members'][player]['hand'] != []:
            new_score = (player, await hand_value(games[game_id]['members'][player]['hand'], games[game_id]['community_cards']))
            scores.append(new_score)
        max_score = str(max(scores, key=itemgetter(1))[1])
        winners = []
        # will create list of all winners
        for index,score in enumerate(scores):
          if score[1] == float(max_score):
            winners.append(score)
        winner_pot = round(curr_pot / len(winners))
        # interact with each winner
        for winner in winners:
          winner_id = winner[0]
          current_winner = await client.fetch_user(int(winner_id))
          for player in members_obj:
            await player.send(f"***{current_winner.name} won the game for ${curr_pot}!***")
          winner_money = int(bank[winner_id][0])
          winner_money += winner_pot
          bank[winner_id][0] = str(winner_money)
        # finish game
        bankrupt = []
        # update each player
        for member in games[game_id]['members']:
          games[game_id]['members'][member]['debt'] = '0'
          games[game_id]['members'][member]['hand'] = []
          if int(bank[member][0]) != 0:
            games[game_id]['members'][member]['status'] = 'Playing'
          else:
            bankrupt.append(member.name)
            games[game_id]['members'].pop(member)
            total_players -= 1
        # reset poker game
        games[game_id]['community_cards'] = []
        games[game_id]['go_to'] = games[game_id]['start']
        games[game_id]['start'] = str(turn_next)
        games[game_id]['pot'] = '0'
        games[game_id]['turn'] = str(turn_next)
        games[game_id]['last_raise'] = '0'
        games[game_id]['deck'] = ['021','031','041','051','061','071','081','091','101','111','121','131','141','022','032','042','052','062','072','082','092','102','112','122','132','142','023','033','043','053','063','073','083','093','103','113','123','133','143','024','034','044','054','064','074','084','094','104','114','124','134','144']
        # send update to each player
        for player in members_obj:
          if bankrupt != []:
            for member in bankrupt:
              await player.send(f"**{member} wen't bankrupt :(**")
          if(total_players >= 2):
            await player.send(f"**{owner.name} can start a new game or end this lobby with '%game end'**")
          else:
            await player.send(f"**Game over! Not enough people to play.**")
        if total_players < 2:
          games.pop(game_id)
        with open("games.json","w") as file:
          json.dump(games, file)
        with open("bank.json","w") as file:
          json.dump(bank, file)
        return
    else:
      #if games[game_id]['start'] == str(turn)
      #  games[game_id]['loop_count'] = str(int(games[game_id]['loop_count']) + 1)
      # turn with no draw
      current_turn_name = await client.fetch_user(int(members_array[turn]))
      for player in members_obj:
        await player.send(f"*It is now {current_turn_name.name}'s turn*")
    games[game_id]['turn'] = str(turn)
    games[game_id]['start'] = str(start)
    with open("games.json","w") as file:
      json.dump(games, file)
    with open("bank.json","w") as file:
      json.dump(bank, file)
    return
  

  # different actions
  if action == 'start':
    if started:
      await sender.send("*Game has already started*")
      return
    if member == members_array[0]:
      if not started and len(games[game_id]['members']) > 1:
        
        games[game_id]['go_to'] = str(prev_turn)
        start = int(games[game_id]['start'])
        big = start
        little = turn_next
        big_member = await client.fetch_user(int(members_array[big]))
        small_member = await client.fetch_user(int(members_array[little]))
        for player_index,player in enumerate(members_obj):
          # sending messages to all players
          if player_index == big:
            # big blind
            games[game_id]['members'][str(player.id)]['debt'] = '500'
          elif player_index == little:
            # little blind
            games[game_id]['members'][str(player.id)]['debt'] = '250'
          await player.send(f"**{member_name} has started the {game_name} game!\nThe big blind is {big_member.name} ($500) and the small blind is {small_member.name} ($250)**")

          # give players starting hand card1
          index = await random_card(games[game_id]['deck'])
          games[game_id]['members'][str(player.id)]['hand'].append(games[game_id]['deck'][index])
          card1 = games[game_id]['deck'].pop(index)
          card1_name = await return_card_name(card1)

          # give players starting hand card2
          index = await random_card(games[game_id]['deck'])
          games[game_id]['members'][str(player.id)]['hand'].append(games[game_id]['deck'][index])
          card2 = games[game_id]['deck'].pop(index)
          card2_name = await return_card_name(card2)
          await player.send(f"**You drew a {card1_name} and a {card2_name}!**\n*It is now {members_obj[turn].name}'s turn*")

          # generate image of hand
          await generateHandImage(int(card1[0:2]), int(card1[2]), int(card2[0:2]), int(card2[2]))
          file_img = discord.File("player_hand.png", filename="image.png")
          embed = discord.Embed(title="Your hand", color=discord.Color.dark_red())
          embed.set_image(url="attachment://image.png")
          await player.send(file=file_img, embed=embed)

        # update hands and deck
      else: await sender.send("*You need at least 2 players in the lobby or the game has already started*")
    else: await sender.send(f"*Only the owner of the game ({owner.name}) can do that*")
  
  elif action == 'pot':
    await sender.send(f"*The current pot is ${games[game_id]['pot']}*")
  
  elif action == 'hand' and started:
    if games[game_id]['members'][member]['hand'] != []:
      card1 = games[game_id]['members'][member]['hand'][0]
      card2 = games[game_id]['members'][member]['hand'][1]
      card1_name = await return_card_name(card1)
      card2_name = await return_card_name(card2)
      await generateHandImage(int(card1[0:2]), int(card1[2]), int(card2[0:2]), int(card2[2]))
      hand_img = discord.File("player_hand.png", filename="image.png")
      embed = discord.Embed(title="Your hand", color=discord.Color.dark_red())
      embed.set_image(url="attachment://image.png")
      await sender.send(f"**You have a {card1_name} and a {card2_name}.**")
      await sender.send(file=hand_img, embed=embed)
    else:
      await sender.send(f"*Your hand is empty*")
  
  elif action == 'river' and started:
    river = games[game_id]['community_cards']
    if river != []:
      await getCommunity(river)
      file_com = discord.File("community.png", filename="image.png")
      embed = discord.Embed(title="Community cards", color=discord.Color.dark_red())
      embed.set_image(url="attachment://image.png")
      community_cards = []
      for card in river:
        card_name = await return_card_name(card)
        community_cards.append(card_name)

        community = ""
      for card_num, card in enumerate(community_cards):
        if card_num != len(community_cards) - 1:
          community += card + ", "
        else:
          community += "and a " + card
      await sender.send(f"**The community cards are {community}.**")
      await player.send(file=file_com, embed=embed)
    else: await sender.send("*There are no community cards*")
  
  elif action == 'end':
    if member == members_array[0] and not started:
      for player in members_obj:
        await player.send(f"***{member_name} has ended the game***")
      games.pop(game_id)
    elif member != members_array[0]:
      await sender.send(f"*Only the owner of the game ({owner.name}) can do that before the round has started*")
    else:
      await sender.send("*You can only end the game before the round has started*")
    
  # checks if it is member's turn
  elif member != members_array[int(games[game_id]['turn'])] and started:
    current_turn_name = await client.fetch_user(int(members_array[int(games[game_id]['turn'])]))
    await sender.send(f"*You can't do that because it is currently {current_turn_name.name}'s turn*")

  elif action == 'raise' and started:
    last_raise = int(games[game_id]['last_raise'])
    # check if raise is possible with current money
    member_money = int(bank[member][0])

    if last_raise > amount:
      await sender.send(f"*Your raise must be greater than or equal to the last raise (${last_raise})*")
    elif amount > 0 and member_money - amount - member_debt >= 0:
      # valid raise
      if member_debt == 0:
        message = f"*{member_name} has raised the bet by ${amount}!*"
      else:
        message = f"*{member_name} has called the ${member_debt} and raised the bet by ${amount}!*"
      for player_index, player in enumerate(members_obj):
        await player.send(message)
        player_debt = int(games[game_id]['members'][str(player.id)]['debt'])
        player_debt += amount
        games[game_id]['members'][str(player.id)]['debt'] = str(player_debt)
      games[game_id]['pot'] = str(curr_pot + amount + member_debt)
      bank[member][0] = str(member_money - amount - member_debt)
      games[game_id]['go_to'] = str(prev_turn)
      games[game_id]['last_raise'] = str(amount)
      games[game_id]['members'][member]['debt'] = '0'
      await next_turn()
    elif member_money - amount - member_debt < 0:
      await sender.send(f"*You don't have enough money to call the previous ${member_debt} and raise by ${amount}.*")
    elif member_money - amount < 0:
      await sender.send(f"*You don't have enough money to raise by ${amount} (use %bank to see your balance)*")
    elif member_money == 0:
      await sender.send("*You are already all-in. Try using '%game check' instead.*")
    else:
      await sender.send("*You must raise the bet by a value greater than $0*")

  elif action == 'call' and started:
    if member_debt == 0:
      await sender.send("*You have no bet to call*")
    elif member_money == 0:
      await sender.send("*You are already all-in. Try using '%game check' instead.*")
    elif member_money > member_debt:
      games[game_id]['members'][member]['debt'] = '0'
      games[game_id]['pot'] = str(curr_pot + member_debt)
      # subtract from bank
      bank[member][0] = str(member_money - member_debt)
      # send update to players
      for player in members_obj:
        await player.send(f"*{member_name} has called the bet of ${member_debt}*")
      await next_turn()
    else:
      games[game_id]['members'][member]['debt'] = '0'
      games[game_id]['pot'] = str(curr_pot + member_debt)
      bank[member][0] = '0'
      for player in members_obj:
        await player.send(f"*{member_name} has called the bet with ${member_money} and is now all-in!*")
      await next_turn()

  elif action == 'check' and started:
    if member_debt == 0 or member_money == 0:
      for player in members_obj:
        await player.send(f"*{member_name} checked*")
      await next_turn()
    else:
      await sender.send(f"*You must call the ${member_debt} to continue. Use '%game call' to call.*")

  elif action == 'fold' and started:
    for player in members_obj:
      await player.send(f"*{member_name} has folded*")
    games[game_id]['members'][member]['hand'] = []
    games[game_id]['members'][member]['status'] = 'Fold'
    await next_turn()

  # dump new info
  elif not started:
    await sender.send("*Game hasn't started*")
  else:
    await sender.send("*Invalid input*")
  with open("games.json","w") as file:
    json.dump(games, file)
  with open("bank.json","w") as file:
    json.dump(bank, file)


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
      goal_time = denver_time + timedelta(hours=2)
      goal_string = str(goal_time)
      # write formatted goal to file
      formattedGoal = goal_string[0:19]
      # information about the game
      new_poker = {
        'game': 'poker',
        'community_cards':[],
        'pot': '0',
        'members': {owner: {'status': 'Playing', 'hand': [], 'debt': '0'}},
        'deck': ['021','031','041','051','061','071','081','091','101','111','121','131','141','022','032','042','052','062','072','082','092','102','112','122','132','142','023','033','043','053','063','073','083','093','103','113','123','133','143','024','034','044','054','064','074','084','094','104','114','124','134','144'],
        'start':'0', # index of who started off the round (for big/little blind)
        'turn': '0', # index of whos turn it currently is
        'end_time': formattedGoal, # 2 hours after game is made
        'go_to':'-1',
        'loop_count':'0',
        'last_raise':'0'
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
async def lfg(ctx, game : str, goal : str, numHours : float=2, scheduled: bool=False):
  if numHours <= 200.00 and numHours > 0.00 and int(goal) > 1:
    original_game = game
    if len(game) == 22:
      try:
        role_id = game[3:21]
        print(role_id)
        role = ctx.guild.get_role(int(role_id))
        game = role.name
      except:
        print(role_id + " doesn't exist")
    # get current time
    denver = pytz.timezone('America/Denver')
    denver_time = datetime.now(denver)
    goal_time = denver_time + timedelta(hours=float(numHours))
    time_left = str(goal_time-denver_time)[0:19]
    goal_string = str(goal_time)
    # write formatted goal to file
    formattedGoal = goal_string[0:19]
    #embed
    embed = discord.Embed(title=(f"LFG for {game}"), description=f"People playing: 1/{goal}", color=discord.Color.green())
    #embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    embed.set_thumbnail(url=await get_thumbnail(game))
    embed.add_field(name="Players:", value=ctx.message.author.mention, inline=False)
    embed.add_field(name="Goal Time:", value=formattedGoal, inline=True)
    embed.add_field(name="Time Remaining:", value=time_left, inline=True)
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
      'guild_id':str(guild_id),
      'guild_name':str(guild_name),
      'goal_time':str(formattedGoal),
      'time_left':time_left,
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

    all_lfg[str(embed_id)] = lfg_dict

    # write to json file
    with open("lfg.json", "w") as file:
      json.dump(all_lfg, file)
    print("Created counter for " + game + " in " + ctx.message.guild.name)
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
          for person in members:
            send_out += (person.mention + "\n")
          des = f"People playing: {count}/{goal}"
          new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.green())
          new_info.set_thumbnail(url=await get_thumbnail(lfg_name))
          new_info.add_field(name="Players:", value=send_out, inline=False)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=True)
          new_info.add_field(name="Time Remaining:", value=time_left, inline=True)
          new_info.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
          await in_embed.edit(embed=new_info)

          #met goal
          if (count == goal):
            print(f"Goal has been reached for {goal} in {guild_name}.")
            if not scheduled:          
              for person in members:
                await person.send(f"**Your group for {lfg_name} in {guild_name} is ready!\nPeople playing:\n{send_out}**")
              await in_embed.delete()
              all_lfg.pop(embed_id)
              print("Removed lfg from database.")
          #not met goal
          else:
            print("Detected reaction from " + str(payload.member) + ". There are is now ", count, " out of ", goal, " people ready to play " + lfg_name + ".")
          
          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        else:
          print(payload.member.name + " already in queue.")
        if count != goal:
          await embed_obj.remove_reaction("✅", payload.member)

        #remove from lfg
      elif str(payload.emoji.name) == "🚫":
        if member in members:
          count -= 1
          members.remove(member)
          all_lfg[embed_id]['members'].remove(str(member.id))
          print(f"{payload.member} has left the lfg for {lfg_name}.")
          des = f"People playing: {count}/{goal}"
          if members == []:
            send_out = "N/A"
          else:
            for person in members:
              send_out += (person.mention + "\n")
          #embed
          new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.green())
          new_info.set_thumbnail(url=await get_thumbnail(lfg_name))
          new_info.add_field(name="Players:", value=send_out, inline=False)
          new_info.add_field(name="Goal Time:", value=goal_time, inline=True)
          new_info.add_field(name="Time Remaining:", value=time_left, inline=True)
          new_info.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
          await in_embed.edit(embed=new_info)

          # dump new info into lfg json
          with open("lfg.json", "w") as file:
            json.dump(all_lfg, file)
        await embed_obj.remove_reaction("🚫", payload.member)
      return
    elif str(payload.emoji.name) == "✅":
      member = str(payload.member.id)
      with open("bank.json", "r") as file:
        try:
          bank = json.load(file)
        except:
          print("There are no members in the bank")
        if member not in bank:
          await payload.member.send("**You can't play because you dont have a bank account set up! Every hour money is updated and your bank account will be created.**")
          return
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
          await payload.member.send(f"**You have joined the poker game and you currently have ${bank[member][0]} in your bank account.**")
          # dump new info
          with open("games.json", "w") as file:
            json.dump(games, file)
          break
        




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
          money += 10
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
    goal_time = all_lfg[file]['goal_time']
    extracted_new = datetime.strptime(goal_time, "%Y-%m-%d %H:%M:%S")
    time_left = str(extracted_new-formatted_denver)[0:19]
    members = all_lfg[file]['members']
    lfg_name = all_lfg[file]['lfg_name']
    names = []
    if (formatted_denver >= extracted_new):  # goal time is passed
      print("Deleting file " + file.rstrip('\n')  + " due to time passing")
      # retrieve lfg information
      goal = int(all_lfg[file]['goal'])
      channel = client.get_channel(int(all_lfg[file]['channel_id']))
      in_embed = await channel.fetch_message(int(all_lfg[file]['embed_id']))
      scheduled = True if all_lfg[file]['scheduled'] == 'True' else False
      guild = all_lfg[file]['guild_name']
      count = len(members)
      send_out = ""
      # create message send out
      for player_id in members:
        member_obj = await client.fetch_user(int(player_id))
        if scheduled and count == goal:
          await member_obj.send(f"**Your scheduled event for {lfg_name} in {guild} is ready to start!**")
        elif scheduled and count != goal:
          await member_obj.send(f"**Your scheduled event for {lfg_name} in the '{guild}' server has failed to meet its goal, but you only need {goal - count} more!**")
        names.append(member_obj)
      # delete unscheduled message but save scheduled message
      if not scheduled:
        await in_embed.delete()
      else:
        if names == []:
          send_out = "N/A"
        else:
          for member in names:
            send_out += (member.mention + "\n")
        # update embed
        des = str("People playing: " + str(count))
        new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.red())
        new_info.set_thumbnail(url=await get_thumbnail(lfg_name))
        new_info.add_field(name="Players:", value=send_out, inline=True)
        new_info.add_field(name="Goal Time:", value="Times up!", inline=False)
        new_info.add_field(name="Time Remaining:", value="0", inline=True)
        new_info.set_footer(text="LFG has ended.")
        await in_embed.edit(embed=new_info)
      # queue file for deletion
      to_delete.append(file)
    # update time in lfg time left
    else:
      count = len(members)
      send_out = ""
      names = []
      channel = client.get_channel(int(all_lfg[file]['channel_id']))
      in_embed = await channel.fetch_message(int(all_lfg[file]['embed_id']))
      for player_id in members:
        member_obj = await client.fetch_user(int(player_id))
        names.append(member_obj)
      if names == []:
        send_out = "N/A"
      else:
        for member in names:
          send_out += (member.mention + "\n")
      des = str("People playing: " + str(count))
      new_info = discord.Embed(title=("LFG for " + str(lfg_name)), description=des, color=discord.Color.green())
      new_info.set_thumbnail(url=await get_thumbnail(lfg_name))
      new_info.add_field(name="Players:", value=send_out, inline=False)
      new_info.add_field(name="Goal Time:", value=goal_time, inline=True)
      new_info.add_field(name="Time Remaining:", value=time_left, inline=True)
      new_info.set_footer(text="React to this message with ✅ or 🚫 to join/leave this lfg.")
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
