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
import json
import seaborn as sb
import tilemapbase

tilemapbase.start_logging()

#format dat zaznamov
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
    def load_data_avg(self, accuracy, data):
        #rozdiel najmensej a najvacsej suradnice
        longdif = round(data[0]['LONGITUDE'].max()/accuracy*10000000)-round(data[0]['LONGITUDE'].min()/accuracy*10000000)
        latdif = round(data[0]['LATITUDE'].max()/accuracy*10000000)-round(data[0]['LATITUDE'].min()/accuracy*10000000)

        longmin = data[0]['LONGITUDE'].min()*10000000
        latmin = data[0]['LATITUDE'].min()*10000000

        arr = [[[] for x in range(longdif) ] for j in range(latdif)]

        for data in data:
            for i in range(len(data)):
                y = round(data['LONGITUDE'][i]*10000000/accuracy-longmin/accuracy)
                x = round(data['LATITUDE'][i]*10000000/accuracy-latmin/accuracy)
                
                #vytvorenie zaznamu a ulozenie do pola
                r = Record('avg', data['LATITUDE'][i], data['LONGITUDE'][i], data['HMSL'][i], data['GSPEED'][i], data['CRS'][i], data['HACC'][i])
                try:
                    arr[x-1][y-1].append(r)
                except:
                    print('error')
                    pass
        self.arr = arr
        #print(arr)
    
    #spriemerovanie dat jedneho vyseku
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

        lat, lon, hmsl, gspeed, crs, hacc = (x/arr_len for x in [lat, lon, hmsl, gspeed, crs, hacc])

        return Record(time, lat, lon, hmsl, gspeed, crs, hacc)

    #vytvorenie df zo spriemerovanych zaznamov
    def get_data(self):
        arr = self.arr

        test = []
        for i in range(len(arr)):
            for y in range(len(arr[i])):
                if len(arr[i][y]) != 0:
                    record = self.aver(arr[i][y])
                    test.append(record)

        df = pd.DataFrame([o.__dict__ for o in test])
        df = df.drop(columns=['time'])
        df.rename(columns={'lat': 'LATITUDE', 'lon': 'LONGITUDE', 'hmsl': 'HMSL', 'gspeed': 'GSPEED', 'crs': 'CRS', 'hacc': 'HACC'}, inplace=True)
        
        return df

#classa zodpovedajuca za vytvorenie a vykreslenie nacitanych dat
class Window:
    def __init__(self, files, filenames):
        self.filenames = filenames
        self.number_of_file = len(files)

        #vytvorenie subplotov posla poctu validnych vstupnych suborov
        self.fig, self.ax = plt.subplots(self.number_of_file, 5, squeeze=False, sharex='row', sharey='row', gridspec_kw = {'wspace':0.025, 'hspace':0.05})
        fig, ax = self.fig, self.ax
        self.data = files

        #odrezanie cesty suborov kvoli prehladnoti mien
        short_filenames = []
        for name in filenames:
            short_filenames.append(name.split('/')[-1])

        #format mien suborov
        rows = ['{}'.format(row) for row in short_filenames]
        pad = 5
        for axes, row in zip(ax[:,0], rows):
            axes.annotate(row, xy=(0, 0.5), xytext=(-axes.yaxis.labelpad - pad, 0),
            xycoords=axes.yaxis.label, textcoords='offset points',
            size=6, ha='right', va='center', rotation=90)

        fig.set_figheight(7)
        fig.set_figwidth(11)

        #prepojenie listenerov na hover a click
        fig.canvas.mpl_connect('pick_event',self.map_click)
        fig.canvas.mpl_connect("motion_notify_event", self.hover)
        
        #vytvorenie tlacidiel a ich formatovanie
        self.labels = ['GPS', 'Altitude', 'Speed', 'Course', 'HACC']
        labels = self.labels

        axRadioButton = plt.axes([0.01,0.5,0.15,0.15]) 
        self.radiobutton = RadioButtons(axRadioButton, list(range(1, len(files) + 1)))

        self.checkbox_status = [1,1,1,1,1]
        checkbox_status = self.checkbox_status
        axCheckButton = plt.axes([0.01,0.2,0.15,0.2])
        checkbox = CheckButtons(ax=axCheckButton, labels=labels, actives=checkbox_status)
        checkbox.on_clicked(self.check_click)

        axButton3 = plt.axes([0.03,0.7,0.11,0.1]) 
        button3 = Button(axButton3, "Correlation")
        button3.on_clicked(self.correlation_click)

        #samotna generacia grafov
        self.generate_plot()

        plt.subplots_adjust(left=0.3)
        plt.get_current_fig_manager().set_window_title('Visualization')
        plt.show()
    
    #format vypisu dat
    def txt(self):
        return ("x: " + "\n" + "y: " + "\n" + "altitude: " + "\n" + "speed: " + "\n" + "crs: " + "\n" + "accuracy: ")

    #zobrazeni annotacie na toolbare pri akcii hover
    def hover(self, event):
        self.fig.canvas.toolbar.set_message(self.txt())
        ax = self.ax
        
        for i in range(self.number_of_file):
            if event.inaxes in [ax[i][0], ax[i][1], ax[i][2], ax[i][3], ax[i][4]] and ax[i][0].collections: 
                for axx in [ax[i][0], ax[i][1], ax[i][2], ax[i][3], ax[i][4]]:
                    cont, ind = axx.collections[0].contains(event)
                    if cont and ind:
                        self.fig.canvas.toolbar.set_message(self.annot_format(ind['ind'][0], i))

    def correlation_click(self, event):
        data = self.data

        index = int(self.radiobutton.value_selected)-1

        #vytovrenie subplotov pre correlacie
        fig2, ax2 = plt.subplots(nrows=1, ncols=3)
        plt.get_current_fig_manager().set_window_title(index + 1)

        attributes = ['LONGITUDE', 'GSPEED', 'HMSL']
        cursors = []

        for i in range(len(attributes)):
            attr = attributes[i]
            ax2[i].scatter(data[index]['HACC'], data[index][attr])
            ax2[i].set_title(attr)
            cursors.append(mplcursors.cursor(ax2[i], hover=True))
            if i % 3 == 0:
                ax2[i].yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.4f}'))

        cursors[0].connect("add", self.cursor_annot1)
        cursors[1].connect("add", self.cursor_annot2)
        cursors[2].connect("add", self.cursor_annot3)
        
        self.cursors = cursors

        #plot dat, formatovanie
        fig3, ax3 = plt.subplots()
        plt.get_current_fig_manager().set_window_title(index + 1)
        ax3.set_title(self.filenames[index])
        corr = data[index].corr()
        sb.heatmap(corr, cmap="Blues", annot=True)

        plt.show()

    #formatovanie hoveru pri korelacnych grafoch
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

        #vytvorenie listov na uchovanie boundry box suradnic pre jednotlive vzorky
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
        
        #nastavenie colormapy podla typu dat
        color = []
        for i in range(len(data)):
            color.append(('Blue', data[i]['HMSL'], data[i]['GSPEED'], data[i]['CRS'], data[i]['HACC']))

        #vytovrenie pola na uchovanie parsovanych dat
        p = [[0 for x in range(5)] for y in range(len(data))] 
        counter = 0
        
        #ofarbenie bodov
        for i in range(len(color)):
            for clr in color[i]:
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
        
        #ziskanie map pomocou tilemapbase
        plotter = []
        for i in range(len(data)):
            extent = tilemapbase.Extent.from_lonlat(x1[i],x2[i],y1[i],y2[i])
            t = tilemapbase.tiles.build_OSM()
            plotter.append(tilemapbase.Plotter(extent, t, width=100))
        
        #vykreslenie dat
        for y in range(len(data)):
            for i in range(5):
                plotter[y].plot(ax[y][i])

        self.fig.canvas.toolbar.update()
        plt.subplots_adjust(left=0.25, top= 0.95, bottom= 0.05)

    #po kliknuti na bod sa vypisu jeho udaje
    def map_click(self, event):
        i = event.ind[0]
        pnts = event.artist.get_offsets()
        xdata, ydata = pnts[0,:]
        
        for z in range(len(self.data)):
            points = [tilemapbase.project(x,y) for x,y in zip(self.data[z]['LONGITUDE'], self.data[z]['LATITUDE'])]
            x, y = zip(*points)

            if x[0] == xdata and y[0] ==ydata:
                break

        print(self.annot_format(i, z))
        self.fig.canvas.toolbar.set_message(self.annot_format(i, z))

    #format bypisu dat pri akcii hover alebo click
    def annot_format(self, i, y):
        return ("x: " + str(self.data[y]['LONGITUDE'][i]) + "\n" + \
        "y: " + str(self.data[y]['LATITUDE'][i]) + "\n" + \
        "altitude: " + str(round(self.data[y]['HMSL'][i]/1000, 2)) + "\n" + \
        "speed: " + str(round(self.data[y]['GSPEED'][i]*3.6/100, 2)) + "\n" + \
        "crs: " + str(round(self.data[y]['CRS'][i], 2)) + "\n" + \
        "accuracy: " + str(round(self.data[y]['HACC'][i], 2)))

    #funkcia vrati hranicne suradnice jazdy ku, ktorej sa pripocita 1/10 rozdielu najmensej a najvacsej suradnice, kvoli lepsej prehlasdnosti na mape
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
        #preedieme lat a long do markator pre pouzitie s tilemapbase pre ziskanie mapy
        points = [tilemapbase.project(x,y) for x,y in zip(self.data[i]['LONGITUDE'], self.data[i]['LATITUDE'])]
        x, y = zip(*points)

        #priradenie bodov pre jednotlive osi
        sct = self.ax[i][counter].scatter(x, y, zorder=1, alpha= 0.2, c=color, cmap=mpl.cm.rainbow, s=30, visible=True, picker=True)
        arr[counter] = sct

    #reusporiadanie subplotov pri ich vebere pomocou checkboxu
    def check_click(self, label):
        i = self.labels.index(label)
        counter = 0
        ax, fig, checkbox_status = self.ax, self.fig, self.checkbox_status

        #chceknute atributy necha viditelne, unchecknute skryje
        for y in range(len(self.data)):
            if ax[y][i].get_visible():
                ax[y][i].set_visible(False)
                checkbox_status[i] = 0
            else:
                ax[y][i].set_visible(True)
                checkbox_status[i] = 1

        if checkbox_status.count(1) > 0:
            gs = gridspec.GridSpec(len(self.data), checkbox_status.count(1), wspace=0.025, hspace=0.05)

        #zmeni velkosti na aktulanom pocte zobrazenych atributov
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

def load_data(divide_sample_by):
        #vyber suboru
        tk.Tk().withdraw()
        filenames = askopenfilenames(title='Choose your file', filetypes=[("csvs", (".txt", ".log", "csv")), ("all", "*")])

        files = []

        #kontrola ci bol vybraty subor
        if not filenames:
            print('Najprv treba vybrat subor!')
            return (files, filenames)
        
        #zisti ci sa jedna o stary alebo novy format dat
        counter = 0
        for file in filenames:     
            try:
                files.append(json_to_df(file))
            except:
                files.append(old_to_df(file))

            if divide_sample_by > 1 and isinstance(divide_sample_by, int):
                files[counter] = files[counter].sample(len(files[counter])//divide_sample_by) #zmensenie vzdorky, podla parametra divide_sample_by
                files[counter].reset_index(drop=True, inplace=True) #reindexovanie aby fungoval index anotacii
                counter += 1

        #chybove hlasky pri nespravne zadanom divide_sample_by
        if divide_sample_by < 1:
            print("divide_sample_by musi byt vacsie ako 1")
        if not isinstance(divide_sample_by, int):
            print("divide_sample_by musi byt typu int")

        filenames = list(filenames)
        return (files, filenames)

#parsovanie stareho formatu dat do df
def old_to_df(filename):
    df = pd.read_csv(filename, names=['TIME','2','LATITUDE','4','LONGITUDE','6','HMSL','8','GSPEED','10','CRS','12', 'HACC'], sep=';')
    df = df.dropna(how='all')
    df = df.drop(columns=['TIME', '2', '4', '6', '8', '10', '12'])
    df['LATITUDE'] = df['LATITUDE'].div(10000000)
    df['LONGITUDE'] = df['LONGITUDE'].div(10000000)
    df['CRS'] = df['CRS'].div(100000)
    return df

#novy format dat typu json do df
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
    df = df.dropna(how='all')
    return df

def append_average(data_arr):
    average = Average()
    average.load_data_avg(300, data_arr)
    data_arr.append(average.get_data())
    return data_arr

#nacitanie dat po kliknuti na tlacidlo, ak bol vybrany average tak prida aj spriemerovanu trasu
def init_visualize_click(plus_average, divide_sample_by):
    data, filenames = load_data(divide_sample_by)

    counter = 0
    if not data:
        return

    #ak sa vo vybranych suboroch nachadza subor s chybnymi datami subor neberieme do uvahy
    for df in data:
        if(df.isnull().values.any()):
            print("Subor {} obsahuje null hodnoty!".format(filenames[counter]))
        if df.empty :
            print("Subor {} obsahuje nespravny format dat!".format(filenames[counter]))
        counter += 1

    #prejde nacitane subory a vymaze obsahujuce bull hodnoty
    data = [df for df in data if not df.isnull().values.any()]

    #vymazeme subory s nespravnym formatom
    data = [df for df in data if not df.empty]

    #ak mame aspon jeden subor so spravnymi datami
    if data:
        #ak sme si vybrazi moznost s averagom, pridame do dat na koniec aj average
        if plus_average:
            data = append_average(data)
            filenames.append('averaged')

        #samotne vytvorenie okna s nacitanymi datami
        Window(data, filenames)

if __name__ == '__main__':
    #vytvorenie uvodneho okna aplikacie
    root = tk.Tk()
    root.geometry('300x200')
    root.resizable(False, False)
    root.title('Analyzator')

    #hodnota ktorou sa bude delit pocet zaznamov v jednotlivych suboroch pouzitim df.sample()
    divide_sample_by = 10

    #tlacidla na vizualizaciu a agerage
    visualize_button = ttk.Button(root, text='Visualize', command=lambda: init_visualize_click(False, divide_sample_by))
    average_button = ttk.Button(root, text='Average', command=lambda: init_visualize_click(True, divide_sample_by))

    visualize_button.pack(ipadx=5, ipady=6, expand=True)
    average_button.pack(ipadx=5, ipady=4, expand=True)

    root.mainloop()
