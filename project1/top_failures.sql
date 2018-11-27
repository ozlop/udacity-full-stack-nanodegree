SELECT day
    , count(errors) / (count(*) * 1.0) AS failure
FROM (
    SELECT date(time) AS day
        , CASE WHEN status = '404 NOT FOUND' THEN 1 END errors
    FROM log
) log
GROUP BY day
HAVING count(errors) / (count(*) * 1.0) > .01
ORDER BY day;
