import bs4 as bs
import urllib.request
import csv
from flask import Flask, jsonify

app = Flask(__name__)

def fetch_data():
    source = urllib.request.urlopen('https://www.envigo.co.in/').read()
    soup = bs.BeautifulSoup(source, 'lxml')
    
    
    data = {
        'title': soup.title.string if soup.title else 'No Title',
        'first_paragraph': soup.p.text if soup.p else 'No Paragraph Found',
        'paragraphs': [paragraph.text.strip() for paragraph in soup.find_all('p')],
        'links': [url.get('href') for url in soup.find_all('a') if url.get('href')],
        'body_paragraphs': [paragraph.text.strip() for paragraph in soup.body.find_all('p')] if soup.body else [],
        'div_body': [div.text.strip() for div in soup.find_all('div', class_='body')],
        'table_data': []
    }

    
    table = soup.table
    if table:
        for tr in table.find_all('tr'):
            td = tr.find_all('td')
            row = [i.text.strip() for i in td]
            data['table_data'].append(row)

    
    soup_xml = bs.BeautifulSoup(source, 'xml')
    data['xml_loc'] = [url.text for url in soup_xml.find_all('loc')]

    
    js_test = soup.find('p', class_='jstest')
    data['js_test'] = js_test.text.strip() if js_test else None

    return data

@app.route('/scrape', methods=['GET'])
def scrape():
    
    scraped_data = fetch_data()
    return jsonify(scraped_data)

def new_func(app):
    app.run(debug=True)

if __name__ == '__main__':
    new_func(app)
