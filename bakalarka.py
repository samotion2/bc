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
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames
import mplcursors
from functools import partial
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import json
import seaborn as sb
import tilemapbase
tilemapbase.start_logging()

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
    def load_data_avg(self, accuracy):
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

class Window:
    def __init__(self, files):
        self.number_of_file = len(files)
        self.fig, self.ax = plt.subplots(self.number_of_file, 5, squeeze=False, sharex='row', sharey='row', gridspec_kw = {'wspace':0.025, 'hspace':0.05})
        fig, ax = self.fig, self.ax
        self.data = files

        fig.set_figheight(7)
        fig.set_figwidth(11)

        fig.canvas.mpl_connect('pick_event',self.map_click)
        fig.canvas.mpl_connect("motion_notify_event", self.hover)
        
        self.labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
        labels = self.labels

        self.checkbox_status = [1,1,1,1,1]
        checkbox_status = self.checkbox_status
        axCheckButton = plt.axes([0.01,0.3,0.15,0.2])
        checkbox = CheckButtons(ax=axCheckButton, labels=labels, actives=checkbox_status)
        checkbox.on_clicked(self.check_click)

        axButton3 = plt.axes([0.03,0.6,0.11,0.1]) 
        button3 = Button(axButton3, "Correlation")
        button3.on_clicked(self.correlation_click)

        self.generate_plot()

        plt.subplots_adjust(left=0.22)
        plt.show()
    
    def txt(self):
        return ("x: " + "\n" + "y: " + "\n" + "altitude: " + "\n" + "speed: " + "\n" + "crs: " + "\n" + "accuracy: ")

    def hover(self, event):
        self.fig.canvas.toolbar.set_message(self.txt())
        ax = self.ax
        
        for i in range(self.number_of_file):
            if event.inaxes in [ax[i][0], ax[i][1], ax[i][2], ax[i][3], ax[i][4]] and ax[i][0].collections: 
                for axx in [ax[i][0], ax[i][1], ax[i][2], ax[i][3], ax[i][4]]:
                    cont, ind = axx.collections[0].contains(event)
                    #print(cont, ind)
                    if cont and ind:
                        #print('ano')
                        self.fig.canvas.toolbar.set_message(self.annot_format(ind['ind'][0], i))
                        #print(self.annot_format(ind['ind'][0]))

    def correlation_click(self, event):
        data = self.data #todo spravit average zo vsetkych teraz ide iba pre jeden!!!!!!!!!!!!!!!!!!!!!!!!!
        print(data)

        fig2, ax2 = plt.subplots(nrows=1, ncols=3) # two axes on figure

        attributes = ['LONGITUDE', 'GSPEED', 'HMSL']
        cursors = []

        for i in range(len(attributes)):
            attr = attributes[i]
            ax2[i].scatter(data[0]['HACC'], data[0][attr])
            ax2[i].set_title(attr)
            cursors.append(mplcursors.cursor(ax2[i], hover=True))

        cursors[0].connect("add", self.cursor_annot1)
        cursors[1].connect("add", self.cursor_annot2)
        cursors[2].connect("add", self.cursor_annot3)
        
        self.cursors = cursors

        fig3, ax3 = plt.subplots()
        corr = data[0].corr()
        sb.heatmap(corr, cmap="Blues", annot=True)

        plt.show()

    def cursor_annot1(self, sel):
        sel.annotation.set_text('HACC: {}\nLONGITUDE: {}\nindex: {}'.format(sel.target[0], sel.target[1], sel.index))

        for s in self.cursors[1].selections:
            self.cursors[1].remove_selection(s)

        for s in self.cursors[2].selections:
            self.cursors[2].remove_selection(s)

    def cursor_annot2(self, sel):
        sel.annotation.set_text('HACC: {}\nGSPEED: {}\nindex: {}'.format(sel.target[0], sel.target[1], sel.index))
        
        for s in self.cursors[0].selections:
            self.cursors[0].remove_selection(s)

        for s in self.cursors[2].selections:
            self.cursors[2].remove_selection(s)

    def cursor_annot3(self, sel):
        sel.annotation.set_text('HACC: {}\nHMSL: {}\nindex: {}'.format(sel.target[0], sel.target[1], sel.index))
        
        for s in self.cursors[0].selections:
            self.cursors[0].remove_selection(s)

        for s in self.cursors[1].selections:
            self.cursors[1].remove_selection(s)

    def generate_plot(self):
        data = self.data
        ax = self.ax
        labels = self.labels

        bb = self.bbset()
        x1 = []
        x2 = []
        y1 = []
        y2 = []

        for i in range(len(bb)):
            x1.append(bb[i][0])
            x2.append(bb[i][1])
            y1.append(bb[i][2])
            y2.append(bb[i][3])
        
        #nastavenie colormapy
        color = []
        for i in range(len(data)):
            color.append(('Blue', data[i]['HMSL'], data[i]['GSPEED'], data[i]['CRS'], data[i]['HACC']))

        p = [[0 for x in range(5)] for y in range(len(data))] 
        counter = 0
        
        for i in range(len(color)):
            for clr in color[i]:
                #print(i)
                self.crtscatter(p[i], clr, i, counter)
                counter += 1
            counter = 0
        
        #nastavenie hranic tabulky, formatovanie osi tabulky
        for y in range(len(data)):
            for i in range(len(p[0])):
                ax[y][i].set_title(labels[i])
                ax[y][i].set_xlim(x1[y], x2[y])
                ax[y][i].set_ylim(y1[y], y2[y])

                ax[y][i].yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
                ax[y][i].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))
                ax[y][i].label_outer()
        
        plotter = []
        for i in range(len(data)):
            extent = tilemapbase.Extent.from_lonlat(x1[i],x2[i],y1[i],y2[i])
            t = tilemapbase.tiles.build_OSM()
            plotter.append(tilemapbase.Plotter(extent, t, width=100))
        
        for y in range(len(data)):
            for i in range(5):
                plotter[y].plot(ax[y][i])

        self.fig.canvas.toolbar.update()
        plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)

    def map_click(self, event):
        i = event.ind[0]
        pnts = event.artist.get_offsets()
        xdata, ydata = pnts[0,:]
        
        for z in range(len(self.data)):
            points = [tilemapbase.project(x,y) for x,y in zip(self.data[z]['LONGITUDE'], self.data[z]['LATITUDE'])]
            x, y = zip(*points)

            if x[0] == xdata and y[0] ==ydata:
                #print(x[0], xdata, y[0], ydata)
                break

        print(self.annot_format(i, z))
        self.fig.canvas.toolbar.set_message(self.annot_format(i, z))

    def annot_format(self, i, y):
        return ("x: " + str(self.data[y]['LONGITUDE'][i]) + "\n" + \
        "y: " + str(self.data[y]['LATITUDE'][i]) + "\n" + \
        "altitude: " + str(round(self.data[y]['HMSL'][i]/1000, 2)) + "\n" + \
        "speed: " + str(round(self.data[y]['GSPEED'][i]*3.6/100, 2)) + "\n" + \
        "crs: " + str(round(self.data[y]['CRS'][i], 2)) + "\n" + \
        "accuracy: " + str(round(self.data[y]['HACC'][i], 2)))

    def bbset(self):
        data = self.data
        #zistenie min a max hodnot lat,long hodnot z dat
        bb = []
        for i in range(len(data)):
            shiftx = (data[i]['LONGITUDE'].max() - data[i]['LONGITUDE'].min())/10
            shifty = (data[i]['LATITUDE'].max() - data[i]['LATITUDE'].min())/10

            bbox = (data[i]['LONGITUDE'].min(), data[i]['LONGITUDE'].max(), data[i]['LATITUDE'].min(), data[i]['LATITUDE'].max())
            bb.append((bbox[0] - shiftx, bbox[1] + shiftx, bbox[2] - shifty, bbox[3] + shifty))
        return bb

    def crtscatter(self, arr, color, i, counter):
        points = [tilemapbase.project(x,y) for x,y in zip(self.data[i]['LONGITUDE'], self.data[i]['LATITUDE'])]
        x, y = zip(*points)

        sct = self.ax[i][counter].scatter(x, y, zorder=1, alpha= 0.2, c=color, cmap=mpl.cm.rainbow, s=30, visible=True, picker=True)
        arr[counter] = sct

    def check_click(self, label):
        i = self.labels.index(label)
        counter = 0
        ax, fig, checkbox_status = self.ax, self.fig, self.checkbox_status

        for y in range(len(self.data)):
            if ax[y][i].get_visible():
                ax[y][i].set_visible(False)
                checkbox_status[i] = 0
            else:
                ax[y][i].set_visible(True)
                checkbox_status[i] = 1

        if checkbox_status.count(1) > 0:
            gs = gridspec.GridSpec(len(self.data), checkbox_status.count(1), wspace=0.025, hspace=0.05)

        for y in range(len(self.data)):
            for j in range(len(checkbox_status)):
                if checkbox_status[j] == 1:
                    ax[y][j].set_position(gs[y, counter].get_position(fig))
                    counter += 1
                else:
                    if checkbox_status.count(1) > 0:
                        ax[y][j].set_position(gs[y, 0].get_position(fig))
            counter = 0

        plt.draw()

def load_data():
        #vyber suboru
        tk.Tk().withdraw()
        filenames = askopenfilenames(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])

        if not filenames:
            print('You have to choose a file first!')
            return
        
        try:
            files = []
            counter = 0
            for file in filenames:
                #files.append(pd.read_csv(file, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';')) #old format
                files.append(json_to_df(file))

                files[counter] = files[counter].sample(len(files[counter])//10) #zmensenie vzdorky
                files[counter].reset_index(drop=True, inplace=True) #reindexovanie aby fungoval index anotacii
                counter+=1

            return files
        except:
            print('Vybrany subor alebo subory su v zlom formate')
            return

def json_to_df(filename):
    logs = []
    print(filename)
    for line in open(filename, 'r'):
        logs.append(json.loads(line))

    time = lat = lon = hmsl = gspeed = crs = hacc = None

    #tvar noveho dataframu
    data = {'LATITUDE':[],
            'LONGITUDE':[],
            'HMSL':[],
            'GSPEED':[],
            'CRS':[],
            'HACC':[]}

    for line in logs:
        #rozdelenie riadkov
        if 'lon' in line:
            lat = line['lat']
            lon = line['lon']
            hmsl = line['hMSL']
            hacc = line['hAcc']
        elif 'speed' in line:
            speed = line['speed']
            crs = line['heading']
        #ak mame vsetky data vytvorime zaznam do buduceho df
        if lat and lon and hmsl and hacc and speed and crs:
            data['LATITUDE'].append(lat)
            data['LONGITUDE'].append(lon)
            data['HMSL'].append(hmsl)
            data['HACC'].append(hacc)
            
            data['GSPEED'].append(speed)
            data['CRS'].append(crs)
            
            time = lat = lon = hmsl = gspeed = crs = hacc = None

    #vytvorime samotny df
    df = pd.DataFrame(data)
    return df
    #print(df)

def init_average_click():
    average = Average()
    average.load_data_avg(300)
    average.write_data()
    print("averaged")

def init_generate_click():
    data = load_data()
    if data:
        Window(data)

def placeholder():
    print('placeholder_func')

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('300x200')
    root.resizable(False, False)
    root.title('Analyzator')

    # exit button
    generate_button = ttk.Button(root, text='Generate', command=lambda: init_generate_click())
    average_button = ttk.Button(root, text='Average', command=lambda: init_average_click())
    old_format_button = ttk.Button(root, text='Old To New', command=lambda: placeholder())

    generate_button.pack(ipadx=5, ipady=6, expand=True)
    average_button.pack(ipadx=5, ipady=4, expand=True)
    old_format_button.pack(ipadx=5, ipady=4, expand=True)

    root.mainloop()
