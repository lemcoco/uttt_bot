import random
from datetime import datetime as dt
import csv
import os
from utils import checkWinner, winningConditions

nlim = [100, 82]

take = []

def randomcell(grid, checkfree = True):
    """ Choose a random free cell, if all cell are free in grid, please call with checkfree = False"""
    if checkfree:
        lst = [i for i in range(9) if grid[i] == None]
        p = random.choice(lst)
    else:
        p = random.choice(grid)
    return p

def take_info(b):
    """ Append b in the list of boards already take """
    global take
    take.append(b)
        
def take_init():
    """ Init list of boards already take """
    global take
    take = []

def good_pos(p):
    """ Return good position to allow win at next move in this board, regarding the cell p"""
    global winningConditions
    good = []
    condition_p = [condition for condition in winningConditions if p in condition] #all winning conditions contains p
    for cond in condition_p: #for all conditions contains p
        good += [m for m in cond if m != p] #add to goods_lst the two others positions to win with p
    return good

def last_pos(n, m):
    """ Look for the last position to win when n and m are already take by the same mark, return False if it's impossible to win with n and m"""
    global winningConditions
    condition_n = [condition for condition in winningConditions if n in condition] #all winning conditions contains n
    win = [condition for condition in condition_n if m in condition] #all winning conditions contains n and m
    if len(win) > 0:
        p = [i for i in win[0] if i != n and i != m]
        return p[0]
    else:
        return False

def goods(take_me, free = False):
    """ Return good positions regarding take_me list
        goods_lst contains many occurrences of some elements because these elements are good regarding several elements of take_me
        NB : that's list version of good_pos function """
    global winningConditions
    goods_lst = []
    for n in take_me:
        condition_n = [condition for condition in winningConditions if n in condition] #all winning conditions contains n
        for cond in condition_n: #for all conditions contains n
            goods_lst += [m for m in cond if m != n] #add to goods_lst the two others positions to win with n
    if free:
        goods_free = [n for n in goods_lst if n in free] #list of good and free positions
        return goods_free
    else:
        return goods_lst

def really_goods(take_me, free):
    """ Return positions allow win at next move in this board regarding take_me and free lists
        goods_lst contains many occurrences of some elements because these elements are good regarding several elements of take_me
        NB : that's list and developed version of good_pos function """
    global winningConditions
    goods_lst = []
    for n in take_me:
        condition_n = [condition for condition in winningConditions if n in condition] #all winning conditions contains n
        for cond in condition_n: #for all conditions contains n
            p, q = [m for m in cond if m != n] #list of the two others positions to win with n
            if p in free and q in free: #If the missing positions to win are free
                goods_lst.append(p)
                goods_lst.append(q)
    return goods_lst

def can_win(take_me, free = False):
    """ Return possibilites of win in one move when len(take_me) >= 2, if list free argument is != False, return only free position
        NB : that's list version of last_pos function  """
    global winningConditions
    win = []
    for i in range(len(take_me)):
        n = take_me[i]
        condition_n = [condition for condition in winningConditions if n in condition] #all winning conditions contains n
        for m in take_me[0:i] + take_me[i+1:]: #elements of take_me != n
            temp = [condition for condition in condition_n if m in condition] #all winning conditions contains n and m
            if temp != []: #if a win condition contains n and m
                p = [i for i in temp[0] if i != n and i != m][0] #take the missing position to win
                if p not in win:
                    win.append(p)
    if free:
        win_free = [n for n in win if n in free] #list possibilities of win where you can move
        return win_free
    else:
        return win
    
def startstrategy():
    """ Return board and place for the first move """
    b = 4 #always start in central board
    p = random.randint(0, 8)
    return b, p

def no_deep(board, b, mark):
    """ Strategy without looking at next possible move :
        -> If the board is already take : random choice
        -> If board is empty : random choice
        -> If BOT has one cell : choose in positions that allow win at next move in this board
        -> If BOT has more than two cells : choose the missing position to win, if it's free
        -> If opponent has one cell : choose in positions that allow win at next move in this board for him, to restrain his strategy
        -> If opponent has more than two cells : choose the missing position to win, if it's free, to restrain his strategy
        -> If none of these conditions are full, there isn't any win possibilites : choose randomly """
    global take
    
    localboard = list(board[b])
    opp_mark = not mark
    is_free = (b not in take) #True if no one already take this board
    
    free = [i for i in range(9) if localboard[i] == None]
    take_me = [i for i in range(9) if localboard[i] == mark]
    take_opp = [i for i in range(9) if localboard[i] == opp_mark]
    lfree = len(free)
    ltakeme = len(take_me)
    ltakeopp = len(take_opp)

    if lfree == 9 or not is_free: #if board is empty
        p = random.choice(free)
        print('Empty or already take board, random choice')
        return p

    #adopt this strategy only if board is not take
    if ltakeme >= 2: #If BOT already has more than two cells in the board
        win = can_win(take_me, free) #list possibilities of win in one move
        if win != []:
            p = random.choice(win)
            print('More than two places already take by me, win')
            return p
    if ltakeme >= 1: #If BOT has more than one cell in the board (if more than two, last if loop return before)
        good = really_goods(take_me, free)
        if good != []:
            p = random.choice(good)
            print('One place or more already take by me, random choice in good position')
            return p
    if ltakeopp >= 2:
        win = can_win(take_opp, free) #list possibilities of win in one move
        if win != []:
            p = random.choice(win)
            print('More than two places already take by opponent, block him')
            return p
    if ltakeopp >= 1: #If BOT has more than one cell in the board (if more than two, last if loop return before)
        good = really_goods(take_opp, free)
        if good != []:
            p = random.choice(good)
            print('One place or more already take by opponent, random choice in good position to block him')
            return p

    #If function reach this point, there isn't win possibilities and no good place : random choice
    print('None win possibilities or good positions : random choice')
    p = random.choice(free)
    return p

def rankingnextboard(board, temp, opp_mark, b, choice = False):
    """ Rank elements of temp in :
        -> Empty_lst : send opp to an empty board
        -> almostempty_lst : send opp to a board where he hasn't any cells
        -> notworst_lst : send opp to a board where he has only one cell
        -> notnotworst_lst : send opp to a board where he can't win directly
        if choice = True, function select randomly in the best list
        to use this function with temp as an int, call with lst = False"""
    empty_lst = []
    almostempty_lst = []
    notworst_lst = []
    notnotworst_lst = []
    
    for i in temp:
        temp_free = [] #List of free cells in the board i
        temp1 = [] #list of cells already take in the board i
        temp2 = [] #list of cells already take by the opponent in the board i
        for j in range(9):
            if i == b: #If play at i will send opponent in the board b, consider the cell i not free
                if board[i][j] == None and i != j: temp_free.append(j)
                else: temp1.append(j)
            else: 
                if board[i][j] == None: temp_free.append(j)
                else: temp1.append(j)
            if board[i][j] == opp_mark:
                temp2.append(j)
        if temp1 == []: #if the board i is empty
            empty_lst.append(i)
        if temp2 == []: #if opponent hasn't any cells in the board i
            almostempty_lst.append(i)
        elif len(temp2) == 1: #if opponent has one cell in the board i
            notworst_lst.append(i)
        elif len(temp2) >= 2 and can_win(temp2, temp_free) == []: #if opponent has more than two cell in the board i but he can't win with these cells
            notnotworst_lst.append(i)
    
    if choice:
        if empty_lst != []:
            p = random.choice(empty_lst)
            print('empty_lst')
            return p
        if almostempty_lst != []:
            p = random.choice(almostempty_lst)
            print('almostempty_lst')
            return p
        if notworst_lst != []:
            p = random.choice(notworst_lst)
            print('notworst_lst')
            return p
        if notnotworst_lst != []:
            p = random.choice(notnotworst_lst)
            print('notnotworst_lst)')
            return p
        print('None')
        return None
    else:
        return empty_lst, almostempty_lst, notworst_lst, notnotworst_lst

def deep_one(board, b, mark):
    """ No_deep function but all random.choice replace by an opponent possibilities exploration
        Strategy looking at next possible move :
        -> If the board is already take : look for optimal position to restrain opponent strategy at next move
        -> If board is empty : look for optimal position to restrain opponent strategy at next move
        -> If BOT has one cell : choose in positions that allow win at next move in this board
        -> If BOT has more than two cells : choose the missing position to win, if it's free
        -> If opponent has one cell : choose in positions that allow win at next move in this board for him, to restrain his strategy
        -> If opponent has more than two cells : choose the missing position to win, if it's free, to restrain his strategy
        -> If none of these conditions are full, there isn't any win possibilites : choose randomly """
    global take
    
    opp_mark = not mark
    is_free = (b not in take) #True if no one already take this board
    
    free = [i for i in range(9) if board[b][i] == None]
    take_me = [i for i in range(9) if board[b][i] == mark]
    take_opp = [i for i in range(9) if board[b][i] == opp_mark]
    lfree = len(free)
    ltakeme = len(take_me)
    ltakeopp = len(take_opp)

    if lfree == 9: #if board is empty
        print('lfree == 9:')
        temp = [i for i in free if i != b] #free without b boaard, because this board will not say free after this move LOL
        p = rankingnextboard(board, temp, opp_mark, b, choice = True)
        if p != None:
            return p
    
    if not is_free: #if board is already take
        print('not is_free:')
        p = rankingnextboard(board, free, opp_mark, b, choice = True)
        if p != None:
            return p

    #adopt this strategy only if board is not take
    if ltakeme >= 2: #If BOT already has more than two cells in the board
        win = can_win(take_me, free) #list possibilities of win in one move
        if win != []:
            print('ltakeme >= 2:')
            p = rankingnextboard(board, win, opp_mark, b, choice = True)
            if p != None:
                return p
    if ltakeme >= 1: #If BOT has more than one cell in the board (if more than two, last if loop return before)
        good = really_goods(take_me, free)
        if good != []:
            print('ltakeme >= 1:')
            p = rankingnextboard(board, good, opp_mark, b, choice = True)
            if p != None:
                return p
    if ltakeopp >= 2:
        win = can_win(take_opp, free) #list possibilities of win in one move
        if win != []:
            print('ltakeopp >= 2')
            p = rankingnextboard(board, win, opp_mark, b, choice = True)
            if p != None:
                return p
    if ltakeopp >= 1: #If BOT has more than one cell in the board (if more than two, last if loop return before)
        good = really_goods(take_opp, free)
        if good != []:
            print('ltakeopp >= 1:')
            p = rankingnextboard(board, good, opp_mark, b, choice = True)
            if p != None:
                return p

    #If function reach this point, there isn't win possibilities and no good place : look at next move
    print('None !')
    p = rankingnextboard(board, free, opp_mark, b, choice = True)
    if p != None:
        return p
    else:
        print('random choice:')
        p = random.choice(free)
        return p

def placestrategy(board, b, mark, count):
    """ Choose strategy within the count """
    #if count < nlim[0]:
    #print('Deep one method chosen')
    p = deep_one(board, b, mark)
    return p

