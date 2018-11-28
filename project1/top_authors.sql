WITH visited
AS (
    SELECT path
        , count(path) AS total
    FROM log
    WHERE path LIKE '/article/%'
        AND status = '200 OK'
    GROUP BY path
    )
SELECT authors.name, sum(visited.total) AS TOTAL
FROM visited
JOIN articles
    ON visited.path = CONCAT('/article/', articles.slug)
JOIN authors
    ON articles.author = authors.id
GROUP BY authors.name
ORDER BY total DESC;
