import pandas as pd
import numpy as np
import yfinance
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

def lista_levels(name):

	ticker = yfinance.Ticker(name)
	
	df = ticker.history(interval="1d",start="2021-07-15",end="2022-07-15")

	df['Date'] = pd.to_datetime(df.index)
	df['Date'] = df['Date'].apply(mpl_dates.date2num)

	df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]


	def isSupport(df,i):
	  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] \
	  and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

	  return support

	def isResistance(df,i):
	  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] \
	  and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2] 

	  return resistance

	levels = []

	for i in range(2,df.shape[0]-2):
	  if isSupport(df,i):
	    levels.append(df['Low'][i])
	  elif isResistance(df,i):
	    levels.append(df['High'][i])


	return levels