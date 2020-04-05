import requests
from bs4 import BeautifulSoup
import pandas as pd
import webbrowser
import os


class Parser(object):
    __url = ''
    __results = []

    def __init__(self):
        search_query = input("Please, enter your search query \n")
        self.__url = 'https://www.olx.ua/list/q-' + search_query.replace(' ', '-')
        self.__page = requests.get(self.__url)

    def parse(self):
        soup = BeautifulSoup(self.__page.content, 'html.parser')
        pager_exists = soup.find('div', class_='pager')
        if pager_exists:
            max_page_number = soup.find('div', class_='pager').find_all('span', class_='item')[-1].getText().strip()
            if int(max_page_number) > 10:
                max_page_number = 10

        self.fill_data(soup)

        # Extract other pages.
        if 'max_page_number' in locals():
            for p in range(2, int(max_page_number)):
                url = self.__url + '/?page=' + str(p)
                pages = requests.get(url)
                soups = BeautifulSoup(pages.content, 'html.parser')
                self.fill_data(soups)

        # Distinct list values, exclude duplicate links.
        self.__results = list({v['link']: v for v in self.__results}.values())
        # Sort by price.
        self.__results = sorted(self.__results, key=lambda i: i['price'])
        # Store result to HTML file and open it in prowser.
        self.html_dump()

    def fill_data(self, soup: BeautifulSoup):
        ads = soup.find_all('table', class_='fixed')

        for ad in ads:
            try:
                title = ad.find('h3')
                price = ad.find('p', class_='price')
                link = ad.find('a', class_='detailsLink')
                if title.text and price.text and link.get('href'):
                    link_href = link.get('href').strip()
                    product_list = {
                        'product': title.text.strip(),
                        'price': int(price.text.strip().replace(' ', '').replace('грн.', '')),
                        'link': '<a target="_blank" href={0}>{0}</a>'.format(link_href),
                    }

                    self.__results.append(product_list)
            except Exception as e:
                continue

    def make_clickable(val):
        # target _blank to open new window
        return '<a target="_blank" href="{}">{}</a>'.format(val, val)

    def html_dump(self):
        html_string = '''
        <html>
          <head><title>HTML Pandas Dataframe with CSS</title></head>
          <link rel="stylesheet" type="text/css" href="assets/css/df_style.css"/>
          <body>
            {table}
          </body>
        </html>.
        '''

        df = pd.DataFrame(self.__results)
        df.set_index('price')

        # Write html to file
        text_file = open("results.html", "w+")
        text_file.write(html_string.format(table=df.to_html(escape=False, classes='result-table')))
        text_file.close()

        webbrowser.open('file://' + os.path.realpath('results.html'))


Parser().parse()
