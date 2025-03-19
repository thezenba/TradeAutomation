import pandas as pd
import matplotlib.pyplot as plt
from modules.BinanceTraderBot import BinanceTraderBot
from binance.client import Client
from tests.backtestRunner import backtestRunner
from strategies.ut_bot_alerts import *
from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy
from strategies.rsi_strategy import getRsiTradeStrategy
from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.ma_rsi_volume_strategy import getMovingAverageRSIVolumeStrategy

# ------------------------------------------------------------------------
# 🔎 CONFIGURAÇÕES DO BACKTEST 🔎

STOCK_CODE = "BTC"  # Código da Criptomoeda
OPERATION_CODE = "BTCUSDT"  # Código da operação (cripto + moeda)
INITIAL_BALANCE = 100  # Valor de investimento inicial em USDT ou BRL
CANDLE_PERIOD = Client.KLINE_INTERVAL_1HOUR  # Período do candle
CLANDES_RODADOS = 7 * 24  # Número de candles a serem analisados

# Pasta para salvar os resultados
RESULTS_FOLDER = "backtest_results"

# ------------------------------------------------------------------------
# ⏬ FUNÇÃO PARA SALVAR RESULTADOS EM CSV E EXCEL ⏬

def save_results(results, strategy_name):
    """
    Salva os resultados do backtest em arquivos CSV e Excel.
    """
    import os

    # Cria a pasta de resultados, se não existir
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    # Salva a curva de equity em CSV
    equity_curve = results["equity_curve"]
    equity_curve.to_csv(f"{RESULTS_FOLDER}/{strategy_name}_equity_curve.csv", index=False)

    # Salva o histórico de operações em CSV
    trades_history = results["trades_history"]
    trades_history.to_csv(f"{RESULTS_FOLDER}/{strategy_name}_trades_history.csv", index=False)

    # Salva um resumo dos resultados em Excel
    summary = {
        "Estratégia": strategy_name,
        "Balanço Final": results["final_balance"],
        "Lucro/Prejuízo Total": results["profit_amount"],
        "Lucro Percentual": results["profit_percentage"],
        "Total de Operações": results["total_trades"],
        "Operações Vencedoras": results["winning_trades"],
        "Operações Perdedoras": results["losing_trades"],
        "Win Rate": results["win_rate"],
        "Drawdown Máximo": results["max_drawdown"],
        "Sharpe Ratio": results["sharpe_ratio"],
        "Sortino Ratio": results["sortino_ratio"],
    }
    summary_df = pd.DataFrame([summary])
    summary_df.to_excel(f"{RESULTS_FOLDER}/{strategy_name}_summary.xlsx", index=False)

# ------------------------------------------------------------------------
# ⏬ FUNÇÃO PARA GERAR GRÁFICOS ⏬

def plot_equity_curve(results, strategy_name):
    """
    Gera e salva gráficos da curva de equity e drawdown.
    """
    equity_curve = results["equity_curve"]

    plt.figure(figsize=(12, 6))

    # Gráfico da curva de equity
    plt.subplot(2, 1, 1)
    plt.plot(equity_curve["date"], equity_curve["balance"], label="Balanço", color="blue")
    plt.title(f"Curva de Equity - {strategy_name}")
    plt.xlabel("Data")
    plt.ylabel("Balanço")
    plt.legend()

    # Gráfico do drawdown
    plt.subplot(2, 1, 2)
    drawdown = (equity_curve["balance"].cummax() - equity_curve["balance"]) / equity_curve["balance"].cummax()
    plt.plot(equity_curve["date"], drawdown, label="Drawdown", color="red")
    plt.title("Drawdown")
    plt.xlabel("Data")
    plt.ylabel("Drawdown (%)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"{RESULTS_FOLDER}/{strategy_name}_equity_drawdown.png")
    plt.close()

# ------------------------------------------------------------------------
# ⏬ EXECUÇÃO DOS BACKTESTS ⏬

def run_backtests():
    """
    Executa backtests para todas as estratégias e salva os resultados.
    """
    # Inicializa o bot e obtém os dados históricos
    devTrader = BinanceTraderBot(
        stock_code=STOCK_CODE,
        operation_code=OPERATION_CODE,
        traded_quantity=0,
        traded_percentage=100,
        candle_period=CANDLE_PERIOD,
    )
    devTrader.updateAllData()

    # Lista de estratégias a serem testadas
    strategies = [
        ("UT BOTS", utBotAlerts, {"atr_multiplier": 2, "atr_period": 1}),
        ("MA RSI e VOLUME", getMovingAverageRSIVolumeStrategy, {}),
        ("MA ANTECIPATION", getMovingAverageAntecipationTradeStrategy, {"volatility_factor": 0.5, "fast_window": 7, "slow_window": 40}),
        ("MA SIMPLES", getMovingAverageTradeStrategy, {"fast_window": 7, "slow_window": 40}),
        ("RSI", getRsiTradeStrategy, {"low": 30, "high": 70}),
        ("VORTEX", getVortexTradeStrategy, {}),
    ]

    # Executa o backtest para cada estratégia
    all_results = []
    for strategy_name, strategy_function, strategy_params in strategies:
        print(f"\n📊 Executando backtest para: {strategy_name}")
        results = backtestRunner(
            stock_data=devTrader.stock_data,
            strategy_function=strategy_function,
            periods=CLANDES_RODADOS,
            initial_balance=INITIAL_BALANCE,
            verbose=False,
            **strategy_params,
        )

        # Salva os resultados e gera gráficos
        save_results(results, strategy_name)
        plot_equity_curve(results, strategy_name)

        # Adiciona os resultados à lista para comparação
        all_results.append({
            "Estratégia": strategy_name,
            "Balanço Final": results["final_balance"],
            "Lucro Percentual": results["profit_percentage"],
            "Win Rate": results["win_rate"],
            "Drawdown Máximo": results["max_drawdown"],
            "Sharpe Ratio": results["sharpe_ratio"],
        })

    # Salva a comparação de todas as estratégias em um único arquivo Excel
    comparison_df = pd.DataFrame(all_results)
    comparison_df.to_excel(f"{RESULTS_FOLDER}/comparacao_estrategias.xlsx", index=False)
    print(f"\n✅ Comparação de estratégias salva em: {RESULTS_FOLDER}/comparacao_estrategias.xlsx")

# ------------------------------------------------------------------------
# ⏬ EXECUTA O BACKTEST ⏬

if __name__ == "__main__":
    run_backtests()