# Cirrus US fleet snapshot

- Source: FAA Releasable Aircraft Database, extracted 2026-08-14T23:05:46Z.
- Not affiliated with Cirrus Aircraft. Public registry data only. Owner names and addresses stripped.

## Headlines

- **9,386** Cirrus airframes currently on the US register.
- **9,381** are production models (SR20 / SR22 / SR22T / SF50).
- **8,958** have a valid registration (`V`); **364** sit on a manufacturer dealer certificate (`M`, almost all Minnesota).
- **7.7%** of rows have no usable manufacture year — a real data-quality issue, not a rounding error.
- Median age of airframes with a year: **9.0 years**.
- Registrations are LLC-heavy (**63.4%**).

## How to read this

The FAA file is **who holds a US N-number today**, not Cirrus factory shipments.
A 2024 SR22 delivered to Europe never appears. A 2006 SR22 still flying in Florida does.
Delaware and Wyoming rank high because of how aircraft are titled, not because everyone flies there.

## Model mix

| Model | n | % |
|---|---:|---:|
| SR22 | 3,996 | 42.6 |
| SR22T | 3,024 | 32.2 |
| SR20 | 1,608 | 17.1 |
| SF50 | 753 | 8.0 |
| SR10 | 3 | 0.0 |
| SRT | 1 | 0.0 |
| EX18 | 1 | 0.0 |

## Talking points (for a screen-share)

1. Registry ≠ deliveries. Compare this file to Cirrus/GAMA shipment numbers and the gap is exports + write-offs + foreign registers.
2. Factory inventory is visible: status `M` clusters in Minnesota.
3. Ownership is mostly LLCs — a liability/tax pattern, not a flying pattern.
4. Always publish the missing-year rate. 8% blank is material if someone uses vintage for residual values.
