from datetime import datetime as dt
import csv
import os
from boardcreation import empty_board, add_mark, add_bigmark, createvideo

winningConditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]] #Winning possibilities

filename = None

bo = [[ None for _ in range(9)] for _ in range(9)]
gb = [None for _ in range(9)]

n = 0
count = 0
nextb = None
mark = False

def gamefile_init(p1 : str, p2 : str):
    """ Init the game log file """
    global filename
    if filename != None: os.remove(filename)
    strdate = dt.today().strftime('%d_%m_%Y_@_%H_%M')
    filename = 'fight_' + p1 + '_' + p2 + '_' + strdate + '.csv'
    with open(filename, 'w', newline = '') as fichiercsv:
        gamefile = csv.writer(fichiercsv, delimiter = ';')
        gamefile.writerow(['Count', 'Mark', 'Big Cell', 'Little Cell', 'Cell Take'])

def gamefile_add(count, mark, b, p, t):
    """ Add a row in the game log file """
    global filename
    if mark:
        m = 'X'
    else:
        m = 'O'
    with open(filename, 'a', newline = '') as fichiercsv:
        gamefile = csv.writer(fichiercsv, delimiter = ';')
        gamefile.writerow([str(count), m, str(b), str(p), str(t)])

def gamefile_restore(name):
    """ Restore a game log file to complete it """
    global filename
    if filename != None: os.remove(filename)
    filename = name

def get_filename():
    return filename

def checkWinner(mark, grid):
    """ Check if player with mark won a board """
    global winningConditions
    for condition in winningConditions:
        if grid[condition[0]] == mark and grid[condition[1]] == mark and grid[condition[2]] == mark:
            return True
    return False

def changeNextBoard(grid, p):
    """ Return first free board starting from p """
    q = p
    for m in range(p, p + 9): #next_board is the first free board starting from the position p
        q = m % 9
        if None in grid[q]:
            return q

def createvid(name, videoname, v= 'fast'):
    """ Create a video game file with a csv game file, raise a ValueError if the file is corrupted """
    global bo
    global gb
    global n
    global count
    global nextb
    global mark
    rep = str(os.getcwd())
    os.chdir("temp/") #work in a different directory to not disturb game is progress

    if v == 'fast':
        ips = 2
    elif v == 'slow':
        ips = 1
    else:
        os.chdir(rep)
        raise TypeError
    
    bo = [[ None for _ in range(9)] for _ in range(9)]
    gb = [None for _ in range(9)]
    
    n = 0
    count = 0
    nextb = None
    mark = False
    
    with open(name, newline = '') as fichiercsv:
        fichier = csv.reader(fichiercsv, delimiter = ';')
        temp = []
        
        for row in fichier: #create temp list with rows after verication of the file's validity
            n += 1
            if row[0] == 'Count': #skip first row
                continue
            elif row[0] == 'winner': #skip winner row
                continue
            
            if row[1] == 'X' and mark == False: #init mark and check if the mark is the right one
                mark = True
            elif row[1] == 'O' and mark == True:
                mark = False
            else:
                os.chdir(rep)
                raise ValueError("Mark error, make sure mark column is an alternation between X and O") #If mark is not X or O, or if mark is X or O for 2 row in a row, the file is corrupted

            if len(row) != 5:
                os.chdir(rep)
                raise ValueError("Row " + str(n) + " is incomplete")
            try:
                c = int(row[0])
                b = int(row[2])
                p = int(row[3])
                t = eval(row[4])
            except: #If error, the file is corrupted
                os.chdir(rep)
                raise ValueError("Data in row " + str(n) + " is wrong")
            
            if c == count + 1: #If count is not continuous, the file is corrupted
                count = c
            else:
                os.chdir(rep)
                raise ValueError("Count error at row " + str(n))
            
            if b != nextb and nextb != None: #If big cell is not the next board, the file is corrupted
                os.chdir(rep)
                raise ValueError("Match error between next cell and big cell in the row " + str(n))
            
            bo[b][p] = mark
            nextb = changeNextBoard(bo, p)

            #If loop goes here, row is valid, add it to temp list
            r = [count, mark, b, p, t, nextb]
            
            if t:
                l = []
                for m in bo[b]: #copy bo[b]
                    if m:
                        l.append(True)
                    elif m == False:
                        l.append(False)
                    else:
                        l.append(None)
                r.append(l)
            else:
                r.append(None)
            temp.append(r)
        
        rlast = temp[-1]
        for _ in range(2):
            temp.append(rlast) #add 2 occurences of the last image
        
        #print(temp)

        createvideo(temp, videoname, ips)
        os.chdir(rep)
        return "temp/" + videoname

def check_resume(name):
    """ Check if the game corresponding to the csv file 'name' can be resumed """
    with open(name, "r") as file:
        for line in file:
            pass
    if line.startswith('winner'):
        return False
    else:
        return True

def board_restore(board, uboard, name):
    """ Restore a board from a csv game file, raise a ValueError if the file is corrupted """
    grid = empty_board(False)
    n = 0
    ucount = 0
    count = 0
    nextb = None
    mark = False
    
    with open(name, newline = '') as fichiercsv:
        fichier = csv.reader(fichiercsv, delimiter = ';')
        for row in fichier:
            n += 1
            if row[0] == 'Count': #skip first row
                continue
            elif row[0] == 'winner': #skip winner row
                continue
            
            if row[1] == 'X' and mark == False: #init mark and check if the mark is the right one
                mark = True
            elif row[1] == 'O' and mark == True:
                mark = False
            else:
                raise ValueError("Mark error, make sure mark column is an alternation between X and O") #If mark is not X or O, or if mark is X or O for 2 row in a row, the file is corrupted

            if len(row) != 5:
                raise ValueError("Row " + str(n) + " is incomplete")
            try:
                c = int(row[0])
                b = int(row[2])
                p = int(row[3])
                t = eval(row[4])
            except: #If error, the file is corrupted
                raise ValueError("Data in row " + str(n) + " is wrong")
            
            if c == count + 1: #If count is not continuous, the file is corrupted
                count = c
            else:
                raise ValueError("Count error at row " + str(n))

            if b != nextb and nextb != None: #If big cell is not the next board, the file is corrupted
                raise ValueError("Match error between next cell and big cell in the row " + str(n))
            
            board[b][p] = mark
            nextb = changeNextBoard(board, p)
            
            if t:
                uboard[b] = mark
                ucount += 1
                grid = add_mark(p, b, mark, nextb, False)
                grid = add_bigmark(b, mark, board[b], False)
            else:
                grid = add_mark(p, b, mark, nextb, False)
        
        if t: #repeat last line with saving !
            uboard[b] = mark
            ucount += 1
            grid = add_mark(p, b, mark, nextb, False)
            grid = add_bigmark(b, mark, board[b])
        else:
            grid = add_mark(p, b, mark, nextb)
        
        return grid, count, ucount, mark, nextb
