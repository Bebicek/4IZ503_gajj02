CREATE OR REPLACE TABLE `police_shootings_master.master_dataset` AS
SELECT
  -- Základní identifikátory
  s.city_state,
  b.state_clean,
  b.city_clean,
  
  -- Shooting statistiky
  s.shooting_count,
  s.avg_victim_age,
  s.pct_male,
  s.pct_minority,
  s.pct_unarmed,
  s.pct_mental_illness,
  s.pct_body_camera,
  
  -- Budget statistiky
  b.avg_city_population,
  b.avg_police_dollars,
  b.avg_police_city_dollars,
  b.avg_police_cnty_dollars,
  b.years_with_data,
  b.latest_year,
  
  -- Derived metriky
  s.shooting_count / b.avg_city_population * 100000 AS shooting_rate_per_100k,
  b.avg_police_dollars / b.avg_city_population AS police_budget_per_capita
  
FROM
  `police_shootings_cleaned.shootings_aggregated` s
INNER JOIN
  `police_shootings_cleaned.budgets_aggregated` b
ON
  s.city_state = b.city_state;