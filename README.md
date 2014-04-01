#####MarketMaker

###General Working Flow
The Market class is the main Class which runs the simulation. In start_simulation you will find a quick overview of how a simulation could be started. Also, if you want to get, how this is working, start of in the Market.py class with reading the comments and then go on.

###How does a Trading Algorithm work
Trading Algorithms are refered to as TAlgorithms or TAlgos often in the comments and here. At the moment, there is no standard how the TAlgo will be initlialized (in which order the Broker, portfolio, ... instances will be passed). So look into the market class to find out. You will be passed a Market instance (and through Market.data you'll have a DataHandler Instance through that too), a Broker Instance and a Portfolio instance.
##For What do I need the Classes?
#1. DataHandler
In the DataHandler, which you can reference through Market.data, you should define a callback in your TAlgo and do Market.data.time_change.registerObserver(callback). The callback will be called every time, when new data is available. You can get that data through data.get_latest_data(fxcode, time) or data.get_current_tick(fxcode) (also functions of the DataHandler class)
#2. Broker
At the broker you are able to set limit and market orders. Also you can register as an observer (same way like with datahandler) to get information when an order is filled.
#3. Portfolio
Here you can view your current holdings. Also you need to pass by your portfolio to the broker often, so he knows which portfolio he has to charge when executing your orders

For more information about how the classes work and how you can use them, please look at the classes themselves.

[Here you can get even more free forex historical ticks data](http://www.histdata.com/download-free-forex-data/?/ascii/tick-data-quotes)
