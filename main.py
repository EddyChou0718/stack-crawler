import yfinance as yf
import pandas as pd
import os

def get_triple_growth(tickers):
    triple_growth_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            q_fin = stock.quarterly_financials
            if q_fin.empty or q_fin.shape[1] < 2:
                continue

            rev = q_fin.loc['Total Revenue']
            gp = q_fin.loc['Gross Profit']
            op = q_fin.loc['Operating Income']
            ni = q_fin.loc['Net Income Common Stockholders']

            # 計算兩季數據
            m0 = {'g': gp[0]/rev[0], 'o': op[0]/rev[0], 'n': ni[0]/rev[0]}
            m1 = {'g': gp[1]/rev[1], 'o': op[1]/rev[1], 'n': ni[1]/rev[1]}

            if m0['g'] > m1['g'] and m0['o'] > m1['o'] and m0['n'] > m1['n']:
                triple_growth_list.append({
                    'Ticker': ticker,
                    'Gross_Margin': f"{m0['g']:.2%}",
                    'Op_Margin': f"{m0['o']:.2%}",
                    'Net_Margin': f"{m0['n']:.2%}"
                })
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            
    return pd.DataFrame(triple_growth_list)

if __name__ == "__main__":
    # 你可以在這裡定義想要掃描的股票池
    targets = ['2330.TW', '2317.TW', '2454.TW', 'AAPL', 'NVDA', 'MSFT', 'GOOG']
    df = get_triple_growth(targets)
    
    print(df)
    # 儲存結果
    df.to_csv("result.csv", index=False)
