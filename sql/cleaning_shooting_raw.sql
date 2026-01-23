CREATE OR REPLACE TABLE `police_shootings_cleaned.shootings_cleaned` AS
SELECT
  id,
  name,
  date,
  manner_of_death,
  armed,
  age,
  gender,
  race,
  TRIM(INITCAP(city)) AS city_clean,
  TRIM(UPPER(state)) AS state_clean,
  CONCAT(TRIM(INITCAP(city)), ', ', TRIM(UPPER(state))) AS city_state,
  signs_of_mental_illness,
  threat_level,
  flee,
  body_camera
FROM
  `police-shooting-project.police_shooting_raw.shooting_raw`
WHERE
  city IS NOT NULL 
  AND state IS NOT NULL;