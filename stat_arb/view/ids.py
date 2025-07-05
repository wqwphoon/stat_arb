STRATEGY_INPUT = "strategy-input"
REGRESSION_INPUT = "regression-input"


class IDS:
    class STORE_INPUTS:
        DATE_RANGE = "date-range"
        TICKER_A = "ticker-a"
        TICKER_B = "ticker-b"
        DATA_SOURCE = "data-source"
        DATA_SOURCE_DESC = "data-source-desc"
        TEST_TRAIN_SPLIT = "test-train-split"

    class INPUTS:
        DATA_INPUT = "load-data"

    class REGRESSION:
        TYPE = "regression-type"
        TYPE_DESC = "regression-type-desc"
        INPUTS_DIV = "regression-inputs-div"
        INPUTS_STORE = "regression-inputs-store"

        class ID_NAIVE_REGRESSION:
            pass

        class ID_ROLLING_WINDOW_REGRESSION:
            WINDOW_LENGTH = {"id_type": REGRESSION_INPUT, "name": "rolling-window", "property": "length"}

    class STATISTICS:
        ADF_RESULT = "adf-result"
        ECM_RESULT = "ecm-result"

    class GRAPHS:
        PRICE_SERIES = "price-series"
        RESIDUAL = "plot_residual"

    class STRATEGY:
        TYPE = "strategy-type"
        INPUTS_DIV = "strategy-inputs-div"
        INPUTS_STORE = "strategy-inputs-store"
        OUTPUT_DIV = "strategy-output-div"
        OUTPUT_BACKTEST_PLOT = "strategy-backtest-plot"
        OUTPUT_CUM_RETS_PLOT = "strategy-cumulative-returns-plot"

        class ID_TOY_STRATEGY:
            ENTER = {"id_type": STRATEGY_INPUT, "name": "toy-strategy", "property": "enter"}
            EXIT = {"id_type": STRATEGY_INPUT, "name": "toy-strategy", "property": "exit"}

        class ID_ROLLING_WINDOW:
            ENTER = {"id_type": STRATEGY_INPUT, "name": "rolling-window", "property": "enter"}
            EXIT = {"id_type": STRATEGY_INPUT, "name": "rolling-window-exit", "property": "exit"}
            LENGTH = {"id_type": STRATEGY_INPUT, "name": "rolling-window", "property": "length"}
