import requests
from bs4 import BeautifulSoup


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
            max_page_number = soup.find('div', class_='pager').find_all('span', class_='item')[-1].getText()
            if int(max_page_number) > 10:
                max_page_number = 10

        self.fill_data(soup)

        # Extract other pages.
        if 'max_page_number' in locals():
            for p in range(2, max_page_number):
                url = self.__url + '/?page=' + str(p)
                pages = requests.get(url)
                soups = BeautifulSoup(pages.content, 'html.parser')
                self.fill_data(soups)

        print(self.__results)

    def fill_data(self, soup: BeautifulSoup):
        ads = soup.find_all('table', class_='fixed')

        for ad in ads:
            try:
                title = ad.find('h3')
                price = ad.find('p', class_='price')
                link = ad.find('a', class_='detailsLink')
                if title.text and price.text and link.get('href'):
                    product_list = {
                        'product': title.text.strip(),
                        'price': price.text.strip(),
                        'link': link.get('href').strip()
                    }

                    self.__results.append(product_list)
            except Exception as e:
                continue


Parser().parse()
