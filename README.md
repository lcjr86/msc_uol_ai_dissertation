# MSc in Artificial Intelligence from University of Liverpool

## Dissertation Title

```
REINFORCEMENT LEARNING IN CRYPTOCURRENCY TRADING: VISUAL PATTERNS AND TECHNICAL INDICATORS USED TOGETHER TO IDENTIFY TRADING OPPORTUNITIES
```

## Author

Luiz Carlos de Jesus Junior

## Folder's structure:

The following topics are the available folders in this repository.

### <u>Data</u>

The following topics are the available folders in the data folder.
Please note that these folder didn't appear as the data is not commited into this repository.

#### `/data/00_raw_single/`

Raw data (currency and time-to-chart) from Binance API, grabbed year-by-year (from 2017 until 2022).

#### `/data/05_raw_group/`

Data from `00_raw_single` grouped by currency and time-to-chart.

#### `/data/10_candlesticks_signals_raw/`

Data from `05_raw_group` with candlesticks signals marks.

#### `/data/20_candlesticks_signals_processed/`

Data from `10_candlesticks_signals_raw` with candlesticks signals marks validated by internal process (mode details in `data_analysis/notebooks/check_candlestick_patterns.ipynb`).

#### `/data/30_technical_indicators/`

Data from `20_candlesticks_signals_processed` with technical indicators calculated.

#### `/data/40_crypto_index/`

Data from `30_technical_indicators` with crypto index calculated.

#### `/data/db/`

The main thing is a database (`crypto_msc.db`) with all the data processed and ready to be used by the simulation.

### <u>Data Analysis</u>

#### `/data_analysis/config_files/`

- `config_candlestick_patterns.ini`: Configuration file related to the candlestick patterns verifications.

#### `/data_analysis/notebooks/`

- `check_candlestick_patterns.ipynb`

- `check_data_db.ipynb`

#### `/data_analysis/src/`

The code that supports the process of check the candlestick patterns.

### <u>Data Preparation</u>

#### `/data_prep/config_files/`

- `.env`: File that contains the credentials to access the Binance API.
- `config_candlestick_patterns.ini`: Configuration file related to the candlestick patterns verifications.

#### `/data_prep/notebooks/`

- `01_get_multiple_raw_data_using_python-binance.ipynb`
- `05_create_multiple_raw_group_data.ipynb`
- `11_get_candlestick_patterns_automated.ipynb`
- `22_validate_candlestick_patterns_intensity_index_automated.ipynb`
- `31_add_risk_and_technical_indicators_automated.ipynb`
- `41_create_crypto_index_automated.ipynb`

Note: The details schema of these pipelines are added below in this document.

#### `/data_prep/notebooks/src/`

The code that supports the process of check the candlestick patterns.

### <u>Documentation</u>

#### `/data_prep/notebooks/images/`

The images displayed in this document.

### <u>Logs</u>

Logs files from the trading simulation environment.

### <u>Simulation</u>

#### `/simulations/config_files/`

- `config_msc_<CCY>_<TTC>_<FP>.ini`

Where CCY = cryptocurrency, TTC = time-to-chart and FP = feature-package.

#### `/simulations/notebooks/`

- `run_simulation_mix_timestamp_multiprocessing_multiples_config_db.ipynb`
- `simple-simulation_analyser_config_msc-db.ipynb`

## IT Artefact

### Overall Diagram

![](/docs/img/overall_diagram.png)

### Detailed Diagrams

![](/docs/img/01-05-pipeline.png)

![](/docs/img/11-22-pipeline.png)

![](/docs/img/31-41-pipeline.png)

![](/docs/img/run-pipeline.png)

![](/docs/img/sim-pipeline.png)

## Glossary

| Tool / Library / Related     | Description / Definiton                                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| .env file                    | Enable the usage of variables without mixing with the global environments of the context |
| .ipynb                       | An extension of a Jupyter Notebook                                                                       |
| binance                      | Library that work as a connector to Binance public API                   |
| CCY                          | Acronym for currency                                                                                     |
| conda                        | Multilanguage package, dependency and environment manager                               |
| conda environment            | A (coding) conda-like environment                                                                        |
| CURL                         | Close, Upper Shadow, Real-Body and Lower Shadow are metrics regarding a candlestick                      |
| DB                           | Acronym for Database                                                                                     |
| dotenv                       | Python library to read key-value pairs from a .env file                          |
| DT                           | Acronym for date                                                                                         |
| gym                          | API to interact with Reinforcement Learning enviroments                  |
| gym_anytrading               | Collection of 'gym' environments for trading algorithms                        |
| jupyter notebooks            | Development enviroment that allows notes, code and data                         |
| matplotlib                   | Python library for creating data visualizations                               |
| numpy                        | Python package for scientific computing 
| pandas                       | Python library for data analysis and manipulation                             |
| plotly                       | Open-source Graphing library for Python                                         |
| Python                       | Programming Language                                                                                     |
| sklearn                      | Machine Learning Python library                                                 |
| sqlalchemy                   | Database toolkit for Python                                          |
| SQLite                       | Small, fast, self-contained SQL database engine                           |
| stable-baselines3            | Set of reliable reinforcement learning Python implementations   |
| statsmodels                  | Python package with a set of different statistical models                       |
| talib                        | Technical Analysis library  |
| TTC                          | Acronym for time-to-chart                                                                                |
| Visual Studio Code (VS Code) | Code Editor                                                       |

| Term                    | Description / Definiton                                                                                                                                                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A2C                     | A2C stands for "Advantage Actor-Critic." It is a type of reinforcement learning algorithm that combines both policy and value-based methods to make decisions in an environment.                                                                     |
| BNB / Binance Coin      | Binance Coin (BNB) is a cryptocurrency that is used within the Binance cryptocurrency exchange ecosystem. It can be used to pay for trading fees on the exchange, as well as for other services provided by Binance.                                 |
| BNBUSDT                 | BNBUSDT is a trading pair on cryptocurrency exchanges, representing the price of Binance Coin (BNB) in USDT (Tether).                                                                                                                                |
| BTC / Bitcoin           | Bitcoin (BTC) is a cryptocurrency that operates on a decentralized peer-to-peer network. It is used for transactions and storage of value, and is secured through cryptography.                                                                      |
| BTCUSDT                 | BTCUSDT is a trading pair on cryptocurrency exchanges, representing the price of Bitcoin (BTC) in USDT (Tether).                                                                                                                                     |
| candlestick charts      | Candlestick charts are a type of financial chart used to represent the price movement of an asset over time. Each candlestick represents a specific time period, and shows the opening, closing, high, and low prices of the asset for that period.  |
| candlestick patterns    | Candlestick patterns are specific formations that appear on candlestick charts, indicating a potential reversal or continuation of the current price trend.                                                                                          |
| clipped objective       | In machine learning, a clipped objective function is a cost function that sets a limit on the gradient of the function. This is done to prevent the algorithm from making large updates that could result in divergence or instability.              |
| cryptocurrency          | Cryptocurrency is a digital or virtual currency that uses cryptography for security. It operates independently of a central bank or government, and is decentralized.                                                                                |
| cryptocurrency exchange | A cryptocurrency exchange is a digital marketplace where cryptocurrencies can be bought, sold, or traded for other cryptocurrencies or fiat currencies.                                                                                              |
| DQN                     | DQN stands for "Deep Q-Network." It is a type of reinforcement learning algorithm that uses deep neural networks to approximate the action-value function in a given environment.                                                                    |
| ETH / Ethereum          | ETH is a decentralized cryptocurrency that operates on the Ethereum \\blockchain, allowing for fast and secure transactions without the need for intermediaries.                                                                                     |
| ETHUSDT                 | ETHUSDT is a trading pair on cryptocurrency exchanges, representing the price of Ethereum (ETH) in USDT (Tether).                                                                                                                                    |
| feat package            | A feat package is a collection of features or variables used in machine learning models to predict or classify outcomes.                                                                                                                             |
| fiat currency           | Fiat currency is a government-issued currency that is not backed by a physical commodity, such as gold or silver. Its value is determined by supply and demand, and it is used as a medium of exchange.                                              |
| PPO                     | PPO stands for "Proximal Policy Optimization." It is a type of reinforcement learning algorithm that optimizes the policy in a given environment by minimizing the divergence between the new and old policies.                                      |
| RL                      | RL stands for "Reinforcement Learning." It is a type of machine learning that involves training an agent to make decisions in an environment, by rewarding or punishing the agent for certain actions.                                               |
| scenario                | A scenario is a hypothetical situation or set of circumstances used for analysis or planning purposes.                                                                                                                                               |
| stablecoin              | A stablecoin is a type of cryptocurrency that aims to maintain a stable value by being pegged to a fiat currency or commodity, or through algorithmic mechanisms, in order to reduce volatility and make it more suitable for everyday transactions. |
| time-to-chart           | Time-to-chart is a metric used in trading to measure the time it takes for data to be processed and displayed on a chart.                                                                                                                            |
| technical indicators    | Technical indicators are mathematical calculations based on the price and/or volume of an asset, used to analyze and predict price movements.                                                                                                        |
| USDT                    | USDT is a stablecoin that is pegged to the US dollar. It is used on many cryptocurrency exchanges as a trading pair and maintains a stable value to provide the benefits of cryptocurrencies while avoiding volatility.                              |
| visual patterns         | Visual patterns refer to the use of chart patterns and technical indicators to analyze price movements in financial markets and make trading decisions based on visual cues.                                                                         |

## Results

For each cryptocurrency (BTC, BNB and ETH), the following results were obtained with the decomposition of:
- Model: A2C, PPO, DQN & RANDOM
- Time-to-chart: 15m, 1h, 1d
- Feature Package: 1, 2 & 3

### Bitcoin (BTCUSDT)

![](/docs/img/BTC-results.png)

### Binance Coin (BNBUSDT)

![](/docs/img/BNB-results.png)

### Ethereum (ETHUSDT)

![](/docs/img/ETH-results.png)
