import bs4 as bs
import urllib.request
import csv

# Function to fetch and parse the page
def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        source = urllib.request.urlopen(req).read()
        return bs.BeautifulSoup(source, 'lxml')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to extract JavaScript test paragraph
def new_func(soup):
    return soup.find('p', class_='jstest')

# Main function to perform scraping
def scrape_website(url):
    soup = fetch_page(url)

    # Only proceed if soup is successfully created
    if soup:
        try:
            with open('scraped_data.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Title and First Paragraph in the same row
                writer.writerow(['Title', 'First Paragraph'])
                writer.writerow([soup.title.string if soup.title else 'No Title',
                                 soup.p.text.strip() if soup.p else 'No Paragraph Found'])

                # All Paragraphs
                writer.writerow(['All Paragraphs'])
                paragraphs = soup.find_all('p')
                for paragraph in paragraphs:
                    content = paragraph.text.strip()
                    if content:  # Only write non-empty paragraphs
                        writer.writerow([content])

                # All Links
                writer.writerow(['All Links'])
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()
                    link_text = link.text.strip() or 'No Text'  # Capture link text
                    if href:  # Validate non-empty links
                        writer.writerow([link_text, href])  # Write link text and URL

                # All Image Sources
                writer.writerow(['All Image Sources'])
                for img in soup.find_all('img', src=True):
                    src = img['src'].strip()
                    if src:  # Validate non-empty image sources
                        writer.writerow([src])

                # Additional Divs and Classes
                writer.writerow(['All Divs and Classes'])
                for element in soup.find_all(True):  # Find all elements
                    class_name = element.get('class')  # Get the class of the element
                    if class_name:  # If the element has a class
                        content = element.get_text(strip=True)
                        if content:  # Only write non-empty divs
                            writer.writerow([', '.join(class_name), content])

                # Tables
                writer.writerow(['Table Data'])
                tables = soup.find_all('table')
                for table in tables:
                    headers = table.find_all('th')
                    if headers:
                        writer.writerow([' | '.join(header.text.strip() for header in headers)])
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:  # Only write rows with data
                            writer.writerow([' | '.join(col.text.strip() for col in cols)])

                # JavaScript Test Paragraph
                js_test = new_func(soup)
                if js_test:
                    writer.writerow(['JavaScript Test Paragraph', js_test.text.strip()])
                else:
                    writer.writerow(['JavaScript Test Paragraph', 'No JS Test Found'])

            print("Data extraction completed successfully.")
        except PermissionError:
            print("Permission denied: Unable to write to 'scraped_data.csv'. Please ensure the file is not open in another program and you have write permissions.")
        except Exception as e:
            print(f"An error occurred while writing to CSV: {e}")
    else:
        print("Failed to retrieve or parse the page.")

# Run the scrape function
url = 'https://www.w3schools.com/'
scrape_website(url)
