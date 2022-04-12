
# we are using mplfinance to help us visualize the indicator
import mplfinance as mpf
import talib
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import numpy as np
import soporte as levels
import datetime
import numpy
formato3="{:<20} {:<20} {:<20} {:<20} {:<20}"
# to make the visualization better by only taking the last 100 rows of data

cryptos=['LUNA1-USD','BTC-USD','MATIC-USD','SOL-USD','DOT-USD','LINK-USD','ATOM-USD','SAND-USD','ETH-USD','AVAX-USD','ADA-USD','EWT-USD','FIL-USD','GALA-USD','ENJ-USD','CAKE-USD']

#cryptos=['BTC-USD']
def check_even(number):



    if float(number[1]) < 1:
        
        return True  

    return False


def traeCryptos():

  print(HEADER+str(datetime.datetime.now())+ENDC)

  json_string=[]

  for c in cryptos:

    msft = yf.Ticker(c)

    estado=''

    print(c)
    
    niveles=levels.lista_levels(c)

    df = msft.history(start="2020-01-01", end='2022-07-28')

    #EMA = talib.MA(df['Close'],timeperiod=20,matype=1)
     
    #print("Exponential Moving Average",EMA)



    # parameter setup
    length = 20
    mult = 2
    length_KC = 20
    mult_KC = 1.5

    # calculate BB
    m_avg = df['Close'].rolling(window=length).mean()
    m_std = df['Close'].rolling(window=length).std(ddof=0)


    df['upper_BB'] = m_avg + mult * m_std
    df['lower_BB'] = m_avg - mult * m_std

    # calculate true range
    df['tr0'] = abs(df["High"] - df["Low"])
    df['tr1'] = abs(df["High"] - df["Close"].shift())
    df['tr2'] = abs(df["Low"] - df["Close"].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)

    # calculate KC
    range_ma = df['tr'].rolling(window=length_KC).mean()
    df['upper_KC'] = m_avg + range_ma * mult_KC
    df['lower_KC'] = m_avg - range_ma * mult_KC

    highest = df['High'].rolling(window = length_KC).max()
    lowest = df['Low'].rolling(window = length_KC).min()
    m1 = (highest + lowest)/2
    df['value'] = (df['Close'] - (m1 + m_avg)/2)
    fit_y = np.array(range(0,length_KC))
    df['value'] = df['value'].rolling(window = length_KC).apply(lambda x: 
                              np.polyfit(fit_y, x, 1)[0] * (length_KC-1) + 
                              np.polyfit(fit_y, x, 1)[1], raw=True)


    df['ADX'] = talib.ADX(df['High'],df['Low'],df['Close'], timeperiod=14)
    #df[['value']].plot(figsize=(15,4))

    df['real'] = talib.ROC(df['ADX'], timeperiod=1)


    primera=df['real'][-1]


    # add colors for the 'value bar'
    colors = []
    for ind, val in enumerate(df['value']):
      if val >= 0:
        color = 'green'
        if val > df['value'][ind-1]:
          color = 'lime'
      else:
        color = 'maroon'
        if val < df['value'][ind-1]:
          color='red'
      colors.append(color)

    segunda=colors[-1]

    print('ADX '+str(round(df['ADX'][-1],2)))

    if round(df['ADX'][-1],2)<23:

      adx_texto='No hay fuerza'

    elif round(df['ADX'][-1],2)>30:

      adx_texto='Mucha Fuerza'

    else:

      adx_texto=''

    adx_texto=''


    if df['ADX'][-1]<df['ADX'][-2] and (color=='red' or color=='maroon'):

      print(OKGREEN+c +' COMPRA '+adx_texto+ENDC)

      estado=' Compre'+adx_texto

    elif df['ADX'][-1]<df['ADX'][-2] and (color=='green' or color=='lime'):

      print(FAIL+c +' VENTA  '+adx_texto+ENDC)

      estado=estado+' Venda'+adx_texto

    elif df['ADX'][-1]>df['ADX'][-2] and (color=='green' or color=='lime'):

      print(OKGREEN+c +' COMPRA  '+adx_texto+' '+ENDC)

      estado=estado+' Compre'+adx_texto

    else:

      print(OKBLUE+c+' NADA'+ENDC)

    result = list(map(lambda x: (x,abs(x-df['Close'][-1])*100/x,(x-df['Close'][-1])*100/x), niveles))

    precios=list(filter(check_even, result))

    try:

      soportes=min(precios, key=lambda item: item[1])

    except:

      pass

    data = len(precios)

    tipo=''

    porcentaje_cercania_soporte=1

    if data>0:

      if soportes[1]<porcentaje_cercania_soporte:

        #print(df['Close'][ind],df['Close'][-1],(df['Close'][ind]-df['Close'][-1])*100/df['Close'][ind])

        print(WARNING+formato3.format('NIVEL ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)),str(round(soportes[2],3))+'%',str(round(soportes[0],3))+ENDC))

        #estado=estado+' esta Cerca a un nivel'

    print(OKBLUE+'------------------------------------------------------------------------'+ENDC)


    json_string.append({
       "crypto":c,
       "estado":estado
      })
  with open('json_data.json', 'w') as outfile:


    outfile.write(json.dumps(json_string))
    


if __name__ == '__main__':

  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

  print(OKGREEN+".     .       .  .   . .   .   . .    +  ."+ENDC)
  print(OKGREEN+"  .     .  :     .    .. :. .___---------___."+ENDC)
  print(OKGREEN+"       .  .   .    .  :.:. _... .. ..  ... ::-_. ."+ENDC)
  print(OKGREEN+"    .  :       .  .  .:../:            . .^  :.:\."+ENDC)
  print(OKGREEN+"        .   . :: +. :.:/: .   .    .        . . .:\."+ENDC)
  print(OKGREEN+" .  :    .     . _ :::/:               .  ^ .  . .:\."+ENDC)
  print(OKGREEN+"  .. . .   . - : :.:./.                        .  .:\."+ENDC)
  print(OKGREEN+"  .      .     . :..|:                    .  .  ^. .:|"+ENDC)
  print(OKGREEN+"    .       . : : ..||        .                . . !:|"+ENDC)
  print(OKGREEN+"  .     . . . ::. ::\(                           . :)/"+ENDC)
  print(OKGREEN+" .   .     : . : .:.|. ######              .#######::|"+ENDC)
  print(OKGREEN+"  :.. .  :-  : .:  ::|.#######           ..########:|"+ENDC)
  print(OKGREEN+" .  .  .  ..  .  .. :\ ########          :######## :/"+ENDC)
  print(OKGREEN+"  .        .+ :: : -.:\ ########       . ########.:/"+ENDC)
  print(OKGREEN+"    .  .+   . . . . :.:\. #######       #######..:/"+ENDC)
  print(OKGREEN+"      :: . . . . ::.:..:.\           .   .   ..:/"+ENDC)
  print(OKGREEN+"   .   .   .  .. :  -::::.\.       | |     . .:/"+ENDC)
  print(OKGREEN+"      .  :  .  .  .-:.::.::.\             ..:/"+ENDC)
  print(OKGREEN+" .      -.   . . . .: .:::.:.\.           .:/"+ENDC)
  print(OKGREEN+".   .   .  :      : ....::_:..:\   ___.  :/"+ENDC)
  print(OKGREEN+"   .   .  .   .:. .. .  .: :.:.:\       :/"+ENDC)
  print(OKGREEN+"     +   .   .   : . ::. :.:. .:.|\  .:/|"+ENDC)
  print(OKGREEN+"     .         +   .  .  ...:: ..|  --.:|"+ENDC)
  print(OKGREEN+".      . . .   .  .  . ... :..:...(  ..)"+ENDC)
  print(OKGREEN+" .   .       .      :  .   .: ::/  .  .::\."+ENDC)


  traeCryptos()
