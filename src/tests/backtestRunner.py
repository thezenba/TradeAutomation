import numpy as np
import pandas as pd
from datetime import datetime

def backtestRunner(
    stock_data: pd.DataFrame, 
    strategy_function, 
    strategy_instance=None, 
    periods=730, 
    initial_balance=100, 
    commission=0.001,  # 0.1% por operação
    slippage=0.0005,   # 0.05% de slippage
    risk_per_trade=1,  # 1% de risco por operação
    stop_loss=0.10,    # 10% de stop loss
    take_profit=0.20,  # 20% de take profit
    allow_short=False, # Permitir venda a descoberto
    **strategy_kwargs
):
    """
    Executa um backtest de qualquer estratégia com proteção de balanço
    
    Parâmetros:
    -----------
    stock_data : pd.DataFrame
        DataFrame com dados históricos do ativo, deve conter 'close_price' e preferencialmente 'date'
    strategy_function : function
        Função que implementa a estratégia de trading
    strategy_instance : object, optional
        Instância opcional para estratégias baseadas em classes
    periods : int
        Número de períodos para o backtest (padrão: 30)
    initial_balance : float
        Saldo inicial (padrão: 1000)
    commission : float
        Taxa de corretagem por operação (padrão: 0.1%)
    slippage : float
        Estimativa de deslizamento de preço por operação (padrão: 0.05%)
    risk_per_trade : float
        Percentual do capital a arriscar por operação (padrão: 1%)
    stop_loss : float
        Percentual de stop loss (padrão: 10%)
    take_profit : float
        Percentual de take profit (padrão: 20%)
    allow_short : bool
        Permitir posições vendidas a descoberto (padrão: False)
    **strategy_kwargs : dict
        Argumentos adicionais para a estratégia
    
    Retorna:
    --------
    dict
        Dicionário com resultados do backtest e detalhes das operações
    """
    def calculate_trade_size(balance, risk_per_trade, stop_loss):
        """
        Calcula o tamanho da posição com proteção contra balanço negativo
        """
        if balance <= 0:
            return 0
        
        potential_trade_size = balance * risk_per_trade / stop_loss
        max_trade_size = min(potential_trade_size, balance)
        
        return max(0, max_trade_size)

    def safe_trade_profit(balance, trade_size, price_change, transaction_cost):
        """
        Calcula o lucro da operação garantindo que não torne o balanço negativo
        """
        trade_profit = trade_size * price_change - transaction_cost
        max_loss = balance
        return max(trade_profit, -max_loss)

    # Verificar se o DataFrame tem a coluna necessária
    required_columns = ["close_price"]
    for col in required_columns:
        if col not in stock_data.columns:
            raise ValueError(f"O DataFrame deve conter a coluna '{col}'")
    
    # Verificar se há coluna de data para indexação
    if "date" in stock_data.columns:
        has_date = True
        stock_data = stock_data.set_index("date") if stock_data.index.name != "date" else stock_data
    else:
        has_date = False
        print("⚠️ Aviso: Não foi encontrada coluna 'date'. Usando índice numérico.")
    
    # Determinar períodos mínimos requeridos
    min_required_periods = max(
        strategy_kwargs.get("slow_window", 40) + 20,
        strategy_kwargs.get("min_periods", 0)
    )
    
    # Preparar os dados
    stock_data = stock_data[-max(periods, min_required_periods):].copy().reset_index()
    stock_data.dropna(inplace=True)
    
    if len(stock_data) < min_required_periods:
        print(f"⚠️ Aviso: Apenas {len(stock_data)} períodos restantes após remover NaN. Pode não ser suficiente para análise.")
    
    # Inicializar variáveis
    balance = initial_balance
    initial_capital = initial_balance
    position = 0  # 0 = sem posição, 1 = comprado, -1 = vendido (se allow_short for True)
    entry_price = 0
    trade_size = 0
    last_signal = None
    max_balance = initial_balance
    min_balance = initial_balance
    max_drawdown = 0
    
    # Histórico de balanço e operações
    equity_curve = []
    trades_history = []
    daily_returns = []
    current_stop_loss = 0
    current_take_profit = 0
    
    print(f"📊 Iniciando backtest da estratégia: {strategy_function.__name__}")
    print(f"🔹 Balanço inicial: ${balance:.2f}")
    
    for i in range(1, len(stock_data)):
        # Parar se o balanço estiver zerado
        if balance <= 0:
            print("🚨 Balanço zerado. Encerrando backtest.")
            break
        
        current_data = stock_data.iloc[:i+1].copy()
        
        # Obter data da entrada se disponível
        current_date = current_data.iloc[-1]["date"] if has_date else i
        current_price = current_data.iloc[-1]["close_price"]
        
        # Adicionar balanço atual ao histórico
        equity_curve.append({"date": current_date, "balance": balance, "price": current_price})
        
        # Verificar stop loss e take profit para posições abertas
        if position != 0:
            if position == 1:  # Posição comprada
                stop_triggered = current_price <= current_stop_loss
                profit_triggered = current_price >= current_take_profit
            else:  # Posição vendida
                stop_triggered = current_price >= current_stop_loss
                profit_triggered = current_price <= current_take_profit
            
            # Fechar posição se atingir stop loss ou take profit
            if stop_triggered or profit_triggered:
                exit_reason = "stop_loss" if stop_triggered else "take_profit"
                
                # Calcular resultado da operação
                if position == 1:
                    price_change = (current_price - entry_price) / entry_price
                else:
                    price_change = (entry_price - current_price) / entry_price
                
                # Considerar custos de transação
                transaction_cost = trade_size * (commission + slippage)
                trade_profit = safe_trade_profit(balance, trade_size, price_change, transaction_cost)
                balance += trade_profit
                
                # Registrar operação
                trades_history.append({
                    "entry_date": entry_date,
                    "exit_date": current_date,
                    "position": "long" if position == 1 else "short",
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "exit_reason": exit_reason,
                    "trade_size": trade_size,
                    "profit_pct": price_change * 100,
                    "profit_amount": trade_profit,
                    "balance_after": balance
                })
                
                position = 0
                trade_size = 0
                print(f"🚫 {exit_reason.upper()} acionado em {current_date}: {exit_reason} em ${current_price:.2f}, Lucro/Perda: ${trade_profit:.2f}")
        
        # Obter sinal da estratégia
        if strategy_instance:
            signal = strategy_function(strategy_instance, current_data, **strategy_kwargs)
        else:
            signal = strategy_function(current_data, **strategy_kwargs)
        
        if signal is None:
            continue
        
        # Converter sinal para posição desejada
        desired_position = 1 if signal else (-1 if allow_short else 0)
        
        # Agir apenas se mudar a posição
        if desired_position != position:
            # Fechar posição atual se existir
            if position != 0:
                # Calcular resultado da operação
                if position == 1:
                    price_change = (current_price - entry_price) / entry_price
                else:
                    price_change = (entry_price - current_price) / entry_price
                
                # Considerar custos de transação
                transaction_cost = trade_size * (commission + slippage)
                trade_profit = safe_trade_profit(balance, trade_size, price_change, transaction_cost)
                balance += trade_profit
                
                # Registrar operação
                trades_history.append({
                    "entry_date": entry_date,
                    "exit_date": current_date,
                    "position": "long" if position == 1 else "short",
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "exit_reason": "signal",
                    "trade_size": trade_size,
                    "profit_pct": price_change * 100,
                    "profit_amount": trade_profit,
                    "balance_after": balance
                })
                
                position = 0
                trade_size = 0
            
            # Abrir nova posição se for o caso
            if desired_position != 0:
                position = desired_position
                entry_price = current_price
                entry_date = current_date
                
                # Calcular tamanho da posição com base no risco
                trade_size = calculate_trade_size(balance, risk_per_trade, stop_loss)
                
                # Definir stop loss e take profit
                if position == 1:
                    current_stop_loss = entry_price * (1 - stop_loss)
                    current_take_profit = entry_price * (1 + take_profit)
                else:
                    current_stop_loss = entry_price * (1 + stop_loss)
                    current_take_profit = entry_price * (1 - take_profit)
                
                # Registrar operação de entrada
                print(f"{'🔵 COMPRA' if position == 1 else '🔴 VENDA'} em {current_date}: Preço ${entry_price:.2f}, Tamanho ${trade_size:.2f}, Stop: ${current_stop_loss:.2f}, Take Profit: ${current_take_profit:.2f}")
        
        # Calcular drawdown
        if balance > max_balance:
            max_balance = balance
        
        if balance < min_balance:
            min_balance = balance
        
        current_drawdown = (max_balance - balance) / max_balance
        max_drawdown = max(max_drawdown, current_drawdown)
        
        # Calcular retorno diário
        if i > 1:
            daily_return = (balance - equity_curve[-2]["balance"]) / equity_curve[-2]["balance"]
            daily_returns.append(daily_return)
    
    # Fechar posição final se existir
    if position != 0 and balance > 0:
        final_price = stock_data.iloc[-1]["close_price"]
        
        # Calcular resultado da operação final
        if position == 1:
            price_change = (final_price - entry_price) / entry_price
        else:
            price_change = (entry_price - final_price) / entry_price
        
        # Considerar custos de transação
        transaction_cost = trade_size * (commission + slippage)
        trade_profit = safe_trade_profit(balance, trade_size, price_change, transaction_cost)
        balance += trade_profit
        
        final_date = stock_data.iloc[-1]["date"] if has_date else len(stock_data) - 1
        
        # Registrar operação final
        trades_history.append({
            "entry_date": entry_date,
            "exit_date": final_date,
            "position": "long" if position == 1 else "short",
            "entry_price": entry_price,
            "exit_price": final_price,
            "exit_reason": "end_of_data",
            "trade_size": trade_size,
            "profit_pct": price_change * 100,
            "profit_amount": trade_profit,
            "balance_after": balance
        })
        
        print(f"📉 Fechando posição no fim do período: Preço ${final_price:.2f}, Lucro/Perda: ${trade_profit:.2f}")
    
    # Garantir que o balanço nunca seja negativo
    balance = max(0, balance)
    
    # Calcular métricas de desempenho
    profit_amount = balance - initial_capital
    profit_percentage = (profit_amount / initial_capital) * 100
    total_trades = len(trades_history)
    
    winning_trades = [t for t in trades_history if t["profit_amount"] > 0]
    losing_trades = [t for t in trades_history if t["profit_amount"] <= 0]
    
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    
    avg_win = np.mean([t["profit_amount"] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t["profit_amount"] for t in losing_trades]) if losing_trades else 0
    
    profit_factor = abs(sum(t["profit_amount"] for t in winning_trades) / sum(t["profit_amount"] for t in losing_trades)) if losing_trades and sum(t["profit_amount"] for t in losing_trades) != 0 else float('inf')
    
    # Calcular métricas de risco
    if daily_returns:
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        sortino_ratio = np.mean(daily_returns) / np.std([r for r in daily_returns if r < 0]) * np.sqrt(252) if np.std([r for r in daily_returns if r < 0]) > 0 else 0
    else:
        sharpe_ratio = 0
        sortino_ratio = 0
    
    # Converter para DataFrame para facilitar análises posteriores
    equity_df = pd.DataFrame(equity_curve)
    trades_df = pd.DataFrame(trades_history) if trades_history else pd.DataFrame()
    
    # Resultados
    print("\n📊 RESULTADOS DO BACKTEST:")
    print(f"🔹 Balanço final: ${balance:.2f}")
    print(f"📈 Lucro/prejuízo total: ${profit_amount:.2f} ({profit_percentage:.2f}%)")
    print(f"📊 Total de operações: {total_trades}")
    print(f"✅ Operações vencedoras: {len(winning_trades)} ({win_rate*100:.2f}%)")
    print(f"❌ Operações perdedoras: {len(losing_trades)} ({(1-win_rate)*100:.2f}%)")
    print(f"💰 Lucro médio por operação vencedora: ${avg_win:.2f}")
    print(f"💸 Perda média por operação perdedora: ${avg_loss:.2f}")
    print(f"📉 Drawdown máximo: {max_drawdown*100:.2f}%")
    print(f"📊 Fator de lucro: {profit_factor:.2f}")
    print(f"📈 Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"📈 Sortino Ratio: {sortino_ratio:.2f}")
    
    # Adicionar informações por tipo de saída
    exit_reasons = {}
    if not trades_df.empty:
        exit_counts = trades_df["exit_reason"].value_counts()
        for reason in exit_counts.index:
            exit_reasons[reason] = exit_counts[reason]
    
    # Compilar resultados
    results = {
        "final_balance": balance,
        "profit_amount": profit_amount,
        "profit_percentage": profit_percentage,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "max_drawdown": max_drawdown,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "exit_reasons": exit_reasons,
        "equity_curve": equity_df,
        "trades_history": trades_df,
        "strategy_name": strategy_function.__name__,
        "strategy_params": strategy_kwargs
    }
    
    return results