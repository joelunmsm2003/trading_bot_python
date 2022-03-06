
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
# to make the visualization better by only taking the last 100 rows of data

msft = yf.Ticker("BTC-USD")
print(msft.info)

df = msft.history(start="2021-01-01", end='2022-02-28')



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




df['squeeze_on'] = (df['lower_BB'] > df['lower_KC']) & (df['upper_BB'] < df['upper_KC'])
df['squeeze_off'] = (df['lower_BB'] < df['lower_KC']) & (df['upper_BB'] > df['upper_KC'])

#df = df[-120:]

print(df['squeeze_off'])

df['_squeeze_off']=[1000 if s else -1000 for s in df['squeeze_off']]

df['_squeeze_on']=[500 if s else -500 for s in df['squeeze_on']]

df['zero']=[0 if s else -0 for s in df['squeeze_off']]

df[['_squeeze_on','_squeeze_off','zero','value']].plot(figsize=(15,4))

#luna 12

df['ADX'] = talib.ADX(df['High'],df['Low'],df['Close'], timeperiod=12)
#df[['value']].plot(figsize=(15,4))

df['real'] = talib.ROC(df['ADX'], timeperiod=14)



primera=df['real'][-1]

df[['real']].plot(figsize=(15,4))

plt.savefig('value SQZ.png')



# extract only ['Open', 'High', 'Close', 'Low'] from df
ohcl = df[['Open', 'High', 'Close', 'Low']]

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


if primera<-10 and color=='red':

  print('compra')

if primera<-10 and color=='verde':

  print('venta')




def trades_(adx_fuerza):

  estado='rango'

  ganancia_total=0

  for ind, val in enumerate(df['value']):

    if df['real'][ind]<-adx_fuerza:
      if val >= 0:
        color = 'green'

        if estado=='compra':
          precio_venta=df['Close'][ind]

          

          ganancia=(precio_venta-precio_compra)*100/precio_compra

          print('ganancia---------------------',ganancia)
          print('venta',df['Close'][ind],precio_compra)
          print(df[df['Close']==df['Close'][ind]].index.values[0])
          #print('Pendiente ADX',df['real'][ind])


          ganancia_total=ganancia_total+ganancia

          estado='venta'


        if val > df['value'][ind-1]:
          pass
      else:
        color = 'maroon'
        if val < df['value'][ind-1]:
          color='red'


          if estado=='venta' or estado=='rango':
            precio_compra=df['Close'][ind]

            estado='compra'

          precio_compra=df['Close'][ind]

          print('-----------compra',df['Close'][ind])
          print(df[df['Close']==df['Close'][ind]].index.values[0])


  print('ganancia_total',ganancia_total)


    
  # add 2 subplots: 1. bars, 2. crosses
  apds = [mpf.make_addplot(df['value'], panel=1, type='bar', color=colors, alpha=0.8, secondary_y=False),
          mpf.make_addplot([0] * len(df), panel=1, type='scatter', marker='x', markersize=50, color=['gray' if s else 'black' for s in df['squeeze_off']], secondary_y=False)]

  # plot ohcl with subplots
  fig, axes = mpf.plot(ohcl, 
                volume_panel = 2,
                figratio=(2,1),
                figscale=1, 
                type='candle', 
                addplot=apds,
                returnfig=True)

  #plt.show()
  #plt.savefig('SQZ.png')


trades_(12)

'''
for i in range(0,20):
  print(i)
  trades_(i)

'''