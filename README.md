# Analýza senzorických a telemetrických údajov z vozidla linkového autobusu

### Potrebné knižnice:

    pandas
    numpy
    matplotlib
    mpl_toolkits
    tkinter
    mplcursors
    json
    seaborn
    tilemapbase
    
### Akceptované formáty dát
##### Formát 1
všetky dáta v jednom riadku oddelené čiarkou
    
    2021-04-21 14:42:21,069 - INFO - ;LAT;492268755;LON;187449692;HMSL;365658;GSPEED;4;CRS;20707796;HACC;3187

##### Formát 2
dáta vo formáte json rozdelené do po sobe nasledujúcich riadkov vo formáte JSON

    {"_mode": 0, "_length": "b'$\\x00'", "_checksum": "b'\\x1d9'", "_parsebf": 1, "_ubxClass": "b'\\x01'", "_ubxID": "b'\\x14'", "version": 0, "reserved0": 0, "invalidLlh": 0, "iTOW": 87379473, "lon": 0.0, "lat": 0.0, "height": 0, "hMSL": -17000, "lonHp": 0.0, "latHp": 0.0, "heightHp": 0.0, "hMSLHp": 0.0, "hAcc": 429496729.5, "vAcc": 429496729.5, "timestamp": 1644797761.3385432}
    
    {"_mode": 0, "_length": "b'$\\x00'", "_checksum": "b'\\xe2\\xc9'", "_parsebf": 1, "_ubxClass": "b'\\x01'", "_ubxID": "b'\\x12'", "iTOW": 87379473, "velN": 0, "velE": 0, "velD": 0, "speed": 0, "gSpeed": 0, "heading": 0.0, "sAcc": 2000, "cAcc": 180.0, "timestamp": 1644797761.339206}

### Použitie
- po spustení aplikácie si používateľ vyberie či chce dáta iba vizualizovať alebo aj priemerovať
    - pri vizualizácii sa vybreslia vybrané dáta
    - pri priemerovaní sa k vybraným súborom pridajú spriemerované dáta
- po kliknutí na tlačidlo correlate sa vykreslia korelácie vybraného súboru označené pomocou radiobuttonu
- checkbox slúži na skrývanie/zobrazovanie jednotlivých vykreslených atribútov


### Nastavenie sample size
- premenna udáva koľko násobne sa má zmenšiť sample size
- akceptované hodnoty sú väčsie ako 1
- iba celé čísla
- premenná sa nachádza v časti main

```divide_sample_by = 10 <--- tu zmeniť hodnotu```
    
### Sample data
v súbore sample_data
