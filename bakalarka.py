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

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# global data1
# cbpresent = False
# cb = []

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
        self.fig, self.ax = plt.subplots(len(files),5)
        fig, ax = self.fig, self.ax
        self.data = files

        fig.set_figheight(7)
        fig.set_figwidth(11)

        fig.canvas.mpl_connect('pick_event',self.map_click)
        fig.canvas.mpl_connect("motion_notify_event", self.hover)
        
        #radiobuttons
        self.labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
        labels = self.labels
        axRadioButton = plt.axes([0.01,0.5,0.15,0.15]) 
        self.radiobutton = RadioButtons(axRadioButton, self.labels)

        #fig.text(1, 1, 'textbox', fontsize=10)

        self.checkbox_status = [1,1,1,1,1]
        checkbox_status = self.checkbox_status
        axCheckButton = plt.axes([0.01,0.2,0.15,0.2]) 
        checkbox = CheckButtons(ax=axCheckButton, labels=labels, actives=checkbox_status)
        checkbox.on_clicked(self.check_click)

        axButton1 = plt.axes([0.01,0.7,0.10,0.08]) 
        button1 = Button(axButton1, "Generate")
        button1.on_clicked(self.generate_click)

        axButton2 = plt.axes([0.12,0.7,0.10,0.08]) 
        button2 = Button(axButton2, "Average")
        button2.on_clicked(average_click)

        plt.subplots_adjust(left=0.3)
        plt.show()
    
    def txt(self):
        return ("x: " + "\n" + "y: " + "\n" + "altitude: " + "\n" + "speed: " + "\n" + "crs: " + "\n" + "accuracy: ")

    def hover(self, event): #mozno pridat nejaky sleep aby to nelagovalo
        self.fig.canvas.toolbar.set_message(self.txt())
        # ax = self.ax
        # if event.inaxes in [ax[0], ax[1], ax[2], ax[3], ax[4]] and ax[0].collections: #nefunguje pre posledny 
        #     for axx in [ax[0], ax[1], ax[2], ax[3], ax[4]]:
        #         cont, ind = axx.collections[0].contains(event)
        #         #print(cont, ind)
        #         if cont and ind:
        #             print('ano')
        #             #self.fig.canvas.toolbar.set_message(self.annot_format(ind['ind'][0]))
        #             #print(self.annot_format(ind['ind'][0]))

    def generate_click(self, event):
        data = self.data
        ax = self.ax
        labels = self.labels
        #print(data['LONGITUDE'][0])

        # figg = make_subplots(rows=3, cols=5, shared_xaxes=True, shared_yaxes=True)

        # for j in range(1,4):
        #     for i in range(1,6):
        #         figg.add_trace(go.Scatter(x=data['LONGITUDE']/10000000, y=data['LATITUDE']/10000000), row=j, col=i)

        # figg.show()
        
        # for y in range(i*j):
        #     figg.data[y].update(hovertemplate=self.annot_format(3))

        #figg.update_layout(height=600, width=800, title_text="Side By Side Subplots")
        
        # figg = px.scatter_mapbox(data, lon=data['LONGITUDE']/10000000, lat=data['LATITUDE']/10000000, color="GSPEED", title="A Plotly Express Figure")
        # figg.update_layout(mapbox_style="open-street-map")
        tmp = self.bbset()
        x1 = []
        x2 = []
        y1 = []
        y2 = []

        for i in range(len(tmp)):
            x1.append(tmp[i][0])
            x2.append(tmp[i][1])
            y1.append(tmp[i][2])
            y2.append(tmp[i][3])
        #print(x1)
        
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

        #self.radiobutton.on_clicked(partial(radio_click, p, data, ax, labels))
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
            plotter.append(tilemapbase.Plotter(extent, t, width=50))
        
        for y in range(len(data)):
            for i in range(5):
                plotter[y].plot(ax[y][i])
                #plotter.plot(ax[1][i])

        plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)
        plt.draw()

    def map_click(self, event):
        i = event.ind[0]
        pnts = event.artist.get_offsets()
        xdata, ydata = pnts[0,:]
        
        for z in range(len(self.data)):
            points = [tilemapbase.project(x,y) for x,y in zip(self.data[z]['LONGITUDE']/10000000, self.data[z]['LATITUDE']/10000000)]
            x, y = zip(*points)

            if x[0] == xdata and y[0] ==ydata:
                print(x[0], xdata, y[0], ydata)
                break

        print(self.annot_format(i, z))
        self.fig.canvas.toolbar.set_message(self.annot_format(i, z)) #------------------------------------TU ZMENIT

    def annot_format(self, i, y):
        return ("x: " + str(self.data[y]['LONGITUDE'][i]/10000000) + "\n" + \
        "y: " + str(self.data[y]['LATITUDE'][i]/10000000) + "\n" + \
        "altitude: " + str(round(self.data[y]['HMSL'][i]/1000, 2)) + "\n" + \
        "speed: " + str(round(self.data[y]['GSPEED'][i]*3.6/100, 2)) + "\n" + \
        "crs: " + str(round(self.data[y]['CRS'][i]/100000, 2)) + "\n" + \
        "accuracy: " + str(round(self.data[y]['HACC'][i], 2)))

    def bbset(self):
        data = self.data
        #zistenie min a max hodnot lat,long hodnot z dat
        bb = []
        for i in range(len(data)):
            shiftx = (data[i]['LONGITUDE'].max() - data[i]['LONGITUDE'].min())/100000000
            shifty = (data[i]['LATITUDE'].max() - data[i]['LATITUDE'].min())/300000000

            bbox = (data[i]['LONGITUDE'].min()/10000000, data[i]['LONGITUDE'].max()/10000000, data[i]['LATITUDE'].min()/10000000, data[i]['LATITUDE'].max()/10000000)
            bb.append((bbox[0] - shiftx, bbox[1] + shiftx, bbox[2] - shifty, bbox[3] + shifty))
        return bb

    def crtscatter(self, arr, color, i, counter):
        points = [tilemapbase.project(x,y) for x,y in zip(self.data[i]['LONGITUDE']/10000000, self.data[i]['LATITUDE']/10000000)]
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
            gs = gridspec.GridSpec(len(self.data), checkbox_status.count(1))

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
        tkinter.Tk().withdraw()
        filenames = askopenfilenames(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])

        if not filenames:
            print('You have to choose a file first!')
            return
        
        #self.radiobutton.set_active(0)
        #hidecb()
        
        try:
            files = []
            for file in filenames:
                files.append(pd.read_csv(file, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';'))
            # data = data.sample(len(data)//10) #zmensenie vzdorky
            # data.reset_index(drop=True, inplace=True) #reindexovanie aby fungoval index anotacii
            return files
        except:
            print('zly file')
            return

def hidecb():
    global cbpresent
    global cb

    if cbpresent == True:
        cb.remove()
        cbpresent = False

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


def average_click(event):
    average = Average()
    average.load_data_avg(300)
    average.write_data()
    print("averaged")

if __name__ == '__main__':
    data = load_data()
    Window(data)
