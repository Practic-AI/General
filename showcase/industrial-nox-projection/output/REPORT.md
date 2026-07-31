# Industrial NOx projection — public demo report

- **Data:** synthetic multi-unit series (`data/synthetic_units.csv`)
- **Features:** humidity_abs, temp_ambient
- **Target:** NOx (mg/Nm³) per unit
- **Split:** train 80% / test 20%

## Disclaimer

This package uses **synthetic data** for portfolio and training purposes. It is not linked to any real plant. Projections are estimates, not CEMS replacements.

## Test metrics

```
  unit  n_train  n_test  r2_rf_test  r2_linear_test  rmse_rf_test  mae_rf_test  imp_humidity  imp_temp
Unit_1     9230    2308    0.840350        0.835100     35.635296    28.539724      0.937765  0.062235
Unit_2     9235    2309    0.849841        0.844373     41.183768    32.705708      0.969295  0.030705
Unit_3     9202    2301    0.719116        0.714186     42.801138    34.114689      0.878071  0.121929
Unit_4     9216    2305    0.860628        0.869174     30.449200    24.252329      0.099058  0.900942
Unit_5     9211    2303    0.837595        0.830436     38.965734    31.218015      0.950871  0.049129
Unit_6     9200    2300    0.844247        0.838809     34.461628    27.487523      0.894317  0.105683
```

## Predict

```bash
py -3 predict.py --unit 1 --humidity 10.5 --temp 18
py -3 predict.py --unit all --humidity 10 --temp 18
py -3 predict.py --series examples/series_input.csv --unit all
```
