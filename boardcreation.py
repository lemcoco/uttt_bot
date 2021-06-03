import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
#plt.rcParams['animation.ffmpeg_path'] = 'C:/Program Files/ffmpeg/bin/ffmpeg.exe' #your path to ffmpeg here on Windows !

import json
with open('config.json') as config_file:
    config = json.load(config_file)

mark_color = config['BOARD']['mark_color']
bigmark_color = config['BOARD']['big_mark_color']
last_mark_color = config['BOARD']['last_mark_color']
boardcolor = config['BOARD']['big_board_color']
cellcolor = config['BOARD']['little_board_color']
square = config['BOARD']['next_board_color']

upositions = [ #Centers of ultime board 's cells
    [0.45, 2.25], [1.35, 2.25], [2.25, 2.25],
    [0.45, 1.35], [1.35, 1.35], [2.25, 1.35],
    [0.45, 0.45], [1.35, 0.45], [2.25, 0.45]
]
rpositions = [ #relative position of cells from center of board
    [-0.3, +0.3], [+0.0, +0.3], [+0.3, +0.3],
    [-0.3, +0.0], [+0.0, +0.0], [+0.3, +0.0],
    [-0.3, -0.3], [+0.0, -0.3], [+0.3, -0.3]
]
last = [None, None, None]

tlist = np.linspace(0, 2*np.pi, 100)
big_radius = 0.3
lit_radius = 0.08
bigx = big_radius*np.cos(tlist)
bigy = big_radius*np.sin(tlist)
litx = lit_radius*np.cos(tlist)
lity = lit_radius*np.sin(tlist)

fig = plt.figure()

def empty_board(save = True):
    global last
    plt.cla()
    last = [None, None, None]
    for i in [0.9, 1.8]:
        plt.plot([i, i], [0, 2.7], color = boardcolor)
        plt.plot([0, 2.7], [i, i], color = boardcolor)
    l1 = [0.3, 0.6, 1.2, 1.5, 2.1, 2.4]
    for i in l1:
        for j in [0.1, 1, 1.9]:
            plt.plot([i, i], [j, j + 0.7], color = cellcolor)
            plt.plot([j, j + 0.7], [i, i], color = cellcolor)
    plt.axis('square')
    plt.axis(False)
    if save: plt.savefig('grid.png', bbox_inches='tight')
    return 'grid.png'

def add_mark_fix(p, z, mark):
    global upositions
    global rpositions
    global last
    cx, cy = upositions[z]
    px, py = rpositions[p]
    x = cx + px
    y = cy + py

    #Add mark
    if mark:
        plt.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color = mark_color, linewidth=2)
        plt.plot([x - 0.08, x + 0.08], [y + 0.08, y - 0.08], color = mark_color, linewidth=2)
    else:
        lx = [i + x for i in litx]
        ly = [i + y for i in lity]
        plt.plot(lx, ly, color = mark_color, linewidth=2)

def add_mark(p, z, mark, next_board, save = True):
    global upositions
    global rpositions
    global last
    cx, cy = upositions[z]
    px, py = rpositions[p]
    x = cx + px
    y = cy + py

    #Add mark
    if mark:
        plt.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color = last_mark_color, linewidth=1)
        plt.plot([x - 0.08, x + 0.08], [y + 0.08, y - 0.08], color = last_mark_color, linewidth=1)
    else:
        lx = [i + x for i in litx]
        ly = [i + y for i in lity]
        plt.plot(lx, ly, color = last_mark_color, linewidth=1)

    #Add mark
    if last[0] != None :
        add_mark_fix(last[0], last[1], last[2])
    last = [p, z, mark]

    #erase red on this board
    lcx = [cx - 0.40, cx + 0.40, cx + 0.40, cx - 0.40, cx - 0.40]
    lcy = [cy - 0.40, cy - 0.40, cy + 0.40, cy + 0.40, cy - 0.40]
    plt.plot(lcx, lcy, 'w', linewidth=3)

    #red on next board
    rx, ry = upositions[next_board]
    lrx = [rx - 0.40, rx + 0.40, rx + 0.40, rx - 0.40, rx - 0.40]
    lry = [ry - 0.40, ry - 0.40, ry + 0.40, ry + 0.40, ry - 0.40]
    plt.plot(lrx, lry, color = square)
    
    if save: plt.savefig('grid.png', bbox_inches='tight')
    return 'grid.png'


def add_bigmark(p, mark, board, save = True):
    global upositions
    x, y = upositions[p]
    if mark:
        plt.plot([x - 0.3, x + 0.3], [y - 0.3, y + 0.3], color = bigmark_color, linewidth=3)
        plt.plot([x - 0.3, x + 0.3], [y + 0.3, y - 0.3], color = bigmark_color, linewidth=3)
    else:
        lx = [i + x for i in bigx]
        ly = [i + y for i in bigy]
        plt.plot(lx, ly, color = bigmark_color, linewidth=3)

    for i in range(9):
        if board[i] != None:
            add_mark_fix(i, p, board[i])

    if save: plt.savefig('grid.png', bbox_inches='tight')
    return 'grid.png'

def creation(row):
    """ Update grid for each row """
    mark = row[1]
    b = row[2]
    p = row[3]
    t = row[4]
    nextb = row[5]
    boardb = row[6]
    
    grid = add_mark(p, b, mark, nextb, False)
    if t:
        grid = add_bigmark(b, mark, boardb, False)

def createvideo(temp, videoname, ips):
    """ Create video animation file with the temp list """
    fig = plt.figure()
    grid = empty_board(False)
    ani = FuncAnimation(fig, creation, frames = temp)
    writervideo = FFMpegWriter(fps = ips)
    ani.save(videoname, writer = writervideo)
    return
