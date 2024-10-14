from flask import Flask, jsonify, request
import bs4 as bs
import urllib.request
import csv

app = Flask(__name__)

def scrape_data():
    url = 'https://www.envigo.co.in/'
    source = urllib.request.urlopen(url).read
    soup = bs.BeautifulSoup(source, 'lxml')
    data = {
        'title': soup.title.string if soup.title else 'No Title',
        'headings': [],
        'paragraphs': [],
        'div_content': [],
        'span_tags': [],
        'links': [],
        'table_data': [],
        'sitemap_urls': []
    }

    # Scraping headings (h1, h2, h3, etc.)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if headings:
        for heading in headings:
            data['headings'].append({'tag': heading.name, 'text': heading.text.strip()})

    # Scraping paragraphs
    paragraphs = soup.find_all('p')
    if paragraphs:
        for paragraph in paragraphs:
            data['paragraphs'].append(paragraph.text.strip())

    # Scraping divs (all divs, including nested ones)
    divs = soup.find_all('div')
    if divs:
        for div in divs:
            data['div_content'].append({'class': div.get('class', 'No Class'), 'text': div.text.strip()})

    # Scraping span tags
    spans = soup.find_all('span')
    if spans:
        for span in spans:
            data['span_tags'].append(span.text.strip())

    # Scraping links (a tags)
    links = soup.find_all('a')
    if links:
        for link in links:
            href = link.get('href', 'No Link')
            data['links'].append({'href': href, 'text': link.text.strip()})

    # Scraping table data (if any)
    tables = soup.find_all('table')
    if tables:
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                data['table_data'].append([cell.text.strip() for cell in cells])

    # Sitemap or loc URLs if the site has a sitemap
    soup_xml = bs.BeautifulSoup(source, 'xml')
    urls = soup_xml.find_all('loc')
    if urls:
        for url in urls:
            data['sitemap_urls'].append(url.text)

    return data

# Search function to filter data based on the search term
def search_data(search_term, data):
    search_results = {}

    # Search the title
    if search_term.lower() in data['title'].lower():
        search_results['title'] = data['title']

    # Search in headings
    search_results['headings'] = [heading for heading in data['headings'] if search_term.lower() in heading['text'].lower()]

    # Search in paragraphs
    search_results['paragraphs'] = [para for para in data['paragraphs'] if search_term.lower() in para.lower()]

    # Search in divs
    search_results['div_content'] = [div for div in data['div_content'] if search_term.lower() in div['text'].lower()]

    # Search in spans
    search_results['span_tags'] = [span for span in data['span_tags'] if search_term.lower() in span.lower()]

    # Search in links
    search_results['links'] = [link for link in data['links'] if search_term.lower() in link['text'].lower()]

    # Search in table data
    search_results['table_data'] = [row for row in data['table_data'] if any(search_term.lower() in cell.lower() for cell in row)]

    # Search in sitemap URLs
    search_results['sitemap_urls'] = [url for url in data['sitemap_urls'] if search_term.lower() in url.lower()]

    return search_results

# API endpoint for scraping and searching
@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q', '')

    if not search_term:
        return jsonify({"error": "Please provide a search term using the 'q' query parameter."}), 400

    # Scrape the data
    scraped_data = scrape_data()

    # Search the scraped data
    search_results = search_data(search_term, scraped_data)

    # Return the search results as JSON
    return jsonify(search_results)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
