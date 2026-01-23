CREATE OR REPLACE TABLE `police_shootings_cleaned.politics_cleaned` AS
SELECT
  Area,
  `Republican Vote Share` AS republican_vote_share_pct,
  `Partisan Segregation` AS partisan_segregation
FROM
  `police-shooting-project.police_shooting_raw.politics_raw`
WHERE
  Area IS NOT NULL;