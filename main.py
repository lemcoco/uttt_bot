import discord
from discord.ext import commands
import os
import json
from random import randint, choice
from shutil import copy
from boardcreation import empty_board, add_mark, add_bigmark
from gamestrategy import take_init, take_info, placestrategy, startstrategy
from utils import *

"""
    Main program of Ultimate Tic Tac Toe BOT

    Use a commands.Bot object with async functions
    
    This program needs :
        - utils.py : Not async functions that make sure the game runs conrrectly.
        - boardcreation.py : fuctions to create grid, image of the board. The file grid is overwrited during the game and delete at the end.
        - gamestrategy.py : functions allow the BOT to play against a user.
        - keepalive.py : uncomment the lines '#from keep_alive import keep_alive' and '#keep_alive()' when program run on a server.
        - temp folder : working folder to create video without disturbing game in progress if there is one.
        - config.json : json files that contain BOT token, BOT prefix and all msg the BOT can be led to write.

    The program is based on the lists board and uboard :
        - board contains 9 lists correspond to the 9 classic tic-tac-toe boards with of 9 elements correspond to the 9 cells.
        - uboard contains 9 elements correspond to the 9 tic-tac-toe boards.
        The elements are :  - None if nobody takes the cell
                            - True if the first player (X) takes the cell
                            - False if the second player (O) takes the cell

    For the display, program use the temporary image 'grid'
        
"""

#Prefix & Token load
with open('config.json') as config_file:
    config = json.load(config_file)

#token = config['GENERAL']['DISCORD_TOKEN'] #on local machine, Token in config.json file
token = process.env.DISCORD_TOKEN #on Heroku, Token in Config Vars
prefix = config['GENERAL']['PREFIX']

client = commands.Bot(command_prefix=prefix)

@client.event
async def on_ready():
    print("READY TO PLAY TIC TAC TOE!!")

#Variables init
language_list = config['GENERAL']['langlist']
lang = language_list[0]
player1 = ""
player2 = ""
turn = ""
count = 0
ucount = 0
boardmsg = None
turnmsg = None
gameOver = True
next_board = None
board = [] #Littles boards 
uboard = [] #Ultimate board
autoplay = [False, False]
    
@client.command()
async def fight(ctx, p1: discord.Member, p2: discord.Member):
    """ Begins a game
        Takes two arguments: <@player1> -> First player, he plays with X
            <@player2> -> Second player, he plays with O
        You can play against the BOT!"""
    global lang
    global player1
    global player2
    global turn
    global count
    global ucount
    global boardmsg
    global turnmsg
    global gameOver
    global next_board
    global board
    global uboard
    global autoplay
    
    if p1.id != p2.id: #Check if user don't try to play against himself
        
        if gameOver: #Check if a game is in progress

            #boards init
            board = [[ None for _ in range(9)] for _ in range(9)]
            uboard = [None for _ in range(9)]

            #Global variables init
            player1 = p1
            player2 = p2
            ucount = 0
            gameOver = False

            #autoplay check and init
            if client.user.id == player1.id: autoplay = [True, False]
            elif client.user.id == player2.id: autoplay = [False, True]
            else: autoplay = [False, False]
            
            print('NEW GAME STARTS')

            gamefile_init(str(p1), str(p2)) #init the csv game file
            grid = empty_board() #init the grid

            #Print the board & delete command msg
            await ctx.message.delete()
            title = config['MESSAGES']['fight'][lang]
            msg = str( eval( config['MESSAGES']['fight_msg'][lang] ) )
            fightmsg = discord.Embed(title = title , description = msg, color = 0xf1c40f)
            await ctx.send(embed = fightmsg) #this msg will stay in the channel
            
            if autoplay != [True, False]:
                if autoplay[1] == True:
                    take_init()
                    msg = config['MESSAGES']['autoplay'][lang]
                    await ctx.send(msg)
                #Global variables init
                turn = player1
                count = 0
                next_board = None
                boardmsg = await ctx.send(file = discord.File(grid))
                msg = str( eval( config['MESSAGES']['turnx'][lang] + config['MESSAGES']['start_info'][lang] ) )
                turnmsg = await ctx.send(msg)
            else:
                take_init()
                msg = config['MESSAGES']['autoplay'][lang]
                await ctx.send(msg)
                #Global variables init and first move
                b, p = startstrategy()
                next_board = p
                board[b][p] = True
                gamefile_add(1, True, b, p, False)
                grid = add_mark(p, b, True, next_board)
                print('Start in central board')
                turn = player2
                count = 1
                boardmsg = await ctx.send(file = discord.File(grid))
                msg = str( eval( config['MESSAGES']['turno'][lang] ) )
                turnmsg = await ctx.send(msg)
        else:
            await ctx.reply( config['ERRORS']['errorfight'][lang] )
    else:
        await ctx.reply( config['ERRORS']['errorplayer'][lang] )

@client.command()
async def start(ctx, bigpos: int, pos: int):
    """ Places your mark, for the first move of the game ONLY
        Takes two arguments: <big cell number> -> Classic board you want to move in, must be an integer between 1 and 9
            <little cell number> -> Cell you want to move in (in the selected classic board), must be an integer between 1 and 9"""
    global lang
    global player1
    global player2
    global turn
    global count
    global ucount
    global boardmsg
    global turnmsg
    global gameOver
    global next_board
    global board
    global uboard
    global autoplay

    if not gameOver: #Check if a game is in progress
        
        if count == 0: #Check if this is the first move
            
            if player1 == ctx.author: #Check if the author is the first player
                
                if (0 < bigpos < 10) and (0 < pos < 10): #Check if the big board argument is valid
                        
                    mark = True
                    b = bigpos - 1 #pos is between [1,9] but board index starts from 0
                    p = pos - 1
                    next_board = p
                    board[b][p] = mark
                    
                    print(count)
                    print(ucount)
                    
                    #generate board
                    gamefile_add(1, True, b, p, False)
                    grid = add_mark(p, b, mark, next_board)
        
                    #Print the board & delete command and previous msg
                    await boardmsg.delete()
                    await turnmsg.delete()
                    await ctx.message.delete()

                    if autoplay != [False, True]:
                        turn = player2
                        count = 1
                        boardmsg = await ctx.send(file=discord.File(grid))
                        msg = str( eval( config['MESSAGES']['turno'][lang] ) )
                        turnmsg = await ctx.send(msg)
                    else:
                        turn = player1
                        count = 2
                        b = next_board
                        p = placestrategy(board, next_board, False, count)
                        print('Bot play at ' + str(p))
                        board[b][p] = False
                        next_board = p
                        gamefile_add(2, False, b, p, False)
                        grid = add_mark(p, b, False, next_board)
                        boardmsg = await ctx.send(file=discord.File(grid))
                        msg = str( eval( config['MESSAGES']['turnx'][lang] ) )
                        turnmsg = await ctx.send(msg)
                else:
                    await ctx.reply( config['ERRORS']['errorposition'][lang] )
            else:
                await ctx.reply( config['ERRORS']['errorturn'][lang] )
        else:
            await ctx.reply( config['ERRORS']['errorstart'][lang] )
    else:
        await ctx.reply( str( eval( config['ERRORS']['errorgameover'][lang] ) ) )

@client.command()
async def place(ctx, pos: int, callbybot = False):
    """ Places your mark (X or O), for all moves except the first one
        Takes one argument: <little cell number> -> Cell you want to move in (in the selected classic board), must be an integer between 1 and 9
        BOT automatically select and outlined the classic Tic-Tac-Toe board you are forced to move in"""
    global lang
    global player1
    global player2
    global turn
    global count
    global ucount
    global boardmsg
    global turnmsg
    global gameOver
    global next_board
    global board
    global uboard
    global autoplay
    
    if not gameOver: #Check if a game is in progress
        
        if count > 0: #Check if this is not the first move
            
            if turn == ctx.author or callbybot == True: #Check if the author is the right player
                
                if 0 < pos < 10 or callbybot == True:

                    if callbybot == False : p = pos - 1
                    else : p = pos
                    b = next_board
                    if board[b][p] == None: #Check if the cell is free
                        
                        #init mark
                        mark = (turn == player1)
                        if mark:
                            turn = player2
                        else:
                            turn = player1
                        
                        count += 1
                        board[b][p] = mark
                        next_board = changeNextBoard(board, p)

                        t = False
                        if uboard[b] == None and checkWinner(mark, board[b]):
                            uboard[b] = mark
                            ucount += 1
                            grid = add_mark(p, b, mark, next_board, False) #add little mark without saving grid because add big mark just after
                            grid = add_bigmark(b, mark, board[b])
                            t = True
                            if mark:
                                win = str( eval( config['MESSAGES']['cellwinx'][lang] ) )
                            else:
                                win = str( eval( config['MESSAGES']['cellwino'][lang] ) )
                            
                            await ctx.send(win) #this msg will stay in the channel
                            if autoplay != [False, False]: take_info(b)
                        else:
                            grid = add_mark(p, b, mark, next_board)

                        gamefile_add(count, mark, b, p, t)
                        print(count)
                        print(ucount)
                        
                        if checkWinner(mark, uboard): #Check for a Ultime Winner
                            await boardmsg.delete()
                            await turnmsg.delete()
                            await ctx.message.delete()
                            gameOver = True
                            boardmsg = await ctx.send(file=discord.File(grid))
                            autoplay = [False, False]
                            gamefile_add('winner', mark, 'winner', 'winner', 'winner') #add a row to know if there is a winner
                            os.remove("grid.png")
                            print('Game end by win')
                            if mark:
                                win_msg = str( eval( config['MESSAGES']['winner']['winx'][lang] ) )
                                win = discord.Embed(title = win_title , description = str(eval(winx)) , color = 0xf1c40f)
                                await ctx.send(embed = win) #this msg will stay in the channel
                            else:
                                win_msg = str( eval( config['MESSAGES']['winner']['wino'][lang] ) )
                            title = config['MESSAGES']['winner']['title'][lang]
                            win = discord.Embed(title = title , description = win_msg , color = 0xf1c40f)
                            await ctx.send(embed = win) #this msg will stay in the channel
                        
                        elif count >= 81 or ucount >= 9: #Check if all boards are full or big board is full
                            await boardmsg.delete()
                            await turnmsg.delete()
                            await ctx.message.delete()
                            gameOver = True
                            boardmsg = await ctx.send(file=discord.File(grid))
                            autoplay = [False, False]
                            os.remove("grid.png")
                            msg = str( eval( config['MESSAGES']['tie'][lang] ) )
                            await ctx.send(msg)

                        else: #Print the board & delete command and previous msg
                            if autoplay[1] and mark:
                                p = placestrategy(board, next_board, False, count)
                                print('Bot play at ' + str(p))
                                await place(ctx, p, True)
                            elif autoplay[0] and not mark:
                                p = placestrategy(board, next_board, True, count)
                                print('Bot play at ' + str(p))
                                await place(ctx, p, True)
                            else:
                                await boardmsg.delete()
                                await turnmsg.delete()
                                await ctx.message.delete()
                                boardmsg = await ctx.send(file=discord.File(grid))
                                if mark :
                                    msg = str( eval( config['MESSAGES']['turno'][lang] ) )
                                else :
                                    msg = str( eval( config['MESSAGES']['turnx'][lang] ) )
                                turnmsg = await ctx.send(msg)
                    else:
                        await ctx.reply( config['ERRORS']['errorplace'][lang] )
                else:
                    await ctx.reply( config['ERRORS']['errorposition'][lang] )
            else:
                await ctx.reply( config['ERRORS']['errorturn'][lang] )
        else:
            await ctx.reply( str( eval( config['MESSAGES']['start_info'][lang] ) ) )
    else:
        await ctx.reply( str( eval( config['ERRORS']['errorgameover'][lang] ) ) )
    
@client.command()
async def restorefight(ctx, p1: discord.Member, p2: discord.Member):
    """ Restores the fight corresponding to the attached csv game file
        Takes two arguments: <@player1> -> First player, he plays with X
            <@player2> -> Second player, he plays with O
        Players can be differents from the players who start the fight.
        For the moment, you can't restore a fight against the BOT!"""
    global lang
    global player1
    global player2
    global turn
    global count
    global ucount
    global boardmsg
    global turnmsg
    global gameOver
    global next_board
    global board
    global uboard
    global autoplay

    print(str(p1.id))
    print(str(p2.id))
    
    if len(ctx.message.attachments) != 0:
        
        if p1.id != p2.id: #Check if user don't try to play against himself
            
            if gameOver: #Check if a game is in progress
                
                if client.user.id != p1.id and client.user.id != p2.id:
                    autoplay = [False, False]
                    
                    attachment = ctx.message.attachments[0]
                    await attachment.save(str(attachment.filename))
                    name = attachment.filename
                    
                    if check_resume(name):

                        msg = config['MESSAGES']['wait'][lang]
                        waitmsg = await ctx.send(msg)
                        
                        #boards init
                        board = [[ None for _ in range(9)] for _ in range(9)]
                        uboard = [None for _ in range(9)]

                        #Global variables init
                        player1 = p1
                        player2 = p2
                        ucount = 0
                        gameOver = False
                        count = 0
                        next_board = None
                        
                        print('RESTORE AN OLD GAME')
                        
                        #generate board
                        gamefile_restore(name)
                        
                        try:
                            grid, count, ucount, mark, next_board = board_restore(board, uboard, name)
                        except ValueError as error:
                            msg = str( eval( config['ERRORS']['errorcorrupt'][lang] ) )
                            await ctx.reply(msg)
                            await waitmsg.delete()
                            #Varirables init
                            os.remove("grid.png")
                            player1 = ""
                            player2 = ""
                            turn = ""
                            count = 0
                            ucount = 0
                            boardmsg = None
                            turnmsg = None
                            gameOver = True
                            next_board = None
                            board = []
                            uboard = []
                            autoplay = [False, False]
                            return
                        
                        #Print the board & delete command msg
                        await ctx.message.delete()
                        await waitmsg.delete()
                        title = config['MESSAGES']['restore'][lang]
                        msg = str( eval( config['MESSAGES']['restore_msg'][lang] ) )
                        fightmsg = discord.Embed(title = title , description = msg, color = 0xf1c40f)
                        await ctx.send(embed = fightmsg) #this msg will stay in the channel
                        
                        boardmsg = await ctx.send(file = discord.File(grid))
                        if mark :
                            turn = player2
                            msg = str( eval( config['MESSAGES']['turno'][lang] ) )
                        else :
                            turn = player1
                            msg = str( eval( config['MESSAGES']['turnx'][lang] ) )
                        turnmsg = await ctx.send(msg)
                    else:
                        await ctx.reply( config['ERRORS']['errorrestore'][lang] )
                else:
                    await ctx.reply( config['ERRORS']['errorBOT'][lang] )
            else:
                await ctx.reply( config['ERRORS']['errorfight'][lang] )
        else:
            await ctx.reply( config['ERRORS']['errorplayer'][lang] )
    else:
        await ctx.reply( config['ERRORS']['errorattach'][lang] )

@client.command()
async def gamefile(ctx, video = 'no', v = 'fast'):
    """ Downloads the csv game file of the game in progress (or the last game if there isn't any game in progress)
        Takes two optionals arguments: 'video' -> Download the video of the game
            'fast' or 'slow' -> Choose between 1 or 2 fps (see makevideo command)
        By default video isn't downloaded"""
    global lang
    gamefile = get_filename()
    if gamefile != None:
        print('Game file download')
        await ctx.send(file = discord.File(gamefile))
        if video == 'video':
            waitmsg = await ctx.send("Please wait, BOT creates your video game file, it can take a long time.")
            
            copy(gamefile, "temp/")
            videoname = gamefile[0:-4] + ".avi"
            try:
                video = createvid(gamefile, videoname, v)
            except ValueError as error:
                await waitmsg.delete()
                msg = str( eval( config['ERRORS']['errorcorrupt'][lang] ) )
                await ctx.reply(msg)
                return
            except TypeError as err:
                await waitmsg.delete()
                msg = config['ERRORS']['errorfps'][lang]
                await ctx.reply(msg)
                return
            
            await ctx.send(file = discord.File(video))
            await waitmsg.delete()
            os.remove("temp/" + gamefile)
            os.remove("temp/" + str(videoname))
        await ctx.message.delete()
    else:
        await ctx.reply(config['ERRORS']['errorcsv'][lang])

@client.command()
async def makevideo(ctx, v = 'fast'):
    """ Creates a video with the attached csv game file
        Takes one optional argument: 'fast' or 'slow' ('fast' by default)
            'fast' -> 2 fps video
            'slow' -> 1 fps video"""
    global lang
    if len(ctx.message.attachments) != 0:
        attachment = ctx.message.attachments[0]
        name = str(attachment.filename)
        await attachment.save("temp/" + name)
        waitmsg = await ctx.send("Please wait, BOT creates your video game file, it can take a long time.")

        videoname = name[0:-4] + ".avi"
        try:
            video = createvid(name, videoname, v)
        except ValueError as error:
            await waitmsg.delete()
            msg = str( eval( config['ERRORS']['errorcorrupt'][lang] ) )
            await ctx.send(msg)
            return
        except TypeError:
            await waitmsg.delete()
            msg = config['ERRORS']['errorfps'][lang]
            await ctx.reply(msg)
            return
        
        await ctx.send(file = discord.File(video))
        await waitmsg.delete()
        await ctx.message.delete()
        os.remove("temp/" + name)
        os.remove("temp/" + str(videoname))
    else:
        await ctx.reply( config['ERRORS']['errorattach'][lang] )

@client.command()
async def end(ctx):
    """ Ends the game in progress
        Don't takes any arguments"""
    global lang
    global player1
    global player2
    global turn
    global count
    global ucount
    global boardmsg
    global turnmsg
    global gameOver
    global next_board
    global board
    global uboard
    global autoplay

    if not gameOver:
        #Delete previous msg
        await boardmsg.delete()
        await turnmsg.delete()
        os.remove("grid.png")
        print('Game end by force')

        #Varirables init
        player1 = ""
        player2 = ""
        turn = ""
        count = 0
        ucount = 0
        boardmsg = None
        turnmsg = None
        gameOver = True
        next_board = None
        board = []
        uboard = []
        autoplay = [False, False]
        
        #Print goodbye & the rules for the next fight
        title = config['MESSAGES']['force_end'][lang]
        msg = str( eval( config['ERRORS']['errorgameover'][lang] + config['MESSAGES']['download'][lang] ) )
        goodbye = discord.Embed(title = title , description = msg, color=0xe74c3c)
        await ctx.send(embed = goodbye)
        await ctx.message.delete()
    else:
        await ctx.message.delete()

@client.command()
async def rules(ctx):
    """ Displays the rules of Ultimate Tic Tac Toe
        (in the current language)
        Don't takes any arguments"""
    global lang
    title = config['MESSAGES']['rules']['title'][lang]
    msg = config['MESSAGES']['rules']['msg'][lang]
    rule = discord.Embed(title = title , description = msg, color = 0xe74c3c)
    await ctx.send(embed = rule)
    await ctx.message.delete()

@client.command()
async def language(ctx, language_prefix = 'list'):
    """ Changes the language of the BOT's messages
        Takes one argument: prefix of the new language (for example: 'en' or 'fr')
        Without argument, the command shows the list of implemented languages"""
    global lang
    global language_list
    if language_prefix in language_list: #if language l is implemented, switch to this language
        lang = language_prefix
        await ctx.message.delete()
    elif language_prefix == 'list':
        await ctx.send( str(language_list) )
        await ctx.message.delete()
    else:
        await ctx.reply( str( eval( config['ERRORS']['errorlanguage'][lang] ) ) )

@client.command()
async def pidor(ctx, arg = '0'):
    """ Use the command to see what it does
        Don't takes any arguments... I think"""
    title = "WHY <:M3_scarlet:829075217594449982> WILL WIN THE PI D'OR TOURNAMENT? <:pi_dor:590183398199263233>"
    msg = """ <:M3_scarlet:829075217594449982> M3 are the best, everybody knows !!! <:M3_scarlet:829075217594449982>
But if you want arguments, maybe you can add how many arguments you want :man_shrugging:"""
    if arg != '0':
        msg += """\n\nYou really need arguments?! :expressionless:
In my opinion you're not a real <:M3_scarlet:829075217594449982>!"""
    message = discord.Embed(title = title , description = msg, color=discord.Color.from_rgb(168, 10, 43))
    message.set_author(name="M. Rey", icon_url="https://cdn.discordapp.com/emojis/717657936763289631.png")
    await ctx.send(embed = message)
    await ctx.message.delete()

@language.error
async def language_error(ctx, error):
    print(error)
    language_prefix = "no language"
    await ctx.reply( str( eval( config['ERRORS']['errorlanguage'][lang] ) ) )

@restorefight.error
async def restorefight_error(ctx, error):
    print(error)
    await ctx.reply(error)
    
@gamefile.error
async def gamefile_error(ctx, error):
    print(error)
    await ctx.reply(error)

@makevideo.error
async def makevideo_error(ctx, error):
    print(error)
    await ctx.reply(error)

@fight.error
async def fight_error(ctx, error):
    global lang
    print(error)
    await ctx.reply( config['ERRORS']['errorplayer'][lang] )

@place.error
async def place_error(ctx, error):
    global lang
    print(error)
    await ctx.reply( config['ERRORS']['errorposition'][lang] )

@start.error
async def start_error(ctx, error):
    global lang
    print(error)
    await ctx.reply( config['ERRORS']['errorposition'][lang] )

client.run(token)
