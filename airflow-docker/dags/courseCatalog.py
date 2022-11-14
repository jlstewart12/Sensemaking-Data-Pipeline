# The DAG object; needed to instantiate a DAG
from urllib import response
from airflow import DAG
from datetime import timedelta

# Operators; needed to operate
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

# Task Functions; used to facilitate tasks
import urllib.request
import time
import glob, os
import json

# pull course catalog pages
def catalog():

    #define pull(url) helper function
    def pull(url):
        response = urllib.request.urlopen(url).read()
        data = response.decode('utf-8')
        return data
         
    #define store(data,file) helper function
    def store(data,file):
        f = open(file, 'w+')
        f.write(data)
        f.close()
        print('wrote file: ' + file)

    urls = ['http://student.mit.edu/catalog/m1a.html',
        'http://student.mit.edu/catalog/m1b.html',
        'http://student.mit.edu/catalog/m22c.html'
    ]

    for url in urls:
        index = url.rfind('/') + 1 
        data = pull(url)
        file = url[index:]
        store(data, file)
        print('pulled: ' + file)
        print('--- waiting ---')
        time.sleep(15)

# combine course catalog pages
def combine():
    # local directory
    # os.chdir("scratch/")

    # concatenate all files into combo file
    with open('combo.txt', 'w') as outfile:
        for file in glob.glob("*.html"):
            with open(file) as infile:
                outfile.write(infile.read())

# build array of course titles
def titles():
    from bs4 import BeautifulSoup
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print('wrote file: ' + file)

    file = open("combo.txt", "r")
    html = file.read()
    html = html.replace('\n', ' ').replace('\r', '')
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all('h3')
    titles = []

    # tag inner text
    for item in results:
        titles.append(item.text)
    store_json(titles, 'titles.json')

# remove punctuation/numbers/one character words
def clean():
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print('wrote file: ' + file)

    with open('titles.json') as file:
        titles = json.load(file)

        # remove punctuation/numbers
        for index, title in enumerate(titles):
            punctuation= '''!()-[]{};:'"\,<>./?@#$%^&*_~1234567890'''
            translationTable= str.maketrans("","",punctuation)
            clean = title.translate(translationTable)
            titles[index] = clean

        # remove one character words
        for index, title in enumerate(titles):
            clean = ' '.join( [word for word in title.split() if len(word)>1] )
            titles[index] = clean

        store_json(titles, 'titles_clean.json')

# count word frquency
def count_words():
     from collections import Counter

     def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print('wrote file: ' + file)
           
     with open('titles_clean.json', 'r') as file:
            titles = json.load(file)
            words = []

            # extract words and flatten
            for title in titles:
                words.extend(title.split())

            # count word frequency
            counts = Counter(words)
            store_json(counts, 'words.json')

# args passed to each operator
with DAG(
   "assignment",
   start_date=days_ago(1),
   schedule_interval="@daily",catchup=False,
) as dag:

# INSTALL BS4 BY HAND THEN CALL FUNCTION

   # ts are tasks
    t0 = BashOperator(
        task_id='task_zero',
        bash_command='pip install beautifulsoup4',
        retries=2
    )

    t1 = PythonOperator(
        task_id='task_one',
        depends_on_past=False,
        python_callable=catalog
    )
    t2 = PythonOperator(
        task_id='task_two',
        depends_on_past=False,
        python_callable=combine
    )
   
    t3 = PythonOperator(
        task_id='task_three',
        depends_on_past=False,
        python_callable=titles
    )

    t4 = PythonOperator(
       task_id='task_four',
       depends_on_past=False,
       python_callable=clean
   )

    t5 = PythonOperator(
        task_id='task_five',
        depends_on_past=False,
        python_callable=count_words
    )
    t0>>t1>>t2>>t3>>t4>>t5