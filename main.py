# BMS Controller LiPoFe4 Version 0.99.06
# Micropython with Raspberry Pico W
# 04.02.2024 jd@icplan.de
# mit senden an Thingspeak

# bitte anpassen
oled_display = 1                                                                   # 0=kein display 1=betrieb mit oled display
wifi_ein = 1                                                                       # 0=kein wifi 1=betrieb mit wifi und internet
zellen = 8                                                                         # zellenzahl (anzahl balancer)
sp_min_aus = 3.05                                                                  # r1 entladen aus - mindestspannung
sp_min_ein = 3.20                                                                  # r1 entladen ein - wiedereinschaltspannung gleich oder groesser 
sp_max_aus = 3.70                                                                  # r2 laden aus - maximalspannung
sp_max_ein = 3.65                                                                  # r2 laden ein - wiedereinschalten wenn gleich oder kleiner
ta_max_al_ein = 45                                                                 # alarm maximale akkutemperatur ein -> laden & entladen aus
ta_max_al_aus = 40                                                                 # alarm maximale akkutemperatur aus -> laden & entladen ein
tr_max_al_ein = 90                                                                 # alarm maximale shunttemperatur -> laden aus
tr_max_al_aus = 80                                                                 # alarm maximale shunttemperatur -> laden wieder ein
SEND_INTERVAL = 300                                                                # sendeintervall thingspeak in sekunden

import secrets, network, socket, time, ntptime, utime, machine, os, urequests
if(oled_display):
    import display 

from machine import UART, Pin
uart0 = UART(0, baudrate=300, tx=Pin(16), rx=Pin(17))

led = Pin("LED",Pin.OUT)
led.off()
BUZ = Pin(2, Pin.OUT)                                                              # tongeber
R1 = Pin(19, Pin.OUT)                                                              # relais 1
R2 = Pin(20, Pin.OUT)                                                              # relais 2
R3 = Pin(21, Pin.OUT)                                                              # relais 3
tas = Pin(22,machine.Pin.IN)                                                       # mode taste
LED_ROT = Pin(28, Pin.OUT)                                                         # rote led leuchtet, bei low !
R1.off()                                                                           # alles relais aus
R2.off()
R3.off()
LED_ROT.on()                                                                       # rote (alarm) led aus
#BUZ.on()
time.sleep(0.02)                                                                   # kurzer ton bei start
BUZ.off()
time.sleep(2)                                                                      # bei programmstart 2 sekunden warten

# ab hier nichts aendern !
sowi = 1                                                                           # summertime = 2 wintertime = 1
azelle = 1                                                                         # aktuelle abgefragte zelle
u_error = 0                                                                        # 0 = kein 1 = mindestens ein fehler bei spannungsmessung
a_error = 0                                                                        # 0 = kein 1 = mindestens ein fehler temperatur am akku (ATTINY)
r_error = 0                                                                        # 0 = kein 1 = mindestens ein fehler temperatur am lastwiderstand
runde = 0                                                                          # messrundenzaehler
urunde = 0                                                                         # messunterrundenzaehler
sp = [0] * zellen                                                                  # spannung jeder zelle
sp_e = [0] * zellen                                                                # fehler bei spannungsmessung
sp_min = 0                                                                         # kleinste zellenspannung
sp_min_z = 0                                                                       # zellennummer mit der kleinsten spannung
sp_max = 0                                                                         # groesste zellenspannung
sp_max_z = 0                                                                       # zellennummer mit der groessten spannung
ta_max = 0                                                                         # groesste akkutemperatur
ta_max_z = 0                                                                       # zellennummer mit der groessten akkutemperatur
ta_alarm = 0                                                                       # akkutemperatur zu hoch
tr_max = 0                                                                         # groesste shunttemperatur
tr_max_z = 0                                                                       # zellennummer mit der groessten shunttemperatur
tr_alarm = 0                                                                       # shunttemperatur zu hoch
rel1 = 0                                                                           # relais 1 (0=aus 1=ein)
rel2 = 0                                                                           # relais 2 (0=aus 1=ein)
rel3 = 0                                                                           # relais 3 (0=aus 1=ein)
ta = [0] * zellen                                                                  # temperatur akku
ta_e = [0] * zellen                                                                # fehler bei temperatur akku 
tr = [0] * zellen                                                                  # temperatur lastwiderstand
tr_e = [0] * zellen                                                                # fehler bei temperatur lastwiderstand
up = [0] * zellen                                                                  # uptimer je zelle
soft = [0] * zellen                                                                # softwareversion je zelle
bms_start_t = 0                                                                    # startzeit bms controller
up_d = 0                                                                           # fuer berechnung uptime
up_h = 0                                                                           # fuer berechnung uptime
up_m = 0                                                                           # fuer berechnung uptime
up_s = 0                                                                           # fuer berechnung uptime
upt = 0                                                                            # fuer berechnung uptime
uname = 0
rpv2 = 0
sp_log = [0] * (96)                                                                # 15min aufzeichnung spannung der letzten 24 stunden
t_log = [0] * (96)                                                                 # 15min aufzeichnung zeiten der letzten 24 stunden
html_d = ""                                                                        # string daten
html_t = ""                                                                        # string zeiten
old_time = 0                                                                       # zeit der letzten mqtt sendung
dis_time = 0                                                                       # oled displayversatz zeitzaehler
dis_y = 0                                                                          # oled displayversatz hoehe
dis_x = 0                                                                          # oled displayversatz rechts
dis_zei = 0                                                                        # zaehler zum umschalten der untersten zeile

# html daten fuer webanzeige und quickchart
html00 = """<!DOCTYPE html><html>
    <head><meta http-equiv="content-type" content="text/html; charset=utf-8"><title>BMS Controller für LiFePo4 Balancer</title></head>
    <body><body bgcolor="#A4C8F0"><h1>BMS Controller f&uuml;r LiFePo4 Balancer</h1>
    <table "width=600"><tr><td width="300"><b>Softwareversion</b></td><td>0.99.06 (04.02.2024)</td></tr><tr><td><b>Pico W Firmware</b></td><td>"""
html01 = """</td></tr><tr><td><b>Idee & Entwicklung</b></td><td>https://icplan.de</td></tr><tr><td><b>Datum und Uhrzeit</b></td><td>"""
html02 = """</td></tr><tr><td><b>BMS Uptime</b></td><td>"""
html03 = """</td></tr><tr><td><b>Balancer Akku Spannungsmessung</b></td><td>"""
html04 = """</td></tr><tr><td><b>Balancer Akku Temperaturmessung</b></td><td>"""
html05 = """</td></tr><tr><td><b>Balancer Shunt Temperaturmessung</b></td><td>"""
html06 = """</td></tr><tr><td><b>BMS Gesamtfunktion</b></td><td>"""
html07 = """</td></tr></table><br>"""
html08 = """<table bgcolor="#B4D8F8" border="1" cellspacing="1" width="600"><tr><td bgcolor="#94B8E0" width="50"><b>Nr.</b></td><td bgcolor="#94B8E0" width="100"><b>Spannung</b></td><td bgcolor="#94B8E0" width="100"><b>Temp. Akku</b></td><td bgcolor="#94B8E0" width="100"><b>Temp. Shunt</b></td><td bgcolor="#94B8E0" width="140"><b>Uptime</b></td><td bgcolor="#94B8E0"><b>Software</b></td></tr>"""
html20 = """Ansicht der Akkuspannung der <a href="https://quickchart.io/chart?c={type:'line',data:{labels:["""
html21 = """],datasets:[{label:'LiFePo4 Spannung der letzten 24 Stunden (Volt)',data:["""
html22 = """]}]}}">letzten 24 Stunden</a> als Chart<br>"""
html98 = """</table><br>"""
html99 = """</body></html>"""

HTTP_HEADERS = {'Content-Type': 'application/json'}                                # fuer das thingspeak http paket

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(hostname="BMS")
if(wifi_ein):
    wlan.connect(secrets.ssid, secrets.password)
else:
    wlan.connect('no_ssid', 'no_password')                                         # ungueltige daten setzen

def pin_interrupt(Pin):                                                            # interrupt processing
    global u_error, a_error, r_error, sp_e, ta_e, tr_e
    u_error = 0                                                                    # errormeldungen und speicher loeschen
    a_error = 0
    r_error = 0
    a = 0
    for a in range (0,zellen,1):
        sp_e[a] = 0
        ta_e[a] = 0
        tr_e[a] = 0

tas.irq(trigger=machine.Pin.IRQ_RISING, handler=pin_interrupt)                     # interrupt bei gedrueckte mode taste

def fehler():                                                                      # fehlerreaktionen
    if(u_error)or(a_error)or(r_error):
        LED_ROT.off()                                                              # rote led ein
        R3.on()
    else:
        LED_ROT.on()
        R3.off()

def anzeige():                                                                     # oled anzeigefunktion
    global dis_time, dis_y, dis_x, dis_zei
    display.clear()
    spannung = 0.00001
    for a in range (0,zellen,1):                                                   # alle spannungen zusammenrechnen
        spannung += float(sp[a])
    text = '{:6.3f}'.format(spannung) + " Volt"
    display.dis(text,0+dis_x,0+dis_y,1)
    display.dis_line(0+dis_x,17+dis_y,124+dis_x,17+dis_y,1)
    text = "SP min =" + '{:6.3f}'.format(sp_min) + " V (" + '{:02d}'.format(sp_min_z) + ")" 
    display.dis(text,0+dis_x,20+dis_y,0)
    text = "SP max =" + '{:6.3f}'.format(sp_max) + " V (" + '{:02d}'.format(sp_max_z) + ")" 
    display.dis(text,0+dis_x,28+dis_y,0)
    text = "TA max = " + '{:2d}'.format(ta_max) + "    C (" + '{:02d}'.format(ta_max_z) + ")" 
    display.dis(text,0+dis_x,36+dis_y,0)
    text = "TR max = " + '{:2d}'.format(tr_max) + "    C (" + '{:02d}'.format(tr_max_z) + ")" 
    display.dis(text,0+dis_x,44+dis_y,0)

    if(dis_zei==0):
        text = "IP " + status[0]                                                   # ip adresse zeigen
    if(dis_zei==1):
        uptime =  time.time() - bms_start_t                                        # uptime bms modul berechnen
        d = int(uptime/(24*60*60))
        h = int((uptime-(d*24*60*60))/(60*60))
        m = int((uptime-(d*24*60*60)-(h*60*60))/60)
        s = int(uptime-(d*24*60*60)-(h*60*60)-(m*60))
        text = "UP " + str(d) +"d %02dh %02dm %02ds" % (h,m,s)
    if(dis_zei==2):
        text = "SW Version 00.99.05"                                               # softwareversion anzeigen
    display.dis(text,0+dis_x,52+dis_y,0)
    display.show()
    dis_zei += 1                                                                   # zaehler unterste zeile
    if(dis_zei>2):
        dis_zei = 0

    dis_time += 1                                                                  # zaehler displayversatz erhoehen
    if(dis_time==30):
        dis_time = 0
        dis_x += 1                                                                 # displayanzeige gegen einbrennen verschieben
        if(dis_x==3):
            dis_x = 0
            dis_y += 1
            if(dis_y==3):
                dis_y = 0

def min_max():                                                                     # min und max von spannung und temperatur ermitteln
    global sp, sp_min, sp_min_z, sp_max, sp_max_z, ta_max, ta_max_z, tr_max, tr_max_z, zellen, rel1, rel2, rel3, ta_alarm, tr_alarm
    a = 0                                                                          # min spannung ermitteln
    sp_min = 10.1
    for a in range (0,zellen,1):
        if(sp[a] < sp_min):
            sp_min = sp[a]                                                         # kleinere spannung speichern
            sp_min_z = a + 1                                                       # passende zellennummer speichern
    a = 0                                                                          # max spannung ermitteln
    sp_max = 1.1
    for a in range (0,zellen,1):
        if(sp[a] > sp_max):
            sp_max = sp[a]                                                         # groessere spannung speichern
            sp_max_z = a + 1                                                       # passende zellennummer speichern
    if(rel1==0):                                                                   # rel1 = entladerelais
        if(sp_min >= sp_min_ein):                                                  # spannung ist gleich oder groesser
            rel1 = 1                                                               # wiedereinschalten
            R1.on()
    else:
        if(sp_min < sp_min_aus):                                                   # spannung ist kleiner als mindestspannung
            rel1 = 0
            R1.off()
    if(rel2==1):                                                                   # rel2 = laderelais
        if(sp_max > sp_max_aus):                                                   # maximalspannung ueberschritten
            rel2 = 0                                                               # laden unterbrechen
            R2.off()
    else:
        if(sp_max <= sp_max_ein):                                                  # kann laden wieder aktiviert werden?
            rel2 = 1                                                               # wiedereinschalten
            R2.on()            
    a = 0                                                                          # max temperatur akku ermitteln
    ta_max = 0
    for a in range (0,zellen,1):
        if(ta[a] > ta_max):
            ta_max = ta[a]                                                         # groessere temperatur speichern
            ta_max_z = a + 1                                                       # passende zellennummer speichern
    a = 0                                                                          # max temperatur lastwiderstand/shunt ermitteln
    tr_max = 0
    for a in range (0,zellen,1):
        if(tr[a] > tr_max):
            tr_max = tr[a]                                                         # groessere temperatur speichern
            tr_max_z = a + 1                                                       # passende zellennummer speichern
    if(ta_alarm==0):                                                               # ist akkutemperaturalarm aus
        if(ta_max > ta_max_al_ein):                                                # maximaltemperatur akku ueberschritten
            ta_alarm = 1                                                           # alarm setzen
    else:
        if(ta_max <= ta_max_al_aus):                                               # ist akku wieder kuehler
            ta_alarm = 0                                                           # alarm entfernen
    if(tr_alarm==0):                                                               # ist lastwiderstandtemperaturalarm aus
        if(tr_max > tr_max_al_ein):                                                # maximaltemperatur akku ueberschritten
            tr_alarm = 1                                                           # alarm setzen
    else:
        if(tr_max <= tr_max_al_aus):                                               # ist akku wieder kuehler
            tr_alarm = 0                                                           # alarm entfernen
    if(ta_alarm==1):                                                               # alarm uebertemperatur akku
        rel1 = 0                                                                   # entladen unterbrechen
        R1.off()
        rel2 = 0                                                                   # laden unterbrechen
        R2.off()
    if(tr_alarm==1):                                                               # alarm uebertemperatur shunt/lastwiderstand
        rel2 = 0                                                                   # laden unterbrechen
        R2.off()
                   
def serial_tx():
    global runde, urunde, azelle
    uart0.readline()                                                               # leerlesen falls was angekommen ist
    if(runde==0):
        if(urunde==0):
            s = '{:02d}'.format(azelle) + "05"                                     # spannung lesen
            uart0.write(s)
        if(urunde==1):
            s = '{:02d}'.format(azelle) + "02"                                     # tempertur attiny lesen
            uart0.write(s)
        if(urunde==2):
            s = '{:02d}'.format(azelle) + "03"                                     # temperatur ds1820 lesen
            uart0.write(s)
        if(urunde==3):
            s = '{:02d}'.format(azelle) + "04"                                     # uptime lesen
            uart0.write(s)
        if(urunde==4):
            s = '{:02d}'.format(azelle) + "06"                                     # softwareversion lesen
            uart0.write(s)
    if(runde>0):
        if(urunde==0):
            s = '{:02d}'.format(azelle) + "05"                                     # spannung lesen
            uart0.write(s)
    print("SENDE", s, " ", end='')

def serial_rx():
    global runde, urunde, sp, sp_e, tr, tr_e, ta, ta_e, up, soft, azelle, zellen, u_error, a_error, r_error
    er = 0                                                                         # 0 = kein fehler in messung
    response = uart0.readline()
    try:
        a = int(response)
    except:
        response = "0"
        er = 1
    if(response==None):
        response = "0"
        er = 1
    d = '{:9d}'.format(int(response))
    
    if(urunde==0):                                                                 # spannungswerte
        if(er == 1):
            if(sp_e[azelle-1] > 1):                                                # der dritte fehler in folge
                u_error = 1                                                        # fehler global melden
            else:
                sp_e[azelle-1] += 1
        else:
            sp[azelle-1] = int(d) / 1000                                           # spnnungswert uebernehmen
            sp_e[azelle-1] = 0                                                     # fehlerzaehler zuruecksetzen
        print('UWERT', sp[azelle-1], 'CELLERROR', sp_e[azelle-1], 'UERROR', u_error)

    if(urunde==1):                                                                 # temperatur akku (attiny)
        if(er == 1):
            if(ta_e[azelle-1] > 1):                                                # der dritte fehler in folge
                a_error = 1                                                        # fehler global melden
            else:
                ta_e[azelle-1] += 1
        else:
            ta[azelle-1] = int(d)                                                  # temperaturwert uebernehmen
            ta_e[azelle-1] = 0                                                     # fehlerzaehler zuruecksetzen
        print('TAWERT', ta[azelle-1], 'CELLERROR', ta_e[azelle-1], 'AERROR', a_error)

    if(urunde==2):                                                                 # temperatur akku (attiny)
        if(er == 1):
            if(tr_e[azelle-1] > 1):                                                # der dritte fehler in folge
                r_error = 1                                                        # fehler global melden
            else:
                tr_e[azelle-1] += 1
        else:
            tr[azelle-1] = int(d)                                                  # temperaturwert uebernehmen
            tr_e[azelle-1] = 0                                                     # fehlerzaehler zuruecksetzen
        print('TRWERT', tr[azelle-1], 'CELLERROR', tr_e[azelle-1], 'RERROR', r_error)

    if(urunde==3):                                                                 # uptime lesen
        up[azelle-1] = int(d)                                                      # uptime uebernehmen
        print('UPTIME', up[azelle-1])

    if(urunde==4):                                                                 # softwareversion lesen
        soft[azelle-1] = int(d)                                                    # softwareversion uebernehmen
        print('SOFTWARE', soft[azelle-1])

    azelle += 1                                                                    # hintereinander alle werte abfragen
    if(azelle>zellen):
        azelle = 1
        urunde += 1
        if(urunde==5):
            urunde = 0

def blinken():
    led.on()                                                                       # led blinken als funktionskontrolle
    time.sleep(0.1)
    led.off()

def log_spannung():                                                                # alle 15min einen spannungs- und zeitstempel loggen
    global sp_log, t_log
    for a in range (1,96,1):                                                       # verschiebe alle spannungsdaten
        sp_log[a-1] = sp_log[a]
    spannung = 0.00001
    for a in range (0,zellen,1):                                                   # alle spannungen zusammenrechnen
        spannung += float(sp[a])
    sp_log[95] = spannung                                                          # aktuelle spannung ans ende der daten
    for a in range (1,96,1):                                                       # verschiebe alle zeitdaten
        t_log[a-1] = t_log[a]
    t_log[95] = ("'%02d:%02d'" % (time_a[3],time_a[4]))                            # chart zeitmarkierung

def thingspeak():
    global old_time
    akt_time = time.time()                                                         # nach sendeintervall daten zu thingspeak versenden
    if akt_time - old_time > SEND_INTERVAL:
        old_time = akt_time
        print('senden an ThingSpeak')
        payload = {'field1':str(sp[0]), 'field2':str(ta[0]), 'field3':str(tr[0])}  # erst mal nur testdaten !!!
        try:
            request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + secrets.WRITE_API_KEY, json = payload, headers = HTTP_HEADERS )  
            request.close()
        except OSError as error:
            print(str("mqtt_errornr="),error)

# programmstart
max_wait = 30                                                                      # warten auf WLAN Verbindung
while max_wait > 0:                                                                # maximal 30 sec
    if wlan.status() < 0 or wlan.status() >= 3 or not(wifi_ein):
        break
    max_wait -= 1
    print('waiting for connection...')
    led.on()
    time.sleep(1)
if wlan.status() != 3 and wifi_ein:
    print("1 Minute warten, dann Softreset")                                       # WLAN Netz nicht da oder nicht verbunden
    reset_time = 60                                                                # zeit abwarten mit doppelblinken dann neustart
    while(reset_time):    
        led.on()
        time.sleep(0.05)
        led.off()
        time.sleep(0.2)
        led.on()
        time.sleep(0.05)
        led.off()
        time.sleep(0.7)
        reset_time -= 1
    machine.reset()                                                                # neustart
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    led.off()
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
try:
    ntptime.settime()                                                              # update time per ntp
except OSError as error:
    print(str("errornr="),error)
bms_start_t = time.time()                                                          # startzeit ablegen
s = socket.socket()
s.bind(addr)
s.settimeout(4)
s.listen(10)
print('listening on', addr)
wdt = machine.WDT(timeout=8000)                                                    # watchdog auf 8 sekunden stellen

while True:                                                                        # endlosschleife Hauptprogramm
    local_time_sec = utime.time() + (int(sowi) * 3600)                             # zeitzohne beruecksichtigen
    time_a = utime.localtime(local_time_sec)
    serial_tx()                                                                    # seriellen datensatz senden
    try:
        cl, addr = s.accept()
        wdt.feed()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            lines = str(line)
            if((lines.find("/sommer"))!=(-1)):
                sowi = 2
            if((lines.find("/winter"))!=(-1)):
                sowi = 1
            if((lines.find("/error"))!=(-1)):
                u_error = 0                                                        # errormeldungen und speicher loeschen
                a_error = 0
                r_error = 0
                a = 0
                for a in range (0,zellen,1):
                    sp_e[a] = 0
                    ta_e[a] = 0
                    tr_e[a] = 0
            if not line or line == b'\r\n':
                break

        thistime = ("%02d.%02d.%4d  %02d:%02d:%02d" % (time_a[2],time_a[1],time_a[0],time_a[3],time_a[4],time_a[5]))   # datum und zeit fuer webseite

        html_t = str(t_log[0])                                                     # daten fuer quickchart.io erstellen
        for a in range (1,96,1):
            html_t = html_t + "," + str(t_log[a]) 
        html_d = str(sp_log[0])
        for a in range (1,96,1):
            html_d = html_d + "," + str(sp_log[a])
            
        uname = os.uname()                                                         # micropython version auslesen
        rp2v = uname.release
        response = html00 + rp2v + html01 + thistime + html02
             
        upt =  time.time() - bms_start_t                                           # uptime bms modul berechnen und anzeigen
        up_d = int(upt/(24*60*60))
        up_h = int((upt-(up_d*24*60*60))/(60*60))
        up_m = int((upt-(up_d*24*60*60)-(up_h*60*60))/60)
        up_s = int(upt-(up_d*24*60*60)-(up_h*60*60)-(up_m*60))
        response += ("%4dd %02dh %02dm %02ds" % (up_d,up_h,up_m,up_s)) + html03
        error_merker = 0                                                           # zelle mit fehlfunktion
        error_text = ""                                                            # text der fehlfunktion
        if(u_error):                                                               # anzeige spannungsfunktion
            for a in range (0,zellen,1):
                if(sp_e[a]>0):
                    error_merker = a + 1
                    error_text = "<font color=red>Fehler an Balancer Nr: " + ("%02d</font>" % (error_merker)) 
                    break
        else:
            error_text = "ok"
        response += error_text + html04
        error_merker = 0                                                           # zelle mit fehlfunktion
        error_text = ""                                                            # text der fehlfunktion
        if(a_error):                                                               # anzeige temperaturfunktion akku
            for a in range (0,zellen,1):
                if(ta_e[a]>0):
                    error_merker = a + 1
                    error_text = "<font color=red>Fehler an Balancer Nr: " + ("%02d</font>" % (error_merker)) 
                    break
        else:
            error_text = "ok"
        response += error_text + html05
        error_merker = 0                                                           # zelle mit fehlfunktion
        error_text = ""                                                            # text der fehlfunktion
        if(r_error):                                                               # anzeige temperaturfunktion lastwiderstand
            for a in range (0,zellen,1):
                if(tr_e[a]>0):
                    error_merker = a + 1
                    error_text = "<font color=red>Fehler an Balancer Nr: " + ("%02d</font>" % (error_merker)) 
                    break
        else:
            error_text = "ok"
        response += error_text + html06
        error_text = ""                                                            # text der fehlfunktion
        if((u_error)or(a_error)or(r_error)):
            error_text = "<font color=red>Entladen und Laden abgeschaltet !</font>"
        else:
            error_text = "keine Fehlfunktion"
        response += error_text + html07 + html08
        
        z = 0                                                                      # tabelle mit messwerten für html seite erstellen              
        for z in range (0,zellen,1):
            response += """<tr><td>"""
            response += str(z+1)                                                   # balancernummer
            response += """</td><td>"""
            response += str(sp[z])                                                 # spannungswert
            response += """</td><td>"""
            response += str(ta[z])                                                 # temperatur akku (attiny)
            response += """</td><td>"""
            response += str(tr[z])                                                 # temperatur shunt / lastwiderstand
            response += """</td><td>"""
            
            upt = up[z]                                                            # tabellenwert uptime vom balancer berechnen
            up_d = int(upt/(24*60*60))
            up_h = int((upt-(up_d*24*60*60))/(60*60))
            up_m = int((upt-(up_d*24*60*60)-(up_h*60*60))/60)
            up_s = int(upt-(up_d*24*60*60)-(up_h*60*60)-(up_m*60))
            response += ("%04dd %02dh %02dm %02ds" % (up_d,up_h,up_m,up_s))        # uptime ausgabe formatieren
            response += """</td><td>"""
            response += str(soft[z])
            response += """</td></tr>"""
        response += html98
        response += html20 + html_t + html21 + html_d + html22                     # chart einfuegen
        response += html99
        
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        wdt.feed()
        time.sleep(4)

    except OSError as e:
        if((e.args[0])==110):                                                      # error 110 = timeout socket
            pass
#           print('connection timeout')
        else:
            cl.close()
            print('connection closed')
            
    serial_rx()                                                                    # seriellen datensatz empfangen und auswerten

    if(time_a[5] < 10):
        if((time_a[4] % 15) == 0):                                                 # zu jeder 0, 15, 30, 45 minute
            log_spannung()
            wdt.feed()
            time.sleep(5)
            wdt.feed()
            time.sleep(5)
            wdt.feed()
    if((time_a[3] == 0)and(time_a[4] == 0)):                                       # taeglich um null uhr die interne zeit stellen
        wdt.feed()
        time.sleep(5)
        wdt.feed()
        time.sleep(5)
        wdt.feed()
        time.sleep(5)
        wdt.feed()
        try:
            ntptime.settime()                                                      # update zeit per ntp
        except OSError as error:
            print(str("errornr="),error)
    
    blinken()                                                                      # board led kurz zur funktionskontrolle aufblinken
    min_max()                                                                      # spannungen auswerten und relais schalten
    if(oled_display):                                                              # soll oled genutzt werden
        anzeige()                                                                  # auf oled anzeigen
    if(wifi_ein):                                                                  # soll wifi genutzt werden
        thingspeak()                                                               # daten zu thinhspeak senden
    fehler()                                                                       # fehlerbehandlung
    wdt.feed()                                                                     # watchdog zuruecksetzen

