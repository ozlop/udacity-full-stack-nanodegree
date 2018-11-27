WITH visited
AS (
    SELECT replace(path, '/article/', '') AS path
        , count(path) AS total
    FROM log
    WHERE path LIKE '/article/%'
        AND status = '200 OK'
    GROUP BY path
    )
SELECT articles.title, total
FROM visited
JOIN articles
    ON visited.path = articles.slug
ORDER BY total DESC
LIMIT 3;
