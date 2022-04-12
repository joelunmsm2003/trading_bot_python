import talib
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import numpy as np

msft = yf.Ticker("BTC-USD")
print(msft.info)

df = msft.history(start="2021-01-01", end='2022-02-26', interval="4h")


df['MA'] = talib.SMA(df['Close'],20)
#hist[['Close','MA']].plot(figsize=(15,4))
#hist['RSI'] = talib.RSI(hist['Close'], timeperiod=14)
df['ADX'] = talib.ADX(df['High'],df['Low'],df['Close'], timeperiod=14)

print(df['ADX'].values)
df[['Close','ADX']].plot(figsize=(15,4))
plt.show()
plt.savefig('SMA.png')

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

# check for 'squeeze'

df['squeeze_on'] = (df['lower_BB'] > df['lower_KC']) & (df['upper_BB'] < df['upper_KC'])
df['squeeze_off'] = (df['lower_BB'] < df['lower_KC']) & (df['upper_BB'] > df['upper_KC'])

# buying window for long position:
# 1. black cross becomes gray (the squeeze is released)
long_cond1 = (df['squeeze_off'][-2] == False) & (df['squeeze_off'][-1] == True) 

print(df['squeeze_on'][-2])
print(df['squeeze_on'][-1])
print(df['squeeze_on'][0])
print(df['squeeze_on'][1])
print(df['squeeze_on'][2])
print('long_cond1',long_cond1)
# 2. bar value is positive => the bar is light green k
long_cond2 = df['value'][-1] > 0
enter_long = long_cond1 and long_cond2


# buying window for short position:
# 1. black cross becomes gray (the squeeze is released)
short_cond1 = (df['squeeze_off'][-2] == False) & (df['squeeze_off'][-1] == True) 
# 2. bar value is negative => the bar is light red 
short_cond2 = df['value'][-1] < 0
enter_short = short_cond1 and short_cond2


'''
crypto='solana'
url='http://app01.comunica7.com:5500/api/v1/historial/?criptomoneda='+crypto+'&format=json'

data=requests.get(url)

historico=json.loads(data.text)['results']




def takeSecond(elem):
    return elem['price']

def getPrecio(n):
    return n['price']

def getFecha(n):
    return n['fecha']
#print(historico.sort(key=takeSecond))

prices=list(map(getPrecio, historico))

fechas=list(map(getFecha, historico))

data = {'price': prices,'fecha':fechas}

df = pd.DataFrame(data,columns=['price','fecha'])

df['fecha'] = pd.to_datetime(df['fecha'])

df = df.set_index('fecha')

print(df)

fig, axs = plt.subplots(2)
fig.suptitle(crypto)
plt.xticks(rotation=90)

r=2000

df['rsi'] = talib.RSI(df['price'], timeperiod=r)


print('RSI',df['rsi'])
 
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
axs[0].plot(df['rsi'])
axs[1].plot(df['price'])

plt.gcf().autofmt_xdate() # Rotation
plt.show()
plt.savefig('rsi'+str(r)+'.png')



#df.to_csv("data.csv")

'''