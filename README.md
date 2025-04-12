# Desenvolvido por Zenba
É uma modificação usando IA para fazer trades na Binance Futures.
{AI's Utilizadas: Deepseek & Gemmini 3_27b}

# 1. Instale as seguintes bibliotecas:

    Abra o terminal (ctrl+J) e digite:

    pip install pandas python-binance python-dotenv

# 2. Configure as chaves da API Binance

    Crie um arquivo `.env` na raiz do projeto (mesmo diretório que este README.md).

    Adicione suas chaves de API e Secret Key da Binance no arquivo `.env`, da seguinte forma:
    load_dotenv()
    api_key = "Chave aqui"
    secret_key = "Chave aqui"

# 3. Ative o interpretador no VsCode. Selecione Python -> Conda/Base

    Ctrl + shift + P

    Digitar Interpretador -> Selecionar Interpretador

    Escolher Python -> "Base"

    🟡 IMPORTANTE: Depois de selecionar o interpretador, clique no ícone da LIXEIRA e abra o terminal novamente.

#  Configure o bot e suas variáveis

    Agora a configuração é feita no arquivo .\src\main.py

#  Código para rodar o bot

    Digite no terminal:

    "python .\src\main.py" - para rodar o bot através do terminal
    OU: "python .\src\backtests.py" - para rodar o backtest e testar sua estratégia e ver seus resultados
    antes de utilizar o bot.


# Termos de Uso

    Ao usar o código você aceita os termos disponíveis no arquivo LICENSE.

    Além da licença de distribuição, o robô/código é disponibilizado para uso sob sua total responsabilidade, 
    sem que os desenvolvedores assumam qualquer responsabilidade por perdas financeiras ou outros danos decorrentes de seu uso.
    Negocie com responsabilidade.
