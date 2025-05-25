class IDS:
    class STORE_INPUTS:
        DATE_RANGE = "date-range"
        TICKER_A = "ticker-a"
        TICKER_B = "ticker-b"
        DATA_SOURCE = "data-source"
        TEST_TRAIN_SPLIT = "test-train-split"

    class INPUTS:
        DATA_INPUT = "load-data"

    class REGRESSION:
        TYPE = "regression-type"

    class STATISTICS:
        ADF_RESULT = "adf-result"
        ECM_RESULT = "ecm-result"

    class GRAPHS:
        PRICE_SERIES = "price-series"
        RESIDUAL = "plot_residual"

    class STRATEGY:
        TYPE = "strategy-type"
        INPUTS_DIV = "strategy-inputs-div"

        class TOY_STRATEGY_ID:
            ENTER = "toy-strategy-enter"
            EXIT = "toy-strategy-exit"
