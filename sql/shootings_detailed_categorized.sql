CREATE OR REPLACE TABLE `police_shootings_master.shootings_detailed_categorized` AS
SELECT
  s.*,
  
  -- Přidáme kategorie z master datasetu
  m.budget_category,
  m.population_size,
  m.shooting_rate_category,
  
  -- Armed kategorie
  CASE
    WHEN s.armed IS NULL OR s.armed = 'unarmed' THEN 'Unarmed'
    WHEN s.armed IN ('gun', 'guns and explosives') THEN 'Gun'
    WHEN s.armed IN ('knife', 'sword', 'machete', 'ax', 'hatchet') THEN 'Blade'
    ELSE 'Other'
  END AS armed_category,
  
  -- Age groups
  CASE
    WHEN s.age < 18 THEN 'Minor'
    WHEN s.age < 30 THEN 'Young'
    WHEN s.age < 50 THEN 'Middle'
    WHEN s.age >= 50 THEN 'Senior'
    ELSE NULL
  END AS age_group,
  
  -- Race kategorie
  CASE
    WHEN s.race = 'W' THEN 'White'
    WHEN s.race = 'B' THEN 'Black'
    WHEN s.race = 'H' THEN 'Hispanic'
    WHEN s.race = 'A' THEN 'Asian'
    ELSE 'Other'
  END AS race_category,
  
  -- Threat kategorie
  CASE
    WHEN s.threat_level = 'attack' THEN 'Attack'
    WHEN s.threat_level IS NULL THEN 'Unknown'
    ELSE 'Other_Threat'
  END AS threat_category,
  
  -- Binary flags
  IF(s.signs_of_mental_illness, 'Yes', 'No') AS mental_illness_flag,
  IF(s.body_camera, 'Yes', 'No') AS body_camera_flag
  
FROM
  `police_shootings_cleaned.shootings_cleaned` s
INNER JOIN
  `police_shootings_master.master_dataset_categorized` m
ON
  s.city_state = m.city_state;