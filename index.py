from requests_html import HTMLSession
from bs4 import BeautifulSoup
s = HTMLSession()

def main(entry):
    url = f'https://www.amazon.com/s?k={entry}'
    initial = True

    for count in range(0, 3):
        soup = getData(url)
        #Gets all the div elements containing the products.
        items = soup.find_all('div', {'data-component-type': 's-search-result'})

        item_info_list = []
        for item in items:
            try:
                info = getItemInfo(item)
            except:
                continue
            item_info_list.append(info)

        bestItemOnPage = findBestItemOnPage(item_info_list)
        print("best item on page")
        print(bestItemOnPage)

        if initial: 
            bestItem = bestItemOnPage
            initial = False
            url = getNextPage(soup)
            continue

        bestItem = compare(bestItemOnPage, bestItem)
        url = getNextPage(soup)

    print("best item")
    print(bestItem)
    return bestItem

def getData(url):
    r = s.get(url)
    r.html.render(sleep=1)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    return soup

def getNextPage(soup):
    pages = soup.find('ul', {'class': 'a-pagination'})
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = pages.find('li', {'class': 'a-last'}).find('a')['href']
        return 'https://www.amazon.com/' + url
    else:
        return

#Returns a dictionary containing title, ID, price, average reviews, review count
def getItemInfo(item):
    ID = item.get('data-asin')

    try:
        brand = item.find('span', {'class': 'a-size-base-plus a-color-base'}).text.strip()
    except:
        brand = "none"

    try:
        title = item.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'}).text.strip()
    except:
        title = item.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()

    price = float(item.find('span', {'class': 'a-offscreen'}).text.replace('$','').strip())
    rating = float(item.find('span', {'class': 'a-icon-alt'}).text.replace('out of 5 stars', '').strip())
    numberOfRatings = float(item.find('span', {'class':'a-size-base'}).text.replace(',','').strip())
    return {'ID': ID, 'brand':brand, 'title':title, 'price':price, 'rating':rating, 'numberOfRatings': numberOfRatings}

def findBestItemOnPage(page):
    bestItem = page[0]
    for item in page:
        bestItem = compare(item, bestItem)
    return bestItem
        
def compare(item, bestItem):
    price, rating, numRatings = item['price'], item['rating'], item['numberOfRatings']
    best_price, best_rating, best_numRatings = bestItem['price'], bestItem['rating'], bestItem['numberOfRatings']

    if price < best_price:
        # if the price of the current item is less than the best one by 20%
        if price <= best_price * 0.9:
            return bestItem if best_rating - rating >= 0.3 else item

        # if the price of the current item is less than the best one by 10%
        if price <= best_price * 0.97:
            if best_rating > rating:
                if best_rating - rating >= 0.4:
                    return bestItem
                elif 0.2 <= best_rating - rating < 0.4:
                    return bestItem if numRatings < best_numRatings * 0.80 else item
                else:
                    return item
            else:
                return item
    else:
        return bestItem

print("Please specify a product")
product = input()
main(product)
