from Functions import *



### Obtenemos el Perfil de Riesgo, su Puntuacion y su Horizonte ###

score, profile, horizon = investor_profile_score()

### Seleccionamos los Tickers apropiados ###

tickers = selector_tickers(profile)

### Obtenemos el Portafolio ###

datos,returns,resultados,sim_out_df, pesos_portafolios = optimize_portfolio(tickers,start_date,end_date)

optimal_stats, optimal_weights = sharpe_portfolio(tickers)

### Obtenemos todas las combinaciones del Portfolio Optimo y la Tasa Libre de Riesgo ###

df_portfolios = portfolio_combinations(optimal_stats)

### Black-Litterman ###

expected_return_client, volatility_client,portfolio_client,riskfree_client = portfolio_seleccionado_cliente(df_portfolios)

### Total Return ###

start_date = '2023-12-31'
end_date = '2024-12-31'

total_return = client_portfolio(start_date,end_date,returns,optimal_weights,portfolio_client,riskfree_rate)
total_return = round(total_return*100,2)

print()
print(f'Expected Return: {expected_return_client}')
print()
print(f'Expected Volatility: {volatility_client}')
print()
print(f'You are investing in the following stocks: {tickers}')
print()
print(f'These will be distributed with the following weight: {portfolio_client}')
print()
print(f'And the rest that is {riskfree_client} will be allocated to a Bond known as Risk Free')
print()
print(f'This Portfolio has a Sharpe Ratio of: {round(optimal_stats[2],2)}')
print()
print(f'Because your Investor Profile is {profile}')
print()
print(f'The total return of your portfolio between {start_date} and {end_date} was {total_return}%')




