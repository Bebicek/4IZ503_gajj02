CREATE OR REPLACE TABLE `police_shootings_cleaned.budgets_aggregated` AS
SELECT
  city_state,
  state_clean,
  city_clean,
  
  -- Průměry za všechny roky
  AVG(city_population) AS avg_city_population,
  AVG(police_dollars) AS avg_police_dollars,
  AVG(police_city_dollars) AS avg_police_city_dollars,
  AVG(police_cnty_dollars) AS avg_police_cnty_dollars,
  
  -- Počet let s daty
  COUNT(DISTINCT year) AS years_with_data,
  MAX(year) AS latest_year,
  MIN(year) AS earliest_year
  
FROM
  `police_shootings_cleaned.budgets_cleaned`
GROUP BY
  city_state, state_clean, city_clean;