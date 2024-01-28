# BMS Controller LiPoFe4 Version 0.99.00
# Micropython with Raspberry Pico W
# 28.01.2024 jd@icplan.de
# mit senden an Thingspeak

import secrets, network, socket, time, ntptime, utime, machine, os, urequests 

from machine import UART, Pin
uart0 = UART(0, baudrate=300, tx=Pin(16), rx=Pin(17))

led = machine.Pin("LED",machine.Pin.OUT)
led.off()
time.sleep(2)

# bitte anpassen
zellen = 8                                                                         # zellenzahl (anzahl balancer)
SEND_INTERVAL = 300                                                                # sendeintervall in sekunden

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

# html daten fuer webanzeige und quickchart
html00 = """<!DOCTYPE html><html>
    <head><meta http-equiv="content-type" content="text/html; charset=utf-8"><title>BMS Controller für LiFePo4 Balancer</title></head>
    <body><body bgcolor="#A4C8F0"><h1>BMS Controller f&uuml;r LiFePo4 Balancer</h1>
    <table "width=400"><tr><td width="200"><b>Softwareversion</b></td><td>0.99.00 (28.01.2024)</td></tr><tr><td><b>Pico W Firmware</b></td><td>"""
html01 = """</td></tr><tr><td><b>Idee & Entwicklung</b></td><td>https://icplan.de</td></tr><tr><td><b>Datum und Uhrzeit</b></td><td>"""
html02 = """</td></tr><tr><td><b>BMS Uptime</b></td><td>"""
html03 = """</td></tr></table><br>"""
html04 = """<table bgcolor="#B4D8F8" border="1" cellspacing="1" width="600"><tr><td bgcolor="#94B8E0" width="50"><b>Nr.</b></td><td bgcolor="#94B8E0" width="100"><b>Spannung</b></td><td bgcolor="#94B8E0" width="100"><b>Temp. Akku</b></td><td bgcolor="#94B8E0" width="100"><b>Temp. Shunt</b></td><td bgcolor="#94B8E0" width="140"><b>Uptime</b></td><td bgcolor="#94B8E0"><b>Software</b></td></tr>"""
html20 = """Ansicht der Akkuspannung der <a href="https://quickchart.io/chart?c={type:'line',data:{labels:["""
html21 = """],datasets:[{label:'LiFePo4 Spannung der letzten 24 Stunden (Volt)',data:["""
html22 = """]}]}}">letzten 24 Stunden</a> als Chart<br>"""
html98 = """</table><br>"""
html99 = """</body></html>"""

HTTP_HEADERS = {'Content-Type': 'application/json'}                                # fuer das thingspeak http paket

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(hostname="BMS")
wlan.connect(secrets.ssid, secrets.password)

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

max_wait = 30                                                                      # warten auf WLAN Verbindung
while max_wait > 0:                                                                # maximal 30 sec
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    led.on()
    time.sleep(1)
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
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

while True:                                                                        # endlosschleife Hauptprogramm
    local_time_sec = utime.time() + (int(sowi) * 3600)                             # zeitzohne beruecksichtigen
    time_a = utime.localtime(local_time_sec)
    serial_tx()                                                                    # seriellen datensatz senden
    try:
        cl, addr = s.accept()
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
        response += ("%4dd %02dh %02dm %02ds" % (up_d,up_h,up_m,up_s)) + html03 + html04
        
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
            time.sleep(10 - time_a[5])
    if((time_a[3] == 0)and(time_a[4] == 0)):                                       # taeglich um null uhr die interne zeit stellen
        time.sleep(15)
        try:
            ntptime.settime()                                                      # update zeit per ntp
        except OSError as error:
            print(str("errornr="),error)
    
    blinken()                                                                      # board led kurz zur funktionskontrolle aufblinken
    
    akt_time = time.time()                                                         # nach sendeintervall daten zu thingspeak versenden
    if akt_time - old_time > SEND_INTERVAL:
        old_time = akt_time
        print('senden an ThingSpeak')
        payload = {'field1':str(sp[0]), 'field2':str(ta[0]), 'field3':str(tr[0])} 
        request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + secrets.WRITE_API_KEY, json = payload, headers = HTTP_HEADERS )  
        request.close() 
