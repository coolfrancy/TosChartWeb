def data(cleaned_data_path):
    import pandas as pd
    import os
    import matplotlib.pyplot as plt
    from TosChart.ai import gpt_summary
    
    
    chart_path = os.path.join(os.getcwd(), "web", "static", "graph.png")  


    #refactor the who code to the new database


    #this will give you a list of stocks from the folder
    stocks=os.listdir(cleaned_data_path)

    lists=[]
    ####
    ##cleans all the strategy file so they match the same format
    ###
    for stock in stocks:
        try:
            dt=pd.read_csv(cleaned_data_path+'/'+stock)
            dt.drop(columns=['Price','Amount','Position','P/L', 'Unnamed: 9','Side'], inplace=True)

            symb=dt.columns[0]
            date=dt.columns[2]

            ####
            for ind,num in enumerate(dt[date]):
                if ind%2!=0:
                    if ind>0:
                        dt.loc[ind-1, date]+='-'+num

                #trying somethin

            dt['Trade P/L']=dt['Trade P/L'].shift(periods=-1)

            for i,id in enumerate(dt[symb]):
                if int(id)%2==0:
                    dt.drop(i, inplace=True)

            dt.dropna(inplace=True)
            hold=[]

            #creating holding period because i want to know how long i held the stock
            for index,date in enumerate(dt[date]):
                open, close=date.split('-')
                hold.append(pd.to_datetime(close)-pd.to_datetime(open))
            dt['Holding Time']=hold

            g=dt.columns[0].split()
            dt['Id']=g[1]
            dt.drop(columns=symb, inplace=True)
            lists.append(dt)
        except Exception as e:
            print(e)
            continue

    df=pd.concat(lists)
    df['Trade P/L'] = df['Trade P/L'].str.replace(r'[\$,]', '', regex=True).replace(r'\((\d+(\.\d+)?)\)', r'-\1', regex=True)
    df['Trade P/L']=pd.to_numeric(df['Trade P/L'])

    sell=[]
    for num in df['Date/Time']:
        b, s=num.split('-')
        sell.append(s)
    df['Date']=sell

    # Ensure 'Date' is in datetime format and sort by date
    df = df.assign(Date=pd.to_datetime(df['Date'])).sort_values('Date')


    # Calculate cumulative P/L
    df['Trade Sum'] = df['Trade P/L'].cumsum()

    # Plot and save the line graph
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Trade Sum'], marker='o', label='Cumulative P/L', color='blue')
    plt.axhline(0, color='red', linestyle='--', label='Break-Even Line')
    plt.title('Cumulative Profit/Loss Over Time')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Profit/Loss')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig(chart_path)

    #calculates winners and losers
    wins = df[df['Trade P/L'] > 0]['Trade P/L']
    losses = df[df['Trade P/L'] < 0]['Trade P/L']

    count_win, count_loss = len(wins), len(losses)
    sum_win, sum_loss = wins.sum(), losses.sum()


    average_win=sum_win/count_win
    average_loss=sum_loss/count_loss
    amount_ratio=round(average_win/abs(average_loss), 2)
    win_loss_percentage=round((count_win/(count_loss+count_win))*100, 2)

    #gives you information on data
    desc_dict=df['Trade P/L'].describe().to_dict()
    description=[]
    for name,value in desc_dict.items():
        if'%' not in name:
            description.append(name+' '+str(value))

    description=', '.join(description)

    summary=gpt_summary(description, str(win_loss_percentage), str(amount_ratio))

    return {
        'description':description,
        'win':count_win,
        'loss':count_loss,
        'ratio':amount_ratio,
        'percentage':win_loss_percentage,
        'summary':summary
        } 



if __name__=='__main__':
    data('/workspaces/TosChartWeb/TosChart/cleaned_data')





