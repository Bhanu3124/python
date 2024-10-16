from flask import Flask, request, send_file, jsonify
import bs4 as bs
import urllib.request
import csv
import re
import os

app = Flask(__name__)

def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        source = urllib.request.urlopen(req).read()
        return bs.BeautifulSoup(source, 'lxml')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def new_func(soup):
    return soup.find('p', class_='jstest')

def sanitize_filename(url):
    return re.sub(r'\W+', '_', url)

def scrape_website(url):
    soup = fetch_page(url)

    if soup:
        try:
            sanitized_filename = sanitize_filename(url)
            csv_filename = f'{sanitized_filename}.csv'

            with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                writer.writerow(['Title', 'First Paragraph'])
                writer.writerow([soup.title.string if soup.title else 'No Title',
                                 soup.p.text.strip() if soup.p else 'No Paragraph Found'])

                writer.writerow(['All Paragraphs'])
                paragraphs = soup.find_all('p')
                for paragraph in paragraphs:
                    content = paragraph.text.strip()
                    if content:  
                        writer.writerow([content])

                writer.writerow(['All Links'])
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()
                    link_text = link.text.strip() or 'No Text'
                    if href: 
                        writer.writerow([link_text, href])

                writer.writerow(['All Image Sources'])
                for img in soup.find_all('img', src=True):
                    src = img['src'].strip()
                    if src:  
                        writer.writerow([src])

                writer.writerow(['Additional Divs'])
                for div in soup.find_all('div'):
                    div_content = div.get_text(strip=True)
                    if div_content: 
                        writer.writerow([div_content])

                writer.writerow(['Table Data'])
                tables = soup.find_all('table')
                for table in tables:
                    headers = table.find_all('th')
                    if headers:
                        writer.writerow([' | '.join(header.text.strip() for header in headers)])
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:  
                            writer.writerow([' | '.join(col.text.strip() for col in cols)])

                writer.writerow(['XML Links'])

                js_test = new_func(soup)
                if js_test:
                    writer.writerow(['JavaScript Test Paragraph', js_test.text.strip()])
                else:
                    writer.writerow(['JavaScript Test Paragraph', 'No JS Test Found'])

            return csv_filename

        except PermissionError:
            return "Permission denied: Unable to write to the CSV file."
        except Exception as e:
            return f"An error occurred while writing to CSV: {e}"
    else:
        return "Failed to retrieve or parse the page."

@app.route('/scrape', methods=['POST'])
def scrape_and_download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    csv_filename = scrape_website(url)
    
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Failed to generate CSV file."}), 500

    return jsonify({"message": "Scraping completed successfully", "filename": csv_filename})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = f"{filename}.csv"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(port=8000, debug=True)

