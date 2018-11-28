import datetime, psycopg2
from pprint import pprint


def run_query(query):
    db = psycopg2.connect("dbname=news")
    c = db.cursor()
    articles = c.execute(open(query, 'r').read())
    result = c.fetchall()

    db.close()

    return result


def generate_report(report, data):
    for d in data:
        if report == 'top_failures':
            field1 = str(d[0].strftime("%B %d, %Y"))
            field2 = str(d[1] * 100)
            print('{0!s} - {1:.4}% errors'.format(field1, field2))
            return
        else:
            field1 = str(d[0])
            field2 = d[1]

        if report == 'top_articles':
            field1 = field1.title()
            print('"{}" - {} views'.format(field1, field2))
        else:
            print('{} - {} views'.format(field1, field2))



if __name__ == '__main__':
    reports = ['top_articles', 'top_authors', 'top_failures']

    for report in reports:
        if report == 'top_articles':
            query = 'top_articles.sql'
            print('Top Read Articles:\n')
        if report == 'top_authors':
            query = 'top_authors.sql'
            print('Top Read Authors:\n')
        if report == 'top_failures':
            query = 'top_failures.sql'
            print('Days with Failures Above 1%:\n')

        generate_report(report, run_query(query))
        print('\n')
