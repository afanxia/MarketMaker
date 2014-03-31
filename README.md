
Market Klasse ist Main Klasse sozusagen, sie bekommt referenzen zu der Broker-,
Portfolio-, TradingAlgorithm-, DataHandler- Klasse und instanziert dann alle.

DataHandler und TradingAlgortihm sind abstrakte Klassen, sind also nur dazu da
um vererbt und erweitert zu werden.

TradingAlgorithm bekommt wenn er instanziert wird eine Broker instanz und eine
Portfolio instanz. Das Portfolio gibt zu jedem Zeitpunkt aus, was die
TradingAlgorithm-Instanz (von nun an Trader genannt) besitzt. Spaeter kann man
z.B. hier die Analyse-Funktionen einbauen.

Broker macht Orders und ueberprueft bei Limit Orders bei jedem Update der
Daten, ob man sie erfuellen kann, sonst werden sie nach einer bestimmten 
Zeitspanne geloescht.

In der TradingAlgorithm Klasse sind viele Sachen auch nochmal
ausfuehrlich erklaert.

Der Market aktualisiert einfach nur in einer Dauerschleife den DataHandler,
und ueber Market.change wird jeder darueber informiert (kind of
Observer-Pattern, siehe Wikipedia).



Zuerst hatte ich einen Yahoo Scraper 
geschrieben, der im Minutentakt Ask/Bid Daten von Yahoo Finance holt und in
eine SQLite Datenbank speichert und dazu dann den DataHandler 
"LiteForexHandler", war gestern beim debuggen, und damit sollte das praktisch
auch schon funktionieren. 

Jedoch habe ich heute http://histdata.com gefunden, da gibts historische Tick-
Datas, also besser gehts nicht :) Ist im CSV format, hab jetzt mit dem 
CSVForexTicksHandler angefangen, der sollte auch so gut wie fertig sein. In der
Broker Klasse muesste dann noch einiges geaendert werden, da er halt momentan
auf minuetliche Ask/Bid Daten vom LiteForexHandler eingestellt ist, und nicht
live-tick daten. Das erledige ich wahrscheinlich morgen. Hoffe, dass man ab
morgen das ganze Backtesting-System dann funktioniert.
