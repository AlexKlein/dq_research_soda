SELECT COUNT(DISTINCT cr.model) AS number_of_other_models
FROM   automotive.cars AS cr
WHERE  cr.model NOT IN ('Tesla Model 3', 'Toyota Corolla', 'Ford Focus')