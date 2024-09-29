from bs4 import BeautifulSoup
import requests
import time

def moneycontrol():
    html_text=requests.get('https://www.moneycontrol.com/news/news-all/').text
    soup= BeautifulSoup(html_text,'lxml')
    headings=soup.find_all('li',class_='clearfix')

    for index,heading in enumerate(headings):
        subheading=heading.p.text
        link=heading.a['href']
        heading=heading.a['title']
        with open(f'posts/{index}.txt','w') as f:
            f.write(f"News Heading : {heading}\n")
            f.write(f"Description : {subheading}\n")
            f.write(f"Link for further : {link}\n")
            f.write("")
        print(f'File saved:{index}')

def bbcnews():
    response = requests.get('https://www.bbc.com/news')
    soup = BeautifulSoup(response.content, 'html.parser')

    news_cards = soup.find_all('div', {'data-testid': 'edinburgh-card'})

    base_url = 'https://www.bbc.com/news'

    for index,card in enumerate(news_cards):
        headline = card.find('h2', {'data-testid': 'card-headline'})
        headline_text = headline.get_text(strip=True) if headline else "No headline found"

        description = card.find('p', {'data-testid': 'card-description'})
        description_text = description.get_text(strip=True) if description else "No description found"

        link_tag = card.find('a', {'data-testid': 'internal-link'})
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']
            if not link.startswith('http'):
                link = base_url + link
        else:
            link = "No link found"

        with open(f'posts/{index}.txt','w') as f:
            f.write(f"News Heading : {headline}\n")
            f.write(f"Description : {headline_text}\n")
            f.write(f"Link for further : {link}\n")
        print(f'File saved:{index}')






if __name__ =='__main__':
    while True:
        moneycontrol()
        bbcnews()
        time_wait=10
        print(f'waiting for {time_wait} minutes...')
        time.sleep(time_wait * 60)

            
