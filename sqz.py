import pandas as pd
import numpy as np
import yfinance
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt



def value(c):

  ticker = yfinance.Ticker(c)
  
  df = ticker.history(interval="1d",start="2021-07-15",end="2022-07-15")
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


  return df['value']