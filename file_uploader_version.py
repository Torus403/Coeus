import streamlit as st
import pandas as pd
import yfinance as yf

st.title('Trading Performane Analyzer')
st.write('---')
st.header("Step 1: Upload your historical trading dataset")
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

# STEP 1: UPLOAD THE DATA
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    data = st.dataframe(df)

    # convert the 'Date' column to datetime format and finding min and max dates
    df['BUY DATE'] = pd.to_datetime(df['BUY DATE'])
    df['SELL DATE'] = pd.to_datetime(df['SELL DATE'])
    portfolio_start_date = df['BUY DATE'].min()
    portfolio_end_date = df['SELL DATE'].max()

    ## STEP 2: DISPLAYING OVERVIEW INFORMATION
    portfolio_value = pd.Series(index=['Close'])
    for i in range(0,len(df.index)):
        ticker = df['INSTRUMENT SYMBOL'][i]
        ticker_start_date = df['BUY DATE'][i]
        ticker_end_date = df['SELL DATE'][i]
        tickerDf = yf.Ticker(ticker)
        tickerData = tickerDf.history(start=ticker_start_date,end=ticker_end_date)
        tickerPrices = tickerData['Close']
        ## error management here, if doesnt find stock from yfinance

        # adding the dataframes together
        position_value = tickerPrices*df['QUANTITY'][i]
        portfolio_value = portfolio_value.add(position_value,fill_value=0)

    date_range = pd.date_range(start=portfolio_start_date,end=portfolio_end_date)
    portfolio_value = pd.DataFrame(portfolio_value, index=date_range)
    portfolio_value = portfolio_value.dropna()

    st.write('---')
    st.header('Step 2: Gain an overview of your trading history')
    st.subheader('Portfolio value in $')

    # PART 1: Portfolio value graphs
    st.area_chart(portfolio_value)

    # PART 2: Calculating total returns (overall portfolio and each stock)
    st.text("")
    st.subheader('Portfolio analytics')

    for i in range(0,len(df.index)):
        ticker1 = df['INSTRUMENT SYMBOL'][i]
        tickerReturn1 = ((df['SELL PRICE'][i]-df['BUY PRICE'][i])/df['BUY PRICE'][i])*100
        time_in_portfolio = df['SELL DATE'][i]-df['BUY DATE'][i]
        efficiency = tickerReturn1 / time_in_portfolio.days
        tickerNet = (df['SELL PRICE'][i]-df['BUY PRICE'][i])*df['QUANTITY'][i]
        st.text('Ticker: %s ' % ticker1)
        st.text('- return: %s percent' % round(tickerReturn1, 2))
        st.text('- time in portfolio: %s days' % time_in_portfolio.days)
        st.text('- efficiency (time-weighted return): %s percent per day' % round(efficiency, 2))
        st.text('- net gain / loss for the trade: %s dollars' % int(tickerNet))

































