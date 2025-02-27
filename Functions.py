import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")
from scipy import stats

riskfree_rate = 0.015
start_date = '2016-01-01'
end_date = '2025-01-01'

######################################################################################################################################


def obtener_datos(tickers, start_date, end_date):
    datos = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return datos

######################################################################################################################################


def calcular_rendimientos(datos):
    rendimientos = datos.pct_change().dropna()
    return rendimientos

######################################################################################################################################


def selector_tickers(profile):

    tickers_aggressive   = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'TSLA']
    tickers_moderate     = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'TSLA','PG', 'KO', 'JNJ','PEP', 'WMT']
    tickers_conservative = ['SPY','BIL']

    if profile == 'Aggressive':
        tickers = tickers_aggressive
    
    elif profile =='Moderate':
        tickers = tickers_moderate

    else:
        tickers = tickers_conservative

    return tickers


def simular_portafolios(rendimientos, num_simulaciones=10000):
    num_activos = len(rendimientos.columns)
    resultados = np.zeros((num_simulaciones, 3))  # columnas: [rendimiento, volatilidad, ratio de Sharpe]
    pesos_portafolios = np.zeros((num_simulaciones, num_activos))
    
    for i in range(num_simulaciones):
       
        pesos = np.random.random(num_activos)
        pesos /= np.sum(pesos)
        
        # Calcular el rendimiento y volatilidad del portafolio
        rendimiento_portafolio = np.sum(pesos * rendimientos.mean()) * 252  # anualizado
        volatilidad_portafolio = np.sqrt(np.dot(pesos.T, np.dot(rendimientos.cov() * 252, pesos)))  # anualizado
        
        
        ratio_sharpe = (rendimiento_portafolio - riskfree_rate) / volatilidad_portafolio
        
        # Guardar los resultados en el array predefinido
        resultados[i, 0] = rendimiento_portafolio
        resultados[i, 1] = volatilidad_portafolio
        resultados[i, 2] = ratio_sharpe
        pesos_portafolios[i] = pesos
    
    return resultados, pesos_portafolios


######################################################################################################################################


def optimize_portfolio(tickers, start_date, end_date, num_simulaciones=10000):
    # Obtener datos
    datos = obtener_datos(tickers, start_date, end_date)
    
    # Verificar que los datos no estén vacíos
    if datos.empty:
        print(f"No se pudieron obtener datos para los tickers: {tickers}")
        return
    
    # Calcular rendimientos
    rendimientos = calcular_rendimientos(datos)
    
    # Realizar la simulación de portafolios
    resultados, pesos_portafolios = simular_portafolios(rendimientos, num_simulaciones)
    
    # Convertir los resultados a un DataFrame
    sim_out_df = pd.DataFrame(resultados, columns=['Portfolio_Return', 'Volatility', 'Sharpe_Ratio'])
    
 
    
    # Imprimir los resultados


    return datos,rendimientos,resultados,sim_out_df, pesos_portafolios




######################################################################################################################################


def sharpe_portfolio(tickers):

    print('Establishing the optimal portfolio based on your preferences')

    datos, rendimientos, resultados, sim_out_df, pesos_portafolios= optimize_portfolio(tickers, start_date, end_date)

    idx_max_sharpe = np.argmax(resultados[:, 2])

    max_sharpe_port_stats = sim_out_df.iloc[idx_max_sharpe]

    optimal_weights = pesos_portafolios[idx_max_sharpe].round(2)

    return max_sharpe_port_stats, optimal_weights


######################################################################################################################################


def portfolio_combinations (stats):

    pesos = np.arange(0, 1.01, 0.01)
    df_combinaciones = pd.DataFrame({
    'Portfolio_Weight': pesos,
    'RF_Rate_Weight': 1 - pesos})

    df_combinaciones['Expected Return'] = stats[0] * df_combinaciones['Portfolio_Weight'] + riskfree_rate * df_combinaciones['RF_Rate_Weight']
    df_combinaciones['Volatility']      = stats[1] * df_combinaciones['Portfolio_Weight']

    return df_combinaciones


######################################################################################################################################


def investor_profile_score():
    
    score = 0
    
    print("Investor Profile Questionnaire")
    
    
    print("\n1. What is your primary objective when investing?")
    print("(1) Saving for retirement")
    print("(2) Generating passive income")
    print("(3) Increasing the value of my wealth")
    objective = int(input("Enter the corresponding number: "))
    score += objective
    
    
    print("\n2. How long do you plan to keep your investment?")
    print("(1) Less than 1 year")
    print("(2) Between 1 and 2 years")
    print("(3) Between 2 and 3 years")
    print("(4) More than 4 years")
    horizon = int(input("Enter the corresponding number: "))
    score += horizon
    
    
    print("\n3. What would you do if your investment loses 20% of its value in the short term?")
    print("(1) Sell immediately")
    print("(2) Hold the investment")
    print("(3) Buy more")
    risk = int(input("Enter the corresponding number: "))
    score += risk
    
    
    print("\n4. How familiar are you with investments?")
    print("(1) Very little")
    print("(2) Somewhat familiar")
    print("(3) Very familiar")
    knowledge = int(input("Enter the corresponding number: "))
    score += knowledge
    
    
    print("\n5. What is your approximate annual income?")
    print("(1) Less than $25,000")
    print("(2) Between $25,000 and $75,000")
    print("(3) More than $75,000")
    income = int(input("Enter the corresponding number: "))
    score += income
    
    
    if score <= 8:
        profile = "Conservative"
    elif score <= 14:
        profile = "Moderate"
    else:
        profile = "Aggressive"
    
    print(f"\nYour investor profile is: {profile}")

    return score, profile, horizon


def portfolio_seleccionado_cliente(df_portfolios):

    df_portfolios['Expected Return'] = round(df_portfolios['Expected Return'],2)*100
    df_portfolios['Volatility']      = round(df_portfolios['Volatility'],2)*100

    max_vol = df_portfolios['Volatility'].max()
    min_vol = df_portfolios['Volatility'].min()
    
    print(f'Choose maximum volatility that you are comfortable with {max_vol} and {min_vol}')
    selected_return = int(input(""))

    df_portfolios['Difference'] = abs(df_portfolios['Volatility'] - selected_return)

    selected_index = df_portfolios['Difference'].idxmin()
    
    expected_return      = df_portfolios.loc[selected_index, 'Expected Return']
    volatility           = df_portfolios.loc[selected_index, 'Volatility']
    portfolio_weight     = df_portfolios.loc[selected_index, 'Portfolio_Weight']
    portfolio_volatility = df_portfolios.loc[selected_index, 'RF_Rate_Weight']

    return expected_return,volatility,portfolio_weight,portfolio_volatility


######################################################################################################################################

def client_portfolio(start_date, end_date,returns,optimal_weights,portfolio_client,riskfree_rate):

    start_date = pd.to_datetime(start_date)
    end_date   = pd.to_datetime(end_date)

    
    riskfree_client = 1-portfolio_client

    optimal_weights = [portfolio_client * weight for weight in optimal_weights]

    client_portfolio = returns.loc[start_date:end_date]

    client_portfolio['Portfolio_DailyReturn'] = client_portfolio.mul(optimal_weights).sum(axis=1)

    client_portfolio['Portfolio_DailyReturn'] = client_portfolio['Portfolio_DailyReturn'].apply(lambda x: x + riskfree_client*riskfree_rate/365)

    client_portfolio['Portfolio_TotalReturn'] = client_portfolio['Portfolio_DailyReturn'].cumsum()

    total_return = client_portfolio['Portfolio_TotalReturn'].iloc[-1]

    return total_return


