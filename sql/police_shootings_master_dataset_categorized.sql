CREATE OR REPLACE TABLE `police_shootings_master.master_dataset_categorized` AS
WITH terciles AS (
  SELECT
    *,
    NTILE(3) OVER (ORDER BY police_budget_per_capita) AS budget_tercile,
    NTILE(3) OVER (ORDER BY shooting_count) AS shooting_count_tercile,
    NTILE(3) OVER (ORDER BY shooting_rate_per_100k) AS shooting_rate_tercile
  FROM
    `police_shootings_master.master_dataset`
)
SELECT
  *,
  
  -- Budget kategorie
  CASE budget_tercile
    WHEN 1 THEN 'Low_Budget'
    WHEN 2 THEN 'Medium_Budget'
    WHEN 3 THEN 'High_Budget'
  END AS budget_category,
  
  -- Shooting frequency kategorie
  CASE shooting_count_tercile
    WHEN 1 THEN 'Few_Shootings'
    WHEN 2 THEN 'Medium_Shootings'
    WHEN 3 THEN 'Many_Shootings'
  END AS shooting_frequency,
  
  -- Population size kategorie
  CASE
    WHEN avg_city_population < 200000 THEN 'Small'
    WHEN avg_city_population < 500000 THEN 'Medium'
    ELSE 'Large'
  END AS population_size,
  
  -- Shooting rate kategorie
  CASE shooting_rate_tercile
    WHEN 1 THEN 'Low_Rate'
    WHEN 2 THEN 'Medium_Rate'
    WHEN 3 THEN 'High_Rate'
  END AS shooting_rate_category,
  
  -- Unarmed kategorie
  CASE
    WHEN pct_unarmed <= 0.01 THEN 'None_Unarmed'
    WHEN pct_unarmed <= 0.15 THEN 'Some_Unarmed'
    ELSE 'Many_Unarmed'
  END AS unarmed_category,
  
  -- Minority kategorie
  CASE
    WHEN pct_minority <= 0.33 THEN 'Low_Minority'
    WHEN pct_minority <= 0.66 THEN 'Medium_Minority'
    ELSE 'High_Minority'
  END AS minority_category,
  
  -- Mental illness kategorie
  CASE
    WHEN pct_mental_illness <= 0.1 THEN 'Rare_Mental'
    WHEN pct_mental_illness <= 0.3 THEN 'Some_Mental'
    ELSE 'Frequent_Mental'
  END AS mental_illness_category
  
FROM terciles;