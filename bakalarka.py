import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Button
from matplotlib.widgets import Cursor
from matplotlib.offsetbox import TextArea, AnnotationBbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames

import mplcursors
import tilemapbase
tilemapbase.start_logging()
from functools import partial

global extent
global data1

cbpresent = False
cb = []

class Record:
    def __init__(self, time, lat, lon, hmsl, gspeed, crs, hacc):
        self.time = time
        self.lat = lat
        self.lon = lon
        self.hmsl = hmsl
        self.gspeed = gspeed
        self.crs = crs
        self.hacc = hacc

    def __str__(self):
        return str(self.time) + ';LAT;' + str(self.lat) + ';LON;' + str(self.lon) + ';HMSL;' + str(self.hmsl) + ";GSPEED;" + str(self.gspeed) + ';CRS;' + str(self.crs) + ';HACC;' + str(self.hacc) + '\n'

class Average:
    def load_data(self, accuracy):
        #data_path = askopenfilenames(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])
        data_path = ['C:\\Users\\PC\\Desktop\\sobota_log\\dole\\2021-04-10_08-52-05_gps.log', 'C:\\Users\\PC\\Desktop\\sobota_log\\dole\\2021-04-10_09-22-05_gps.log', 'C:\\Users\\PC\\Desktop\\sobota_log\\dole\\2021-04-10_15-06-16_gps.log']
        data = []
        for i in range(len(data_path)):
            data.append(pd.read_csv(data_path[i], names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';'))

        longdif = round(data[0]['LONGITUDE'].max()/accuracy)-round(data[0]['LONGITUDE'].min()/accuracy)
        latdif = round(data[0]['LATITUDE'].max()/accuracy)-round(data[0]['LATITUDE'].min()/accuracy)

        longmin = data[0]['LONGITUDE'].min()
        latmin = data[0]['LATITUDE'].min()

        arr = [[[] for x in range(longdif) ] for j in range(latdif)]

        for data in data:
            for i in range(len(data)):
                y = round(data['LONGITUDE'][i]/accuracy-longmin/accuracy)
                x = round(data['LATITUDE'][i]/accuracy-latmin/accuracy)
                
                r = Record(data['TIME'][i], data['LATITUDE'][i], data['LONGITUDE'][i], data['HMSL'][i], data['GSPEED'][i], data['CRS'][i], data['HACC'][i])
                try:
                    arr[x-1][y-1].append(r)
                except:
                    pass
        self.arr = arr
    
    def aver(self, rec):
        time = 'avg'
        lat = lon = hmsl = gspeed = crs = hacc = 0
        arr_len = len(rec)
        
        for i in range(arr_len):
            lat += rec[i].lat
            lon += rec[i].lon
            hmsl += rec[i].hmsl
            gspeed += rec[i].gspeed
            crs += rec[i].crs
            hacc += rec[i].hacc

        lat //= arr_len
        lon //= arr_len
        hmsl //= arr_len
        gspeed //= arr_len
        crs //= arr_len
        hacc //= arr_len

        lat, lon, hmsl, gspeed, crs, hacc = (x//arr_len for x in [lat, lon, hmsl, gspeed, crs, hacc])

        return Record(time, lat, lon, hmsl, gspeed, crs, hacc)

    def write_data(self):
        arr = self.arr

        f = open("C:\\Users\\PC\\Desktop\\averaged.txt", "w")

        for i in range(len(arr)):
            for y in range(len(arr[i])):
                if len(arr[i][y]) != 0:
                    record = self.aver(arr[i][y])
                    f.write(str(record))

        f.close()

def annot_format(sel, data):
    return "x: " + str(data['LONGITUDE'][sel.index]/10000000) + "\n" + \
    "y: " + str(data['LATITUDE'][sel.index]/10000000) + "\n" + \
    "altitude: " + str(round(data['HMSL'][sel.index]/1000, 2)) + "\n" + \
    "speed: " + str(round(data['GSPEED'][sel.index]*3.6/100, 2)) + "\n" + \
    "crs: " + str(round(data['CRS'][sel.index]/100000, 2)) + "\n" + \
    "accuracy: " + str(round(data['HACC'][sel.index], 2))

#17.0931,17.1057,48.1707,48.1824
def crtscatter(arr, color, data, ax, counter):
    points = [tilemapbase.project(x,y) for x,y in zip(data['LONGITUDE']/10000000, data['LATITUDE']/10000000)]
    x, y = zip(*points)

    sct = ax[counter].scatter(x, y, zorder=1, alpha= 0.2, c=color, cmap=mpl.cm.rainbow, s=30, visible=True, picker=True)
    arr.append(sct)

def hidecb():
    global cbpresent
    global cb

    if cbpresent == True:
        cb.remove()
        cbpresent = False

def generate_click(ax, radiobutton, labels, fig, event):
    #vyber suboru
    tkinter.Tk().withdraw()
    filename = askopenfilename(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])

    if not filename:
        print('You have to choose a file first!')
        return
    
    radiobutton.set_active(0)
    hidecb()
    
    try:
        data = pd.read_csv(filename, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';')
        # data = data.sample(len(data)//10) #zmensenie vzdorky
        # data.reset_index(drop=True, inplace=True) #reindexovanie aby fungoval index anotacii
        global data1
        data1=data
    except:
        print('zly file')
        return
    
    x1, x2, y1, y2 = bbset(data)

    #nastavenie colormapy
    color = ['Blue', data['HMSL'], data['GSPEED'], data['CRS'], data['HACC']]

    p = []
    counter = 0
    for i in color:
        crtscatter(p, i, data, ax, counter)
        counter += 1

    radiobutton.on_clicked(partial(radio_click, p, data, ax, labels))

    #mplcursors.cursor(ax, hover=True, highlight=0).connect("add", lambda sel: sel.annotation.set_text(annot_format(sel, data))) #tooltip
    #mplcursors.cursor(ax, hover=False, highlight=0).connect("add", lambda sel: fig.canvas.toolbar.set_message(annot_format(sel, data))) #tooltip
    
    #nastavenie hranic tabulky, formatovanie osi tabulky
    for i in range(len(p)):
        ax[i].set_title(labels[i])
        ax[i].set_xlim(x1, x2)
        ax[i].set_ylim(y1, y2)

        ax[i].yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
        ax[i].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
        ax[i].label_outer()

    extent = tilemapbase.Extent.from_lonlat(x1,x2,y1,y2)     #tu 4 veci <-----------------------------------------------
    t = tilemapbase.tiles.build_OSM()
    
    plotter = tilemapbase.Plotter(extent, t, width=50)
    for i in range(5):
        plotter.plot(ax[i])

    plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)
    plt.draw()

def radio_click(p, data, ax, labels, label):
    global cbpresent
    global cb

    for i in p:
        i.set_visible(False)

    i = labels.index(label)
    p[i].set_visible(True)

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

def check_click(labels, ax, fig, checkbox_status, label):
    i = labels.index(label)
    counter = 0

    if ax[i].get_visible():
        ax[i].set_visible(False)
        checkbox_status[i] = 0
    else:
        ax[i].set_visible(True)
        checkbox_status[i] = 1

    if checkbox_status.count(1) > 0:
        gs = gridspec.GridSpec(1, checkbox_status.count(1), height_ratios=[5])

    for j in range(len(checkbox_status)):
        if checkbox_status[j] == 1:
            ax[j].set_position(gs[counter].get_position(fig))
            counter += 1
        else:
            if checkbox_status.count(1) > 0:
                ax[j].set_position(gs[0].get_position(fig))

    plt.draw()

def average_click(event):
    average = Average()
    average.load_data(300)
    average.write_data()
    print("averaged")

#inicializacia dat
def bbset(data):
    #zistenie min a max hodnot lat,long hodnot z dat
    shiftx = (data['LONGITUDE'].max() - data['LONGITUDE'].min())/100000000
    shifty = (data['LATITUDE'].max() - data['LATITUDE'].min())/300000000

    bbox = (data['LONGITUDE'].min()/10000000, data['LONGITUDE'].max()/10000000, data['LATITUDE'].min()/10000000, data['LATITUDE'].max()/10000000)
    return bbox[0] - shiftx, bbox[1] + shiftx, bbox[2] - shifty, bbox[3] + shifty

def test(fig, event):
    i = event.ind[0]
    data = event.artist.get_offsets()
    xdata, ydata = data[i,:]
    print ("x: " + str(data1['LONGITUDE'][i]/10000000) + "\n" + \
    "y: " + str(data1['LATITUDE'][i]/10000000) + "\n" + \
    "altitude: " + str(round(data1['HMSL'][i]/1000, 2)) + "\n" + \
    "speed: " + str(round(data1['GSPEED'][i]*3.6/100, 2)) + "\n" + \
    "crs: " + str(round(data1['CRS'][i]/100000, 2)) + "\n" + \
    "accuracy: " + str(round(data1['HACC'][i], 2)))
    # fig.canvas.toolbar.set_message("x: " + str(data1['LONGITUDE'][i]/10000000) + "\n" + \
    # "y: " + str(data1['LATITUDE'][i]/10000000) + "\n" + \
    # "altitude: " + str(round(data1['HMSL'][i]/1000, 2)) + "\n" + \
    # "speed: " + str(round(data1['GSPEED'][i]*3.6/100, 2)) + "\n" + \
    # "crs: " + str(round(data1['CRS'][i]/100000, 2)) + "\n" + \
    # "accuracy: " + str(round(data1['HACC'][i], 2)))

def main():
    fig, ax = plt.subplots(1,5)

    fig.set_figheight(7)
    fig.set_figwidth(11)

    #fig.canvas.mpl_connect("motion_notify_event", lambda event: fig.canvas.toolbar.set_message(""))
    # cursor1 = Cursor(ax[0], horizOn=True, vertOn=True, useblit=False, color='r', linewidth=1)
    # cursor2 = Cursor(ax[1], horizOn=True, vertOn=True, useblit=True, color='r', linewidth=1)
    fig.canvas.mpl_connect('pick_event', partial(test, fig))
    #radiobuttons
    labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
    axRadioButton = plt.axes([0.01,0.5,0.15,0.15]) 
    radiobutton = RadioButtons(axRadioButton, labels)

    fig.text(1, 1, 'textbox', fontsize=10)

    checkbox_status = [1,1,1,1,1]
    axCheckButton = plt.axes([0.01,0.2,0.15,0.2]) 
    checkbox = CheckButtons(ax=axCheckButton, labels=labels, actives=checkbox_status)
    checkbox.on_clicked(partial(check_click, labels, ax, fig, checkbox_status))

    axButton1 = plt.axes([0.01,0.7,0.10,0.08]) 
    button1 = Button(axButton1, "Generate")
    button1.on_clicked(partial(generate_click, ax, radiobutton, labels, fig))

    axButton2 = plt.axes([0.12,0.7,0.10,0.08]) 
    button2 = Button(axButton2, "Average")
    button2.on_clicked(average_click)
    
    plt.subplots_adjust(left=0.3)
    plt.show()

if __name__ == '__main__':
    main()

