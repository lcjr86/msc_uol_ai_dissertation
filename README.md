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

TBD

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

TBD

## Results

TBD

### Bitcoin (BTCUSDT)

![](/docs/img/BTC-results.png)

### Binance Coin (BNBUSDT)

![](/docs/img/BNB-results.png)

### Ethereum (ETHUSDT)

![](/docs/img/ETH-results.png)