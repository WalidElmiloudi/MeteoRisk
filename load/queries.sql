-- Retrieving the cities that will have the highest temperature
SELECT city,date,temperature_max FROM weather_risk ORDER BY temperature_max DESC;

-- Retrieving the cities that will have the highest precipitation
SELECT city,date,precipitation_sum FROM weather_risk ORDER BY precipitation_sum DESC;

-- Retrieving the cities that will have the highest average risk score
SELECT city , AVG(risk_score) as average_risk FROM weather_risk GROUP BY city ORDER BY average_risk DESC;

-- Retrieving the periods that will have the highest risk score
SELECT date , MAX(risk_score) FROM weather_risk GROUP BY risk_score, date ORDER BY risk_score DESC ;

-- Retrieving what's the most dangerous period
SELECT city , date , risk_score  FROM weather_risk w WHERE risk_score = (SELECT MAX(risk_score) FROM weather_risk WHERE city = w.city);

-- Monitoring How many city are covered
SELECT  count(DISTINCT city) FROM weather_risk;

-- The maximum forecast temperature
SELECT  city , date , temperature_max FROM weather_risk ORDER BY temperature_max DESC LIMIT 1 ;

-- The maximum precipitation
SELECT  city , date , precipitation_sum FROM weather_risk ORDER BY precipitation_sum DESC LIMIT 1 ;