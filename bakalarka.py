import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Button
from mpl_toolkits.axes_grid1 import make_axes_locatable

import tkinter
from tkinter.filedialog import askopenfilename

import mplcursors
import tilemapbase
tilemapbase.start_logging()
from functools import partial

global extent

cbpresent = False
cb = []

def annot_format(sel, data):
    return "x: " + str(data['LONGITUDE'][sel.index]/10000000) + "\n" + \
    "y: " + str(data['LATITUDE'][sel.index]/10000000) + "\n" + \
    "altitude: " + str(round(data['HMSL'][sel.index]/1000, 2)) + "\n" + \
    "speed: " + str(round(data['GSPEED'][sel.index]*3.6/100, 2)) + "\n" + \
    "crs: " + str(round(data['CRS'][sel.index]/100000, 2)) + "\n" + \
    "accuracy: " + str(round(data['HACC'][sel.index], 2))

#17.0931,17.1057,48.1707,48.1824
def crtscatter(arr, color, data, ax):
    points = [tilemapbase.project(x,y) for x,y in zip(data['LONGITUDE']/10000000, data['LATITUDE']/10000000)]
    x, y = zip(*points)

    sct = ax.scatter(x, y, zorder=1, alpha= 0.2, c=color, cmap=mpl.cm.rainbow, s=30, visible=False)
    arr.append(sct)

def hidecb():
    global cbpresent
    global cb

    if cbpresent == True:
        cb.remove()
        cbpresent = False


def generateclick(ax, radiobutton, labels, event):
    #vyber suboru
    tkinter.Tk().withdraw()
    filename = askopenfilename(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])

    if not filename:
        print('You have to choose a file first!')
        return
    
    radiobutton.set_active(0)
    hidecb()
    ax.clear()
    
    try:
        data = pd.read_csv(filename, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';')
    except:
        print('zly file')
        return
    
    x1, x2, y1, y2 = bbset(data)

    #nastavenie colormapy
    color = ['Blue', data['HMSL'], data['GSPEED'], data['CRS'], data['HACC']]

    p = []
    for i in color:
        crtscatter(p, i, data, ax)

    #print(p)
    p[0].set_visible(True)

    mplcursors.cursor(ax, hover=2).connect("add", lambda sel: sel.annotation.set_text(annot_format(sel, data))) #tooltip

    radiobutton.on_clicked(partial(radioclick, p, data, ax, labels))

    #nastavenie hranic tabulky
    ax.set_title(filename)
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)

    #formatovanie osi tabulky
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))

    extent = tilemapbase.Extent.from_lonlat(x1,x2,y1,y2)     #tu 4 veci <-----------------------------------------------
    t = tilemapbase.tiles.build_OSM()

    plotter = tilemapbase.Plotter(extent, t, width=200)
    plotter.plot(ax)

    plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)

def radioclick(p, data, ax, labels, label):
    global cbpresent
    global cb

    #print(label)
    #a.set_visible(not a.get_visible())
    for i in p:
        i.set_visible(False)

    i = labels.index(label)
    p[i].set_visible(True)

    # if i > 0:
    #     cb.remove()

    hidecb()

    if label == 'Speed':
        vmin=data['GSPEED'].min()*3.6/100
        vmax=data['GSPEED'].max()*3.6/100
    elif label == 'HACC':
        vmin=data['HACC'].min()
        vmax=data['HACC'].max()
    elif label == 'Altitude':
        vmin=data['HMSL'].min()/1000
        vmax=data['HMSL'].max()/1000
    elif label == "Course":
        vmin=data['CRS'].min()/100000
        vmax=data['CRS'].max()/100000
    else:
        plt.draw()
        return

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.rainbow)
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    v = np.linspace(vmin, vmax, 10, endpoint=True)
    cb = plt.colorbar(cmap, cax=cax, ticks=v)
    cbpresent = True

    plt.draw()

#print(cbpresent)
#inicializacia dat
def bbset(data):
    #zistenie min a max hodnot lat,long hodnot z dat
    shiftx = (data['LONGITUDE'].max() - data['LONGITUDE'].min())/100000000
    shifty = (data['LATITUDE'].max() - data['LATITUDE'].min())/300000000

    bbox = (data['LONGITUDE'].min()/10000000, data['LONGITUDE'].max()/10000000, data['LATITUDE'].min()/10000000, data['LATITUDE'].max()/10000000)
    return bbox[0] - shiftx, bbox[1] + shiftx, bbox[2] - shifty, bbox[3] + shifty

def init(i):
    if i==1:
        #data_path = '\\averaged.txt'
        data_path = 'C:\\Users\\PC\\Desktop\\averaged.txt'
        #data_path = '.\\sobota_log\\dole\\2021-04-10_08-52-05_gps.log'
        #data_path = '.\\nedela_log\\dole\\2021-04-11_13-36-28_gps.log'
        img_path = 'koliba.png'
        x1 = 17.0931
        x2 = 17.1057
        y1 = 48.1707
        y2 = 48.1824
    else:
        data_path = '2021-04-21_06-12-07_gps.log'
        #data_path = '2021-04-21_14-42-20_gps.log'
        img_path = 'zilina.png'
        x1 = 18.7295
        x2 = 18.7677
        y1 = 49.1976
        y2 = 49.2599

    return data_path, x1, x2, y1, y2, img_path

def main():
    fig, ax = plt.subplots(figsize = (11,7))

    #radiobuttons
    labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
    axRadioButton = plt.axes([0.01,0.5,0.15,0.15]) 
    radiobutton = RadioButtons(axRadioButton, labels)

    axCheckButton = plt.axes([0.01,0.2,0.15,0.2]) 
    checkbox = CheckButtons(axCheckButton, labels)

    axButton = plt.axes([0.01,0.7,0.10,0.08]) 
    button = Button(axButton, "Generate")

    button.on_clicked(partial(generateclick, ax, radiobutton, labels))
    
    plt.subplots_adjust(left=0.3)
    plt.show()

if __name__ == '__main__':
    main()

