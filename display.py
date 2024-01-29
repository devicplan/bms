# Jens Dietrich jd@icplan.de 
# 29.01.2024 (Raspberry Pico W)
# eigener Zeichensatz auf OLED Display
# 128 x 65 OLED (21 x 8 Zeichen)
# neu mit extra Kontrast verstellen

from machine import Pin, I2C
import ssd1306, time, display

sda = Pin(12)
scl = Pin(13)

i2c0=I2C(0,sda=sda, scl=scl, freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c0)

# Zeichensatz 5 x 8 Zeichen, ascii zeichen 0x20 bis 0x7F, linkes byte ist linker Pixelstreifen
z_code = [
0x00,0x00,0x00,0x00,0x00,0x00,                                                     #  
0x00,0x00,0x00,0x4F,0x00,0x00,                                                     # !
0x00,0x00,0x07,0x00,0x07,0x00,                                                     # "
0x00,0x14,0x7F,0x14,0x7F,0x14,                                                     # #
0x00,0x24,0x2A,0x7F,0x2A,0x12,                                                     # $
0x00,0x23,0x13,0x08,0x64,0x62,                                                     # %
0x00,0x36,0x49,0x55,0x22,0x50,                                                     # &
0x00,0x00,0x05,0x03,0x00,0x00,                                                     # '
0x00,0x00,0x1C,0x22,0x41,0x00,                                                     # (
0x00,0x00,0x41,0x22,0x1C,0x00,                                                     # )
0x00,0x14,0x08,0x3E,0x08,0x14,                                                     # *
0x00,0x08,0x08,0x3E,0x08,0x08,                                                     # +
0x00,0x00,0x50,0x30,0x00,0x00,                                                     # ,
0x00,0x08,0x08,0x08,0x08,0x08,                                                     # -
0x00,0x00,0x60,0x60,0x00,0x00,                                                     # .
0x00,0x20,0x10,0x08,0x04,0x02,                                                     # /
0x00,0x3E,0x51,0x49,0x45,0x3E,                                                     # 0
0x00,0x00,0x42,0x7F,0x40,0x00,                                                     # 1
0x00,0x42,0x61,0x51,0x49,0x46,                                                     # 2
0x00,0x21,0x41,0x45,0x4B,0x31,                                                     # 3
0x00,0x18,0x14,0x12,0x7F,0x10,                                                     # 4
0x00,0x27,0x45,0x45,0x45,0x39,                                                     # 5
0x00,0x3C,0x4A,0x49,0x49,0x30,                                                     # 6
0x00,0x01,0x71,0x09,0x05,0x03,                                                     # 7
0x00,0x36,0x49,0x49,0x49,0x36,                                                     # 8
0x00,0x06,0x49,0x49,0x29,0x1E,                                                     # 9
0x00,0x00,0x36,0x36,0x00,0x00,                                                     # :
0x00,0x00,0x56,0x36,0x00,0x00,                                                     # ;
0x00,0x08,0x14,0x22,0x41,0x00,                                                     # <
0x00,0x14,0x14,0x14,0x14,0x14,                                                     # =
0x00,0x00,0x41,0x22,0x14,0x08,                                                     # >
0x00,0x02,0x01,0x51,0x09,0x06,                                                     # ?
0x00,0x32,0x49,0x79,0x41,0x3E,                                                     # @
0x00,0x7E,0x11,0x11,0x11,0x7E,                                                     # A
0x00,0x7F,0x49,0x49,0x49,0x36,                                                     # B
0x00,0x3E,0x41,0x41,0x41,0x22,                                                     # C
0x00,0x7F,0x41,0x41,0x22,0x1C,                                                     # D
0x00,0x7F,0x49,0x49,0x49,0x41,                                                     # E
0x00,0x7F,0x09,0x09,0x09,0x01,                                                     # F
0x00,0x3E,0x41,0x49,0x49,0x7A,                                                     # G
0x00,0x7F,0x08,0x08,0x08,0x7F,                                                     # H
0x00,0x00,0x41,0x7F,0x41,0x00,                                                     # I
0x00,0x20,0x40,0x41,0x3F,0x01,                                                     # J
0x00,0x7F,0x08,0x14,0x22,0x41,                                                     # K
0x00,0x7F,0x40,0x40,0x40,0x40,                                                     # L
0x00,0x7F,0x02,0x0C,0x02,0x7F,                                                     # M
0x00,0x7F,0x04,0x08,0x10,0x7F,                                                     # N
0x00,0x3E,0x41,0x41,0x41,0x3E,                                                     # O
0x00,0x7F,0x09,0x09,0x09,0x06,                                                     # P
0x00,0x3E,0x41,0x51,0x21,0x5E,                                                     # Q
0x00,0x7F,0x09,0x19,0x29,0x46,                                                     # R
0x00,0x46,0x49,0x49,0x49,0x31,                                                     # S
0x00,0x01,0x01,0x7F,0x01,0x01,                                                     # T
0x00,0x3F,0x40,0x40,0x40,0x3F,                                                     # U
0x00,0x1F,0x20,0x40,0x20,0x1F,                                                     # V
0x00,0x3F,0x40,0x38,0x40,0x3F,                                                     # W
0x00,0x63,0x14,0x08,0x14,0x63,                                                     # X
0x00,0x07,0x08,0x70,0x08,0x07,                                                     # Y
0x00,0x61,0x51,0x49,0x45,0x43,                                                     # Z
0x00,0x00,0x7F,0x41,0x41,0x00,                                                     # [
0x00,0x15,0x16,0x7C,0x16,0x15,                                                     # slash
0x00,0x00,0x41,0x41,0x7F,0x00,                                                     # ]
0x00,0x04,0x02,0x01,0x02,0x04,                                                     # ^
0x00,0x40,0x40,0x40,0x40,0x40,                                                     # _
0x00,0x00,0x01,0x02,0x04,0x00,                                                     # `
0x00,0x20,0x54,0x54,0x54,0x78,                                                     # a
0x00,0x7F,0x48,0x44,0x44,0x38,                                                     # b
0x00,0x38,0x44,0x44,0x44,0x20,                                                     # c
0x00,0x38,0x44,0x44,0x48,0x7F,                                                     # d
0x00,0x38,0x54,0x54,0x54,0x18,                                                     # e
0x00,0x08,0x7E,0x09,0x01,0x02,                                                     # f
0x00,0x0C,0x52,0x52,0x52,0x3E,                                                     # g
0x00,0x7F,0x08,0x04,0x04,0x78,                                                     # h
0x00,0x00,0x44,0x7D,0x40,0x00,                                                     # i
0x00,0x20,0x40,0x44,0x3D,0x00,                                                     # j
0x00,0x7F,0x10,0x28,0x44,0x00,                                                     # k
0x00,0x00,0x41,0x7F,0x40,0x00,                                                     # l
0x00,0x7C,0x04,0x18,0x04,0x78,                                                     # m
0x00,0x7C,0x08,0x04,0x04,0x78,                                                     # n
0x00,0x38,0x44,0x44,0x44,0x38,                                                     # o
0x00,0x7C,0x14,0x14,0x14,0x08,                                                     # p
0x00,0x08,0x14,0x14,0x18,0x7C,                                                     # q
0x00,0x7C,0x08,0x04,0x04,0x08,                                                     # r
0x00,0x48,0x54,0x54,0x54,0x20,                                                     # s
0x00,0x04,0x3F,0x44,0x40,0x20,                                                     # t
0x00,0x3C,0x40,0x40,0x20,0x7C,                                                     # u
0x00,0x1C,0x20,0x40,0x20,0x1C,                                                     # v
0x00,0x3C,0x40,0x30,0x40,0x3C,                                                     # w
0x00,0x44,0x28,0x10,0x28,0x44,                                                     # x
0x00,0x0C,0x50,0x50,0x50,0x3C,                                                     # y
0x00,0x44,0x64,0x54,0x4C,0x44,                                                     # z
0x00,0x00,0x08,0x36,0x41,0x00,                                                     # {
0x00,0x00,0x00,0x7F,0x00,0x00,                                                     # |
0x00,0x00,0x41,0x36,0x08,0x00,                                                     # }
0x00,0x08,0x08,0x2A,0x1C,0x08,                                                     # pfeil rechts
0x00,0x08,0x1C,0x2A,0x08,0x08,                                                     # pfeil links
]

# line zeichnen
# x=spalte (seitlich) y=zeile (hoch) farbe 0=loeschen 1=schwarz
def dis_line(ax,ay,bx,by,farbe):
    x = 0,1
    y = 0,1
    x1 = 0,1
    a = 0
    s = 0

    if( ax > bx ):                                                                 # umdrehen
        a = bx
        bx = ax
        ax = a
        a = by
        by = ay
        ay = a

    if(ay <= by ):                                                                 # ay ist kleiner als by -> nach unten
        x = bx - ax
        y = by - ay
        if( x >= y):                                                               # flach nach unten
            x1 = y / x;
            for a in range (ax,bx+1.1):
                s = a - ax                                                         # schrittweite
                x = a
                y = ay + (s * x1)
                oled.pixel(int(x),int(y),farbe)
        else:                                                                      # steil nach unten
            x1 = x / y
            for a in range (ay,by+1,1):
                s = a - ay                                                         # schrittweite
                y = a
                x = ax + (s * x1)
                oled.pixel(int(x),int(y),farbe)
    else:                                                                          # ay ist groesser als by -> noch oben
        x = bx - ax
        y = ay - by
        if( x >= y):                                                               # flach nach oben
            x1 = y / x
            for a in range (ax,bx,1):
                s = a - ax                                                         # schrittweite
                x = a
                y = ay - (s * x1)
                oled.pixel(int(x),int(y),farbe)
        else:                                                                      # steil nach oben
            x1 = x / y
            for a in range (by,ay+1,1):
                s = a - by                                                         # schrittweite
                y = ay + by - a
                x = ax + (s * x1)
                oled.pixel(int(x),int(y),farbe)
    return

# zeichenausgabe an bestimmte displayposition direkt auf dogspeicher
# z=zeichen 0x20-0x7f ; x=0-127 ; y=0-63 ; groesse=0-3; farbe=0-1
# xy position ist zeichen (6x8) oben links
def dis_z (z,x,y,g,f):
    a=b=c=d=e=h=cn=s=stelle=0
    bit = [0,0,0,0,0,0,0,0]
    if((z<0x20) or( z>0x7f)):
        z=0x20                                                                     # nur sichtbare ascii zeichen
    stelle = 6*(z-0x20)                                                            # stelle berechnen
    if (f==0):                                                                     # farbbit und negation farbbit
        c = 0                                                                      # keine farbe
        cn = 1
    else:
        c = 1                                                                      # mit farbe
        cn = 0
    for s in range (0,6,1):
        a = z_code[stelle];                                                        # 6 streifen laden
        stelle +=1
        if ((a & 0x80) > 0): bit[0] = c
        else: bit[0] = cn                                                          # lt. bit farbe setzen
        if ((a & 0x40) > 0): bit[1] = c
        else: bit[1] = cn
        if ((a & 0x20) > 0): bit[2] = c
        else: bit[2] = cn
        if ((a & 0x10) > 0): bit[3] = c
        else: bit[3] = cn
        if ((a & 0x08) > 0): bit[4] = c
        else: bit[4] = cn
        if ((a & 0x04) > 0): bit[5] = c
        else: bit[5] = cn
        if ((a & 0x02) > 0): bit[6] = c
        else: bit[6] = cn
        if ((a & 0x01) > 0): bit[7] = c
        else: bit[7] = cn
        d = g + 1
        if((d > 4) or (d < 1)): d = 1                                              # d darf nur 1-4 sein (groessenscalierung)
        for e in range (0,d,1):
            for b in range (0,8,1):
                for h in range (0,d,1):
                    if(bit[7-b]==f): 
                        oled.pixel(int(x),int(y),bit[7-b])                         # nur farbpixel, kein rahmen um zeichen machen
                    y+=1
            x+=1
            y = y - (d*8)
    return

# OLED Kontrast 
def contrast(x):
    oled.contrast(int(x))                                                          # 0-255 moeglich
    return

# OLED loeschen
def clear():
    oled.fill(0)
    return
    
# Zeichenkette anzeigen (g: 0=21x8 1=10x4 2=5x2)
def dis (t,x,y,g):
    if(len(t)<1):
        return
    w = len(t)                                                                     # laenge der Zeichenkette
    for a in range (0,w,1):
        dis_z(ord(t[a]),x,y,g,1)
        if(g==0): h=6
        if(g==1): h=11
        if(g==2): h=21
        if(g==3): h=42
        x = x + h
    return

# OLED anzeigen
def show():
    oled.show()
    return

