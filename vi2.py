
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
import operator
# to make the visualization better by only taking the last 100 rows of data
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
formato="{:<20} {:<20} {:<20}"
formato3="{:<20} {:<20} {:<20} {:<20} {:<20}"

porcentaje=6

def check_even(number):

    if float(number[1]) < porcentaje:
        
        return True  

    return False


def trades_(porcentaje,crypto,cantidad_usd,porcentaje_cercania_soporte):

  crypto=crypto+'-USD'

  msft = yf.Ticker(crypto)

  porcentaje=6

  df = msft.history(start="2020-01-01", end='2022-04-22')

  close=df['Close']

  tendencia={}

  SMA10 = talib.MA(close,timeperiod=10)

  SMA50 = talib.MA(close,timeperiod=50)

  cruce=(SMA10-SMA50)*100/SMA50

  #cantidad_usd=1000

  cantidad_btc=0
   
  for ind, val in enumerate(cruce):

    if val>0:
      tendencia[ind]='alcista '+str(round(val,2))
    else:
      tendencia[ind]='bajista '+str(round(val,2))


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


  df['squeeze_on'] = (df['lower_BB'] > df['lower_KC']) & (df['upper_BB'] < df['upper_KC'])

  df['squeeze_off'] = (df['lower_BB'] < df['lower_KC']) & (df['upper_BB'] > df['upper_KC'])

  df['_squeeze_off']=[1000 if s else -1000 for s in df['squeeze_off']]

  df['_squeeze_on']=[500 if s else -500 for s in df['squeeze_on']]

  df['zero']=[0 if s else -0 for s in df['squeeze_off']]

  df[['_squeeze_on','_squeeze_off','zero','value']].plot(figsize=(15,4))

  df['ADX'] = talib.ADX(df['High'],df['Low'],df['Close'], timeperiod=14)

  df['real'] = talib.ROC(df['ADX'], timeperiod=1)


  cantidad_btc=0

  niveles=levels.lista_levels(crypto)
  
  for ind, val in enumerate(df['value']):

    print(OKBLUE+'-----------------------------------'+tendencia[ind]+'-----------------------------------'+ENDC)

    if val >= 0:

      print(df['ADX'][ind],df['ADX'][ind-1])

      if df['ADX'][ind]<df['ADX'][ind-1]:

        color = 'green'

        try:

          print(FAIL+formato.format('VENTA ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)))+ENDC)
          
          if cantidad_btc>0: 

            cantidad_usd=cantidad_btc*float(df['Close'][ind])

            cantidad_btc=0

            print('BALANCE...',str(round(cantidad_usd,2)))

        except:

          pass

      if df['ADX'][ind]>df['ADX'][ind-1]:

        color = 'green'

        try:

          print(OKGREEN+formato.format('COMPRA (2) ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)))+ENDC)
            
          if cantidad_usd>0:

            cantidad_btc=cantidad_usd/float(df['Close'][ind])

            cantidad_usd=0

            print('BALANCE....... '+str(round(cantidad_btc*df['Close'][ind],2)))


          estado='compra'

        except:

          pass


    else:

      if df['ADX'][ind]<df['ADX'][ind-1]:

        color='red'

        try:

          precio_compra=df['Close'][ind]

        except:

          pass


        precio_compra=df['Close'][ind]

        #compra_total=compra_total+20

        if cantidad_usd>0:

          cantidad_btc=cantidad_usd/float(df['Close'][ind])

          cantidad_usd=0

          print(OKGREEN+formato.format('COMPRA (1) ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)))+ENDC)
              
          print('BALANCE '+str(round(cantidad_btc*df['Close'][ind],2)))

        #print('Pendiente ADX',df['real'][ind],df['ADX'][ind])
       
    result = list(map(lambda x: (x,abs(x-df['Close'][ind])*100/x,(x-df['Close'][ind])*100/x), niveles))

    precios=list(filter(check_even, result))

    try:

      soportes=min(precios, key=lambda item: item[1])



    except:

      pass

    data = len(precios)

    tipo=''


    if data>0:

      if soportes[2]>porcentaje_cercania_soporte:


        print(df['Close'][ind],df['Close'][ind-1],(df['Close'][ind]-df['Close'][ind-1])*100/df['Close'][ind])
        if cantidad_btc>0: 

          cantidad_usd=cantidad_btc*float(df['Close'][ind])

          cantidad_btc=0

          print(FAIL+formato.format('VENTA ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)))+ENDC)

          print('BALANCE----',str(round(cantidad_usd,2)))




      if df['Close'][ind]<df['Close'][ind-1]:

        print(WARNING+formato3.format('RESISTENCIA ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)),str(round(soportes[2],3))+'%',str(round(soportes[0],3))+ENDC))
        

      else:

        print(WARNING+formato3.format('SOPORTE ',str(df[df['Close']==df['Close'][ind]].index.values[0])[0:10],str(round(df['Close'][ind],3)),str(round(soportes[2],3))+'%',str(round(soportes[0],3))+ENDC))
        



        


  print('BALANCE USD',cantidad_usd)

  print('BALANCE '+crypto,cantidad_btc*df['Close'][ind])

  #print(cantidad_inicial/df['Close'][ind])
        




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

  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('-config', '-c', dest="crypto", action='store', type=str, default=None)
  parser.add_argument('-monto', '-m', dest="cantidad_usd", action='store', type=str, default=None)
  parser.add_argument('-soporte', '-s', dest="soporte", action='store', type=str, default=None)
  args = parser.parse_args()

  print(args.crypto)

  trades_(0,args.crypto,float(args.cantidad_usd),float(args.soporte))

