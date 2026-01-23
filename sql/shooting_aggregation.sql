CREATE OR REPLACE TABLE `police_shootings_cleaned.shootings_aggregated` AS
SELECT
  city_state,
  
  -- Počty
  COUNT(*) AS shooting_count,
  
  -- Průměry
  AVG(age) AS avg_victim_age,
  
  -- Procenta (male)
  COUNTIF(gender = 'M') / COUNT(*) AS pct_male,
  
  -- Procenta (minority = Black nebo Hispanic)
  COUNTIF(race IN ('B', 'H')) / COUNT(*) AS pct_minority,
  
  -- Procenta (unarmed)
  COUNTIF(armed = 'unarmed') / COUNT(*) AS pct_unarmed,
  
  -- Procenta (mental illness)
  COUNTIF(signs_of_mental_illness = TRUE) / COUNT(*) AS pct_mental_illness,
  
  -- Procenta (body camera)
  COUNTIF(body_camera = TRUE) / COUNT(*) AS pct_body_camera
  
FROM
  `police_shootings_cleaned.shootings_cleaned`
GROUP BY
  city_state;