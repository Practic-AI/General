-- Cirrus US-registered fleet — interview-facing SQL
-- Engine: DuckDB. Tables are registered by analyze.py:
--   fleet, status, registrant, engines, regions
--
-- This is a *registry snapshot*, not factory deliveries.
-- year_mfr = manufacture year of airframes still on the US register.

-- 1) Headline counts
SELECT
    count(*) AS registered_airframes,
    count(*) FILTER (WHERE is_production_model = 1) AS production_models,
    count(*) FILTER (WHERE status_code = 'V') AS valid_registration,
    count(*) FILTER (WHERE status_code = 'M') AS manufacturer_held,
    count(*) FILTER (WHERE year_mfr IS NULL) AS missing_year_mfr,
    round(100.0 * count(*) FILTER (WHERE year_mfr IS NULL) / count(*), 1) AS pct_missing_year
FROM fleet;

-- 2) Mix by model
SELECT
    model,
    model_family,
    count(*) AS n,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct_of_us_registry
FROM fleet
GROUP BY 1, 2
ORDER BY n DESC;

-- 3) Vintage: airframes still registered, by year of manufacture
--    NOT the same as GAMA/Cirrus annual deliveries (exports + write-offs leave the US file).
SELECT
    CAST(year_mfr AS INTEGER) AS year_mfr,
    count(*) AS n,
    count(*) FILTER (WHERE model = 'SR20') AS sr20,
    count(*) FILTER (WHERE model = 'SR22') AS sr22,
    count(*) FILTER (WHERE model = 'SR22T') AS sr22t,
    count(*) FILTER (WHERE model = 'SF50') AS sf50,
    sum(count(*)) OVER (ORDER BY CAST(year_mfr AS INTEGER)) AS running_total
FROM fleet
WHERE year_mfr IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 4) Registration state (legal domicile, not necessarily where the airplane lives)
SELECT
    coalesce(nullif(state, ''), '(blank)') AS state,
    count(*) AS n,
    count(*) FILTER (WHERE status_code = 'M') AS manufacturer_held,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM fleet
GROUP BY 1
ORDER BY n DESC
LIMIT 20;

-- 5) Who holds the registration
SELECT
    coalesce(r.registrant_label, '(unknown ' || f.type_registrant || ')') AS registrant,
    count(*) AS n,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM fleet f
LEFT JOIN registrant r ON r.type_registrant = f.type_registrant
GROUP BY 1
ORDER BY n DESC;

-- 6) Status with labels
SELECT
    f.status_code,
    coalesce(s.status_label, '(unmapped)') AS status_label,
    count(*) AS n
FROM fleet f
LEFT JOIN status s ON s.status_code = f.status_code
GROUP BY 1, 2
ORDER BY n DESC;

-- 7) Age of airframes with a known year (snapshot year is passed as a DuckDB variable)
SELECT
    round(avg(age_years), 1) AS mean_age_years,
    median(age_years) AS median_age_years,
    min(age_years) AS newest_age,
    max(age_years) AS oldest_age
FROM (
    SELECT CAST($snapshot_year AS INTEGER) - CAST(year_mfr AS INTEGER) AS age_years
    FROM fleet
    WHERE year_mfr IS NOT NULL
);

-- 8) Vision Jet share of each manufacture year (growth of the jet in the surviving US file)
SELECT
    CAST(year_mfr AS INTEGER) AS year_mfr,
    count(*) AS n,
    count(*) FILTER (WHERE model = 'SF50') AS sf50,
    round(100.0 * count(*) FILTER (WHERE model = 'SF50') / count(*), 1) AS sf50_share_pct
FROM fleet
WHERE year_mfr IS NOT NULL AND CAST(year_mfr AS INTEGER) >= 2016
GROUP BY 1
ORDER BY 1;
