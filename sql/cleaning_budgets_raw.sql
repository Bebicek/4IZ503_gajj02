CREATE OR REPLACE TABLE `police_shootings_cleaned.budgets_cleaned` AS
SELECT
  -- Základní info
  year,
  city_name,
  
  -- Rozdělíme city_name na state a city (SAFE = nepadne při chybě)
  TRIM(SPLIT(city_name, ':')[SAFE_OFFSET(0)]) AS state_clean,
  TRIM(INITCAP(SPLIT(city_name, ':')[SAFE_OFFSET(1)])) AS city_clean,
  CONCAT(
    TRIM(INITCAP(SPLIT(city_name, ':')[SAFE_OFFSET(1)])), 
    ', ', 
    TRIM(SPLIT(city_name, ':')[SAFE_OFFSET(0)])
  ) AS city_state,
  
  -- Populace
  city_population,
  
  -- Převod miliony na dolary
  police * 1000000 AS police_dollars,
  police_city * 1000000 AS police_city_dollars,
  police_cnty * 1000000 AS police_cnty_dollars,
  
  -- Originální hodnoty v milionech
  police,
  police_city,
  police_cnty

FROM
  `police-shooting-project.police_shooting_raw.budgets_raw`
WHERE
  city_name IS NOT NULL
  AND police IS NOT NULL
  AND city_name LIKE '%:%';  -- jen řádky s dvojtečkou