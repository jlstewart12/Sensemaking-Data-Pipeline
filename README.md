# Sensemaking Data Pipeline
Performing data analysis on unstructured MIT course catalog data and using the D3 library to create a visualization of word frequency data

## Code Development

### Libraries

```python
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
```

### Pull course catalog pages

```python
# pull course catalog pages
def catalog():

    #define pull(url) helper function
    def pull(url):
      
        return data
         
    #define store(data,file) helper function
    def store(data,file):
 
        print('wrote file: ' + file)
```
### Tasks

<details><summary>Call helper functions</summary>
<p>

```python
for url in urls:
        index = url.rfind('/') + 1
        #call pull function
        data = pull(url)

        file = url[index:]
        #call store function
        store(data, file)

        print('pulled: ' + file)
        print('--- waiting ---')
        time.sleep(15)
```
</p>
</details>

<details><summary>Combine files</summary>
<p>

```python
# concatenate all files into combo file
    with open('combo.txt', 'w') as outfile:
        for file in glob.glob("*.html"):
            with open(file) as infile:
                outfile.write(infile.read())
```
</p>
</details>

<details><summary>Import BeautifulSoup4 and store the JSON file.</summary>
<p>

```python
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
```
</p>
</details>

<details><summary>Remove all punctuation, numbers, and one-character words from the titles.json file.</summary>
<p>

```python
# remove punctuation/numbers/one character words
def clean():
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print('wrote file: ' + file)

    with open(titles.json) as file:
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
```
</p>
</details>

<details><summary>Save the resulting JSON file.</summary>
<p>

```python
def count_words():
     from collections import Counter
     def store_json(data,file):
           ..
     with open(titles_clean.json) as file:
            titles = json.load(file)
            words = []

            # extract words and flatten
            for title in titles:
                words.extend(title.split())

            # count word frequency
            counts = Counter(words)
            store_json(counts, 'words.json')
```
</p>
</details>

### Airflow Pipeline
```python
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
```

## Code Execution

 1. This terminal command copies the courseCatalog.py file inside the ```airflow-docker/dags``` folder so that Airflow can load the Python tasks as a DAG.
    ```
    cp courseCatalog.py airflow-docker/dags
    ```
 2. In a Terminal window, inside the ```airflow-docker``` folder, run the ```docker-compose up``` command to create and run the containers. All of the containers will be up and running in Docker Desktop.
3. Navigate to http://localhost:8080/ to see the Airflow session. After signing in, switching to Graph View and running each task will show the following result:
    ![](https://github.com/jlstewart12/Sensemaking-Data-Pipeline/blob/main/images/DAG_Graph.png)
4. The JavaScript visualization code can be previewed by placing the direct path to the ```mitcourses_graph.html``` file in the web browser.
    ![](https://github.com/jlstewart12/Sensemaking-Data-Pipeline/blob/main/images/word_count_viz.png)