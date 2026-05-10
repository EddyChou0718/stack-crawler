import yfinance as yf
import pandas as pd
import time

def get_taiwan_stock_list():
    """
    獲取台股上市上櫃清單 (示範用途，建議手動維護一個清單以節省 Actions 時間)
    這裡先列出幾支指標股作為範例，若要全市場掃描，建議分批處理。
    """
    # 建議從證交所抓取，這裡先以範例清單代替
    return ['2330.TW', '2317.TW', '2454.TW', '2308.TW', '2382.TW', '3231.TW', '2303.TW', '8069.TWO']

def get_triple_growth_tw(tickers):
    results = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # 台股強烈建議抓取 Quarterly Financials
            q_fin = stock.quarterly_financials
            
            if q_fin is None or q_fin.empty or q_fin.shape[1] < 2:
                continue
            
            # yfinance 的 index 名稱有時會因版本變動，這裡加入容錯處理
            idx = q_fin.index
            rev_label = 'Total Revenue'
            gp_label = 'Gross Profit'
            op_label = 'Operating Income'
            ni_label = 'Net Income Common Stockholders'
            
            # 檢查必要欄位是否存在
            if not all(label in idx for label in [rev_label, gp_label, op_label, ni_label]):
                continue

            rev = q_fin.loc[rev_label]
            gp = q_fin.loc[gp_label]
            op = q_fin.loc[op_label]
            ni = q_fin.loc[ni_label]

            # 計算最近兩季 (Q0: 最新, Q1: 前一季)
            m0 = {'g': gp[0]/rev[0], 'o': op[0]/rev[0], 'n': ni[0]/rev[0]}
            m1 = {'g': gp[1]/rev[1], 'o': op[1]/rev[1], 'n': ni[1]/rev[1]}

            # 三率三升邏輯
            if m0['g'] > m1['g'] and m0['o'] > m1['o'] and m0['n'] > m1['n']:
                results.append({
                    '股票代碼': ticker.replace('.TW', '').replace('.TWO', ''),
                    '最新季度': q_fin.columns[0].strftime('%Y-%Q'),
                    '毛利率(%)': round(m0['g'] * 100, 2),
                    '營益率(%)': round(m0['o'] * 100, 2),
                    '淨利率(%)': round(m0['n'] * 100, 2)
                })
            
            # 避免被 Yahoo 封鎖 IP，稍微停頓
            time.sleep(0.5)
            
        except Exception as e:
            print(f"無法分析 {ticker}: {e}")
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    target_list = get_taiwan_stock_list()
    df_result = get_triple_growth_tw(target_list)
    
    # 按照營益率排序
    if not df_result.empty:
        df_result = df_result.sort_values(by='營益率(%)', ascending=False)
    
    print(df_result)
    df_result.to_csv("tw_stock_triple_growth.csv", index=False, encoding="utf-8-sig")
