import bs4 as bs
import urllib.request
import csv
import os
from flask import Flask, request, send_file, jsonify

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

@app.route('/scrape', methods=['GET'])
def scrape_website():
    url = request.args.get('url')  
    if not url:
        return jsonify({"error": "No URL provided."}), 400

    soup = fetch_page(url)
    
    if soup:
        csv_file_path = 'scrape_data.csv'  
        
        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
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
                js_test = new_func(soup)
                if js_test:
                    writer.writerow(['JavaScript Test Paragraph', js_test.text.strip()])
                else:
                    writer.writerow(['JavaScript Test Paragraph', 'No JS Test Found'])

            print("Data extraction completed successfully.")
            return send_file(csv_file_path, as_attachment=True) 
            
        except PermissionError:
            return jsonify({"error": "Permission denied: Unable to write to 'scrape_data.csv'."}), 500
        except Exception as e:
            return jsonify({"error": f"An error occurred while writing to CSV: {e}"}), 500
    else:
        return jsonify({"error": "Failed to retrieve or parse the page."}), 500

if __name__ == '__main__':
    app.run(debug=True)

