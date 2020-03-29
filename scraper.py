from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import pprint

# client = MongoClient("127.0.0.1")
# db = client.local
# db.test.insert_one({"1": "Witam"})

response = requests.get("https://www.olx.pl/oferta/mieszkanie-typu-studio-CID3-IDEfjj5.html#0e13fb5515")

soup = BeautifulSoup(response.content, "lxml")
a_tag_location = soup.find(name="a", class_="show-map-link")
location = a_tag_location.string
print(location)
price = int(soup.find(name="strong", class_="xxxx-large not-arranged").string.replace("zł", "").replace(" ", ""))
flat_info = soup.find(name="table", class_="details fixed marginbott20 margintop5 full").find_all("strong")
building_type = flat_info[3].text.strip()
area = flat_info[4].text.strip()
additional_price = int(flat_info[6].text.strip().replace("zł", ""))
description = soup.find(name="div", class_="clr lheight20 large").text.strip()
photos_divs = soup.find_all(name="div", class_="tcenter img-item")
photos_links = []
for photos_div in photos_divs:
    try:
        photos_links.append(photos_div.find("img")["src"])
    except TypeError:
        continue


class Offer:
    def __init__(self, price, description, building_type, additional_price, location, area, photos):
        self.price = price
        self.description = description
        self.building_type = building_type
        self.additional_price = additional_price
        self.location = location
        self.area = area
        self.photos = photos


class Scraper:
    OLX_SITE = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/gdansk/?search%5Bprivate_business%5D=private&search%5Bdist%5D=30"

    def __init__(self):
        self.website = self.OLX_SITE
        self.links = []

    @property
    def number_of_pages(self):
        return int(self.soup.find(name="a", class_="block br3 brc8 large tdnone lheight24", attrs={"data-cy": "page-link-last"}).find(name="span").text)

    @property
    def response(self):
        return requests.get(self.website)

    @property
    def soup(self):
        return BeautifulSoup(self.response.content, "lxml")


    def update_links(self):
        for page_number in range(1, self.number_of_pages + 1):
            if not page_number == 1:
                self.change_page(page_number)
                self.get_links()
            else:
                self.get_links()

    def get_offers_table(self):
        return self.soup.find(name="table", class_="fixed offers breakword redesigned")

    def get_a_tags(self):
        offers_table = self.get_offers_table()
        a_tags = offers_table.find_all(name="a", class_="marginright5 link linkWithHash detailsLink")
        a_tags.extend(offers_table.find_all(name="a", class_="marginright5 link linkWithHash detailsLinkPromoted"))
        return a_tags

    def get_links(self):
        a_tags = self.get_a_tags()
        self.links.extend([a_tag["href"] for a_tag in a_tags])

    def change_page(self, number):
        self.website = self.OLX_SITE + "&page={}".format(number)
        print(self.website)

    def show_links(self):
        pprint.pprint(self.links)


scraper = Scraper()
scraper.update_links()
print(len(set(scraper.links)))
scraper.show_links()
