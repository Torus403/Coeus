## COEUS: app to analyze trading performance

## IMPORTS
import streamlit as st
import altair as alt
import pandas as pd
import yfinance as yf
import numpy as np
from scipy import stats
from datetime import timedelta

# WEBSITE

# Intro layout
st.title('**Coeus - Trading Performance Analyzer**')
st.write('---')

st.header('*INTRODUCTION*')
st.subheader('Why Coeus?')
st.markdown('Coeus is the Greek Titan of Intelligence, we hope that by analyzing and gaining insights into your portfolio, you may gain some of insight into your trading performance')
st.subheader('What is Coeus?')
st.markdown('Coeus is an app which quantifies your trading performance, and allows you to gain insights into how well you trade, and finds ways you can optimize your portfolio')
st.subheader('How does it work?')
st.markdown('By analyzing your trading data, we can quantify the levels of risk, the returns, the level of diversity and much more about your portfolio. This allows us to combine all this data into a single number, the Indicator. You can then observe this value over time to see if your trades are improving ')
st.write('---')

# Input layout
st.header('*INPUT*')
st.subheader('How to input your trading data')
st.markdown('Step 1: Fetch your trading data from your broker. This must be in an excel sheet form')
st.markdown('Step 2: Convert your data by following the example below. Be careful not to include the currency in the excel sheet, only the numerical values. And the date must be in UK format: dd/mm/yyyy. And the symbol must be all caps')
example_input = pd.DataFrame(data={'Instrument name': ['Tesla Inc.'], 'Instrument symbol': ['TSLA'], 'Buy price': ['109.32'], 'Buy date': ['13/03/2020'], 'Sell price': ['274.88'], 'Sell date': ['11/08/2020'], 'Quantity': ['100']})
st.dataframe(example_input)
st.markdown('Step 3: Transform your excel sheet into the CSV format, and upload it using the button below')
st.markdown('Example of CSV input')
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
st.write('---')

# Overview layout
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    ## CALCULATIONS
    # convert the 'Date' column to datetime format and finding min and max dates
    df['Buy date'] = pd.to_datetime(df['Buy date'])
    df['Sell date'] = pd.to_datetime(df['Sell date'])
    portfolio_start_date = df['Buy date'].min()
    portfolio_end_date = df['Sell date'].max()

    # Portfolio value
    portfolio_value = pd.Series(index=['Close'])
    for i in range(0,len(df.index)):
        ticker = df['Instrument symbol'][i]
        ticker_start_date = df['Buy date'][i]
        ticker_end_date = df['Sell date'][i]
        tickerDf = yf.Ticker(ticker)
        tickerData = tickerDf.history(start=ticker_start_date, end=ticker_end_date)
        tickerPrices = tickerData['Close']
        ## error management here, if doesnt find stock from yfinance
        position_value = tickerPrices*df['Quantity'][i]
        portfolio_value = portfolio_value.add(position_value, fill_value=0)
    date_range = pd.date_range(start=portfolio_start_date, end=portfolio_end_date)
    portfolio_value = pd.DataFrame(portfolio_value, index=date_range)
    portfolio_value = portfolio_value.dropna()

    # Overall portfolio performance metrics
    total_sell = sum(df['Sell price']*df['Quantity'])
    total_buy = sum(df['Buy price']*df['Quantity'])
    profit_loss = total_sell - total_buy

    total_returns = ((total_sell - total_buy)/total_buy)*100

    #benchmark = yf.Ticker('^GSPC')
    #benchmark_values = benchmark.history(start=portfolio_start_date, end=portfolio_end_date)
    #benchmark_ret1 = benchmark_values['Close'].pct_change()
    #benchmark_ret = benchmark_ret1.to_numpy()
    #st.write(benchmark_ret)
    #port_ret1 = portfolio_value.pct_change()
    #port_ret = port_ret1.to_numpy()
    #st.write(port_ret)
    #covariance = np.cov(port_ret, benchmark_ret)
    #portfolio_beta = covariance[0, 1]/covariance[1, 1]
    #treynor_measure = total_returns / portfolio_beta

    #portfolio_standard_deviation = portfolio_value.std()
    #sharpe_ratio = total_returns / portfolio_standard_deviation

    #beta_jensen =
    #jensen_measure = (total_returns - risk_free_rate - beta_jensen)*100

    # Asset returns for bar chart
    d = list()
    for i in range(0, len(df.index)):
        ticker = df['Instrument symbol'][i]
        tickerReturns = ((df['Sell price'][i]-df['Buy price'][i])/df['Buy price'][i])*100
        d.append(tickerReturns)
    asset_returns = pd.DataFrame(data=d, index=df['Instrument name'])



    # Analysis layout OVERVIEW
    st.header('*ANALYSIS*')
    st.subheader('Overview')

    st.markdown('List of trades:')
    st.dataframe(df)

    st.markdown('Portfolio valuation over time:')
    st.area_chart(portfolio_value)
    # make a chart with layers for each stock, use altair

    st.markdown('Performance metrics:')
    st.text('Profit-Loss: %s dollars' % int(profit_loss))
    st.text('Total rate of return: %s percent' % round(total_returns,1))
    #st.text('Treynor measure: %s' % treynor_measure)
    #st.text('Sharpe ratio: %s' % sharpe_ratio)
    #st.text('Jensen measure: %s percent' % jensen_measure)

    st.markdown('Asset returns:')
    st.bar_chart(asset_returns)

    # Analysis layout ASSETS
    st.subheader('Asset analysis')
    option2 = st.selectbox('Asset', df['Instrument name'])
    row_index = df[df['Instrument name'] == option2].index
    instrument_symbol = df['Instrument symbol'][row_index].to_list()
    start_date2 = df['Buy date'][row_index].to_list()
    end_date2 = df['Sell date'][row_index].to_list()
    tickerData2 = yf.Ticker(instrument_symbol[0])  # Get ticker data
    tickerDf2 = tickerData2.history(start=start_date2[0], end=end_date2[0])  # Get the historical prices for the ticker

    st.markdown('Information:')
    string_summary = tickerData2.info['longBusinessSummary']
    st.markdown('%s' % string_summary)

    st.markdown('Return:')

    st.markdown('Benchmark S&P 500 comparison:')
    benchmarkData = yf.Ticker('^GSPC')
    benchmarkDf = benchmarkData.history(start=start_date2[0], end=end_date2[0])

    d = {'ticker': ((tickerDf2['Close'] - tickerDf2['Close'][0]) / tickerDf2['Close'][0]) * 100,
     'benchmark': ((benchmarkDf['Close'] - benchmarkDf['Close'][0]) / benchmarkDf['Close'][0]) * 100}
    benching = pd.DataFrame(data=d)

    tickerReturns = ((tickerDf2['Close'][-1] - tickerDf2['Close'][0]) / tickerDf2['Close'][0]) * 100
    tickerReturns = round(tickerReturns, 3)
    benchmarkReturns = ((benchmarkDf['Close'][-1] - benchmarkDf['Close'][0]) / benchmarkDf['Close'][0]) * 100
    benchmarkReturns = round(benchmarkReturns, 3)
    st.text('The stock you choose made %s percent returns over the time period' % tickerReturns)
    st.text('The benchmark (S&P500) made %s percent returns over the time period' % benchmarkReturns)

    # Plotting the data
    st.line_chart(benching)

    






























