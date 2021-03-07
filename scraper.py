import requests

import os
import string

from bs4 import BeautifulSoup


extra_punctuation = string.punctuation + "'" + "-"
translator = str.maketrans('', '', extra_punctuation)


def scrap(num_of_page, article_type):
    """Return dict of link as value and title as key"""

    main_dir = os.getcwd()
    url = "https://www.nature.com/nature/articles?searchType=journalSearch&sort=PubDate&page=1"
    for page in range(1, num_of_page+1):
        page_url = url[:-1] + str(page)
        r = requests.get(page_url)
        soup = BeautifulSoup(r.content, 'lxml')

        article_list = soup.find_all('article')

        current_dir_name = f'Page_{page}'
        os.mkdir(current_dir_name)
        os.chdir(f"./{current_dir_name}")

        articles_info = {}

        for element in article_list:
            e = element.findChild('span', {'class': 'c-meta__type'})
            if e.text == article_type:
                a = element.findChild('a', {'data-track-action': 'view article'})

                link = a.get('href')
                link = url[:22] + link

                dirty_title = a.text
                title = dirty_title.translate(translator).replace(' ', '_')

                articles_info[title] = link

        getArticleData(articles_info, article_type)

        os.chdir(f"{main_dir}")


def getArticleData(articles_info, article_type):
    """Scraping data from <p> in article"""

    if "News" in article_type:
        article_class = 'article__body'
    else:
        article_class = "article-item__body"

    num_of_links = len(articles_info.values())
    num_of_files = 0

    for k, v in articles_info.items():
        response = requests.get(v, 'lxml')
        html = response.content
        articles_soup = BeautifulSoup(html, 'lxml')

        article_body = None

        if articles_soup.find_all('div', {'class': 'Theme-Layer-BodyText--inner'}):
            article_body = articles_soup.find_all('div', {'class': 'Theme-Layer-BodyText--inner'})

        else:
            try:
                article_body = articles_soup.find_all('div', {'class': article_class})
            except (AttributeError, KeyError):
                pass

        for element in article_body:
            with open(f'{k}.txt', 'w', encoding='utf-8') as f:
                f.write(element.text.strip())
            if os.access(f'{k}.txt', os.F_OK):
                num_of_files += 1

    if num_of_links == num_of_files:
        print("Saved all articles.")
    else:
        print(":(")


def main():
    num_of_page = int(input("> "))
    article_type = input("> ")
    scrap(num_of_page, article_type)


if __name__ == "__main__":
    main()
