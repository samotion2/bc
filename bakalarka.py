import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import RadioButtons
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

def annot_format(sel, data, switch):
    if switch == 1:
        addition =  "\n" + "altitude: " + str(round(data['HMSL'][sel.index]/1000, 2))
    elif switch == 2:
        addition =  "\n" + "speed: " + str(round(data['GSPEED'][sel.index]*3.6/100, 2))
    elif switch == 3:
        addition =  "\n" + "crs: " + str(round(data['CRS'][sel.index]/100000, 2))
    elif switch == 4:
        addition =  "\n" + "accuracy: " + str(round(data['HACC'][sel.index], 2))
    else:
        addition = ""

    return "x: " + str(data['LONGITUDE'][sel.index]/10000000) + "\n" + \
    "y: " + str(data['LATITUDE'][sel.index]/10000000) + addition

#17.0931,17.1057,48.1707,48.1824
def crtscatter(arr, color, data, ax):
    points = [tilemapbase.project(x,y) for x,y in zip(data['LONGITUDE']/10000000, data['LATITUDE']/10000000)]
    x, y = zip(*points)

    sct = ax.scatter(x, y, zorder=1, alpha= 0.2, c=color, cmap=mpl.cm.rainbow, s=30, visible=False)
    arr.append(sct)

def generateclick(event):
    #vyber suboru
    tkinter.Tk().withdraw()
    filename = askopenfilename(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])
    #print(filename)
    
    if not filename:
        print('You have to choose a file first!')
    
    return filename

def radioclick(p, data, ax, switch, labels, label):
    global cbpresent
    global cb

    #print(label)
    #a.set_visible(not a.get_visible())
    for i in p:
        i.set_visible(False)

    i = labels.index(label)
    p[i].set_visible(True)
    switch[0] = i

    # if i > 0:
    #     cb.remove()

    if cbpresent == True:
        cb.remove()
        cbpresent = False

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
        data_path = '.\\averaged.txt'
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
    switch = [0]
    data_path, x1, x2, y1, y2, img_path = init(1) #1-koliba, 0-zilina

    #data_path = generateclick()
    
    try:
        data = pd.read_csv(data_path, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';')
    except:
        print('zly file')
        return
    #print(data.head())
    #bbset(data)
    
    x1, x2, y1, y2 = bbset(data)


    fig, ax = plt.subplots(figsize = (11,7))

    #nastavenie colormapy
    color = ['Blue', data['HMSL'], data['GSPEED'], data['CRS'], data['HACC']]
    p = []
    #p.append(ax.scatter(data['LONGITUDE']/10000000, data['LATITUDE']/10000000, zorder=1, alpha= 0.2, s=30, visible=True))
    for i in color:
        crtscatter(p, i, data, ax)

    p[0].set_visible(True)
    cursor = mplcursors.cursor(ax, hover=True) #tooltip
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set(text = annot_format(sel, data, switch[0]))

    #nastavenie hranic tabulky
    ax.set_title(data_path)
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)

    #formatovanie osi tabulky
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))

    #nacitanie mapy na pozadi
    # img = plt.imread(img_path)
    # ax.imshow(img, zorder= 0, extent = [x1, x2, y1, y2], aspect= 'equal')

    extent = tilemapbase.Extent.from_lonlat(x1,x2,y1,y2)     #tu 4 veci <-----------------------------------------------
    t = tilemapbase.tiles.build_OSM()
    
    plotter = tilemapbase.Plotter(extent, t, width=200)
    plotter.plot(ax)

    plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)

    #radiobuttons
    labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
    axCheckButton = plt.axes([0.01,0.5,0.15,0.15]) 
    checkbox = RadioButtons(axCheckButton, labels)

    axButton = plt.axes([0.01,0.7,0.10,0.08]) 
    button = Button(axButton, "Generate")

    checkbox.on_clicked(partial(radioclick, p, data, ax, switch, labels))
    button.on_clicked(generateclick)
    # print(data['HACC'].min())
    # print(data['HACC'].max())

    # print(data['HMSL']/1000)
    plt.show()

if __name__ == '__main__':
    main()

