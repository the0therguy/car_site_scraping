from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser
import json


# https://benjohnokezie.medium.com/lets-check-out-a-new-faster-web-scraping-combo-8228e7c48eb8
def car_details_scrape(link, make):
    page = browser.new_page()
    page.goto(link, timeout=0)
    html = HTMLParser(page.content())
    info = {'link': link, 'make': make, 'title': html.css_first("h1.listing-title").text(),
            'price': html.css_first('span.primary-price').text().strip()}
    dt = html.css_first("dl.fancy-description-list").css("dt")
    dd = html.css_first("dl.fancy-description-list").css("dd")
    for data in range(len(dt)):
        if dt[data].text() != 'MPG':
            info[dt[data].text()] = dd[data].text().strip()

    info['dealer name'] = html.css_first("h3.seller-name").text().strip()
    info['dealer address'] = html.css_first("div.dealer-address").text().strip()
    print(info)


def scrape_search_page(link, browser, make):
    try:
        print(link)
        if "&page=4" in link:
            return
        page = browser.new_page()
        page.goto(link, timeout=0)
        html = HTMLParser(page.content())
        # if html.css_first("cars-datalayer"):
        #     print(json.loads(html.css_first("cars-datalayer").text())[0]['vehicle_array'][1])
        node_attrs = html.css_first("section.sds-page-container").css_first("div.phx-connected").css_first(
            "div#search-live-content")
        if node_attrs:
            count = 0
            for n in node_attrs.css_first("div.sds-page-section__content").css_first("div.vehicle-cards").css(
                    ".vehicle-card"):
                if "inventory-ad" not in n.attributes["class"]:
                    print(count, n.attributes["id"].replace("vehicle-card-", ""))
                    car_details_scrape(
                        "https://www.cars.com/vehicledetail/" + n.attributes["id"].replace("vehicle-card-", "") + "/",
                        make)
                    count += 1
            if node_attrs.css_first("div.sds-page-section__content").css_first("div.vehicle-cards").css_first(
                    "nav.sds-pagination").css_first("div.sds-pagination__controls").css(".sds-button")[
                -1].attributes.get('href'):
                scrape_search_page(link="https://www.cars.com" +
                                        node_attrs.css_first("div.sds-page-section__content").css_first(
                                            "div.vehicle-cards").css_first(
                                            "nav.sds-pagination").css_first("div.sds-pagination__controls").css(
                                            ".sds-button")[
                                            -1].attributes[
                                            'href'], browser=browser, make=make)

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch()
        make = "acura"
        model = "acura-mdx"
        maximum_distance = "all"
        zip_code = ""
        base_url = f"https://www.cars.com/shopping/results/?stock_type=all&makes%5B%5D={make}&models%5B%5D={model}&maximum_distance=all&zip={zip_code}"
        scrape_search_page(base_url, browser, make)
        browser.close()
