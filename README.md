<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/25423296/163456776-7f95b81a-f1ed-45f7-b7ab-8fa810d529fa.png">
</picture>

# BMS Controller

A BMS - Battery Management System Controller has the task of monitoring a large number of LiFePo4, Li-Ion, LiPo battery cells so that they are not damaged during charging and discharging and can be used for as long as possible without any faults.
My BMS controller communicates with the balancer modules via a data bus and controls the charging and discharging of the battery cells directly via switching relays. In my case, these relays each switch a Victron Smart BatterieProtect (SSR 65-220A solid state relay). The battery cells are protected by the BMS controller against overcharging, over-discharging and high and low temperatures. The galvanically isolated bus connection uses its own serial data protocol and can read out the battery voltage, battery temperature and the temperature of the load resistors from the balancers at any time. As soon as a temperature that is too high or too low is detected or a malfunction occurs when reading the data, the BMS controller reacts appropriately and disconnects the load or interrupts charging. In the event of an error, an audio signal can be emitted for signaling purposes. In addition, a switched relay contact can be used freely. In the event of serious malfunctions, the BMS switches off charging or discharging completely. The error must then be acknowledged via the web interface or directly via a button on the BMS module. The BMS controller has a WLAN web interface and can connect to an existing WLAN network. The most important parameters of all battery cells and the function of the BMS can be called up in the network via a browser. To protect against tampering, it is not possible to change settings via the web interface. An OLED display on the BMS controller can also show the most important parameters of the battery cells. If there is a desire to record or further process the battery cell data, the BMS Controller can also send it to a free Thingspeak cloud account. 
It would also be possible to use your own MQTT broker (FHEM, ioBroker, IP-Symcon, Mosquito ...) if a suitable software module is added.

## Functions (Version 00.99.09)

* 1 to 50 balancers can be connected via the isolated serial bus
* maximum bus length 10m (line topology)
* battery voltage measurement via balancer from each cell
* battery temperature measurement via balancer from each cell
* temperature measurement at the load resistor via balancer from each balancer
* read out software version and uptime of each balancer 
* OLED display (operation of the BMS controller is also possible without OLED display)
* in the event of malfunctions, charging or discharging is switched off (one relay each)
* integrated sounder (can be deactivated via software)
* LED alarm function with additional relay output
* WLAN connection (operation also possible without WIFI) 
* logging via Thingspeak or MQTT (WLAN required)
* LEDs indicate the switching status of the three relays
* flashing LED on the Raspberry Pico W as a function check
* web view of all parameters and functions (WLAN required)
* 24-hour graph of the total battery voltage (WLAN required)
* adjustable end-of-discharge voltage (value of the cell with the lowest voltage)
* adjustable end-of-charge voltage (value of the cell with the highest voltage)
* adjustable overtemperature protection of the battery during charging and discharging
* adjustable under-temperature protection of the battery during charging
* adjustable alarm in the event of extreme undervoltage of a cell (long storage without charging)  
* adjustable alarm in the event of extreme overvoltage of a cell (balancer or SSR is defective) 
* 3 variants of power supply possible.
  - a) via USB connection
  - b) via 12-40 volts DC from the battery
  - c) with 230 volts from the mains. (energy-saving switching power supply technology)
* watchdog (automatic restart of the software if it does not respond for a longer period of time)
* error states can be acknowledged via the web view or via the mode button
* firmware in the Raspberry Pico W can be changed and updated at any time
* firmware uses the Micropython scripting language, is well and fully commented
* like every balancer module, the BMS controller has its own uptimer
* time synchronization (WLAN required)

# BMS Controller

Ein BMS - Batterie-Magement-System Controller hat die Aufgabe, eine größere Zahl von LiFePo4, Li-Ion, LiPo Akkuzellen so zu überwachen, dass diese beim Laden und Entladen keinen Schaden nehmen und möglichst lange störungsfrei genutzt werden können.
Mein BMS Controller kommuniziert dafür über einen Datenbus mit den Balancermodulen und steuert direkt über Schaltrelais das Laden und Entladen der Akkuzellen. Bei mir schalten diese Relais je ein Victron Smart BatterieProtect (SSR 65-220A Halbleiterrelais). Die Akkuzellen werden durch den BMS Controller vor Überladung, zu tiefer Entladung, vor hohen und zu tiefen Temperaturen geschützt. Die galvanisch getrennte Bus Verbindung nutzt ein eigenes serielles Datenprotokoll und kann jederzeit aus den Balancern die Akkuspannung, die Akkutemperatur und die Temperatur der Lastwiderstände auslesen. Sobald eine zu hohe, zu tiefe Temperatur erkannt wird oder eine Fehlfunktion beim Lesen der Daten auftritt, reagiert der BMS Controller passend und trennt die Last oder unterbricht das Laden. Im Fehlerfall kann ein Tonsignal zur Signalisierung ausgegeben werden. Zusätzlich ist ein geschalteter Relaiskontakt frei nutzbar. Bei schwerwiegenden Fehlfunktionen schaltet das BMS das Laden oder Entladen komplett ab. Der Fehler muss dann über die Webschnittstelle oder direkt per Taster am BMS Modul quittiert werden. Der BMS Controller hat  eine WLAN Webschnittstelle und kann sich mit einem vorhandenen WLAN Netzwerk verbinden. Die wichtigsten Parameter aller Akkuzellen und der Funktion das BMS kann im Netzwerk per Browser aufgerufen werden. Als Schutz vor Manipulationen ist es über die Webschnittstelle nicht möglich, Einstellungen abzuändern. Ein OLED Display auf dem BMS Controller kann zusätzlich die wichtigsten Parameter der Akkuzellen zeigen. Besteht der Wunsch die Daten der Akkuzellen aufzuzeichnen oder weiterzuverarbeiten, dann kann der BMS Controller diese auch an einen kostenfreien Thingspeak Cloud-Account senden. 
Auch die Nutzung eines eigenen MQTT Brokers (FHEM, ioBroker, IP-Symcon, Mosquito …) wäre möglich, wenn ein passender Softwarebaustein hinzugefügt wird.

## Funktionen (Version 00.99.09)
* 1 bis 50 Balancer können über den isolierten seriellen Bus angeschlossen werden
* Buslänge maximal 10m (Linientopologie)
* Akkuspannungsmessung über Balancer aus jeder Zelle
* Akkutemperaturmessung über Balancer aus jeder Zelle
* Temperaturmessung am Lastwiderstand über Balancer aus jedem Balancer
* Softwareversion und Uptime jedes Balancers auslesen 
* OLED Display (Betrieb des BMS Controllers ist auch ohne OLED Display möglich)
* bei Fehlfunktionen wird das Laden oder Entladen abgeschaltet (je ein Relais)
* Tongeber integriert (kann per Software deaktiviert werden)
* LED Alarmfunktion mit zusätzlichem Relaisausgang
* WLAN Verbindung (Betrieb auch ohne WIFI möglich) 
* Logging über Thingspeak oder MQTT (WLAN notwendig)
* LED’s zeigen den Schaltzustand der drei Relais an
* blinkende LED auf dem Raspberry Pico W als Funktionskontrolle
* Webansicht aller Parameter und Funktionen (WLAN notwendig)
* 24 Stunden Graph der Akkugesamtspannung (WLAN notwendig)
* einstellbare Entladeschluss-Spannung (Wert der Zelle mit der geringsten Spannung)
* einstellbare Ladeschluss-Spannung (Wert der Zelle mit der höchsten Spannung)
* einstellbare Übertemperaturschutz des Akkus beim Laden und Entladen
* einstellbarer Untertemperaturschutz des Akkus beim Laden
* einstellbarer Alarm bei extremer Unterspannung einer Zelle (lange Lagerung ohne Laden)  
* einstellbarer Alarm bei extremer Überspannung einer Zelle (Balancer oder SSR ist defekt) 
* 3 Varianten der Spannungsversorgung möglich.
  - a) über USB Anschluss
  - b) über 12-40 Volt Gleichspannung vom Akku
  - c) mit 230 Volt aus dem Stromnetz. (stromsparende Schaltnetzteiltechnik)
* Watchdog (automatischer Neustart der Software, wenn diese längere Zeit nicht reagiert)
* Fehlerzustände können über die Webansicht oder über den Mode Taster quittiert werden
* Firmware im Raspberry Pico W kann jederzeit geändert und aktualisiert werden
* Firmware nutzt die Scriptsprache Micropython, ist gut und komplett kommentiert
* BMS Controller hat wie jedes Balancermodul einen eigenen Uptimer
* Zeitsynchronisierung (WLAN notwendig)
