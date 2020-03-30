from typing import List

from bs4 import BeautifulSoup, PageElement
from pymongo import MongoClient
import requests
from pprint import pprint

# client = MongoClient("127.0.0.1")
# db = client.local
# db.test.insert_one({"1": "Witam"})
from requests import Response


class Offer:
    def __init__(self, price, description, building_type, additional_price, location, area, photos) -> None:
        self.price = price
        self.description = description
        self.building_type = building_type
        self.additional_price = additional_price
        self.location = location
        self.area = area
        self.photos = photos

    def __str__(self) -> str:
        return f"{str(self.price)}" \
               f"{self.description}" \
               f"{self.building_type}" \
               f"{self.additional_price}" \
               f"{self.location}" \
               f"{self.area}"


class LinksScraper:
    OLX_SITE = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/gdansk/?search%5Bprivate_business%5D=private&search%5Bdist%5D=30"

    def __init__(self) -> None:
        self.website = self.OLX_SITE
        self.links = []

    @property
    def number_of_pages(self) -> int:
        return int(self.soup.find(name="a", class_="block br3 brc8 large tdnone lheight24", attrs={"data-cy": "page-link-last"}).find(name="span").text)

    @property
    def response(self) -> Response:
        return requests.get(self.website)

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.response.content, "lxml")

    def update_links(self) -> None:
        for page_number in range(self.number_of_pages, 0, -1):
            if not page_number == 1:
                self.change_page(page_number)
                self.get_link()
            else:
                self.get_link()

    def get_offers_table(self) -> PageElement:
        return self.soup.find(name="table", class_="fixed offers breakword redesigned")

    def get_a_tags(self) -> PageElement:
        offers_table = self.get_offers_table()
        a_tags = offers_table.find_all(name="a", class_="marginright5 link linkWithHash detailsLink")
        a_tags.extend(offers_table.find_all(name="a", class_="marginright5 link linkWithHash detailsLinkPromoted"))
        return a_tags

    def get_link(self) -> PageElement:
        a_tags = self.get_a_tags()
        self.links.extend([a_tag["href"] for a_tag in a_tags if "olx" in a_tag["href"]])

    def change_page(self, number) -> None:
        self.website = self.OLX_SITE + "&page={}".format(number)

    def show_links(self) -> None:
        pprint.pprint(self.links)

    def get_links(self) -> list:
        return self.links


class OffersScraper:
    def __init__(self, offers_links) -> None:
        self.offers_links = offers_links
        self.offers = []
        self.link = None

    def scrape_offers(self) -> List[Offer]:
        links = []
        for offer_link in self.offers_links:
            print(offer_link)
            self.link = offer_link
            offer = Offer(
                self.get_price(),
                    self.get_description(),
                    self.get_building_type(),
                    self.get_additional_price(),
                    self.get_location(),
                    self.get_area(),
                    self.get_photos(),
                )
            self.offers.append(offer)
        return links

    @property
    def response(self) -> Response:
        return requests.get(self.link)

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.response.content, "lxml")

    def get_location(self) -> PageElement:
        a_tag_location = self.soup.find(name="a", class_="show-map-link")
        return a_tag_location.string

    def get_price(self) -> float:
        return float(self.soup.find(name="strong", class_="xxxx-large").string.replace("zł", "").replace(" ", "").replace(",", "."))

    def get_building_type(self) -> PageElement:
        table_header = self.soup.find("th", text="Rodzaj zabudowy")
        return table_header.find_parent().find(name="strong").text.strip()

    def get_area(self) -> PageElement:
        table_header = self.soup.find("th", text="Powierzchnia")
        return table_header.find_parent().find(name="strong").text.strip()

    def get_additional_price(self) -> float:
        table_header = self.soup.find("th", text="Czynsz (dodatkowo)")
        print(float(table_header.find_parent().find(name="strong").text.strip().replace("zł", "").replace(" ", "").replace(",", ".")))
        return float(table_header.find_parent().find(name="strong").text.strip().replace("zł", "").replace(" ", "").replace(",", "."))

    def get_description(self) -> PageElement:
        return self.soup.find(name="div", class_="clr lheight20 large").text.strip()

    def get_photos(self) -> list:
        photos_divs = self.soup.find_all(name="div", class_="tcenter img-item")
        photos_links = []
        for photos_div in photos_divs:
            try:
                photos_links.append(photos_div.find("img")["src"])
            except TypeError:
                continue
        return photos_links


links_scraper = LinksScraper()
links_scraper.update_links()
print(len(set(links_scraper.links)))
links_scraper.show_links()
offers_scraper = OffersScraper(links_scraper.get_links())
offers = offers_scraper.scrape_offers()
pprint(offers)




scraper = OLXScraper()
links = scraper.scrape_links()

offers = []
for link in links:
    offer = scraper.scrape_offer(link)
    offers.append(offer)
    scraper.add_offer

