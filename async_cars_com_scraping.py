from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser
import json
import asyncio


async def car_details_scrape(link, make, browser):
    try:
        print(link)
        page = await browser.new_page()
        await page.goto(link, timeout=0)
        html = HTMLParser(await page.content())
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
    except Exception as e:
        print("car details")
        print(str(e))


async def scrape_search_page(link, browser, make, semaphore):
    try:
        if "&page=4" in link:
            return

        page = await browser.new_page()
        await page.goto(link, timeout=0)
        html = HTMLParser(await page.content())
        node_attrs = html.css_first("section.sds-page-container").css_first("div.phx-connected").css_first(
            "div#search-live-content")
        if node_attrs:
            count = 0
            tasks = []
            for n in node_attrs.css_first("div.sds-page-section__content").css_first("div.vehicle-cards").css(
                    ".vehicle-card"):
                if "inventory-ad" not in n.attributes["class"]:
                    # print(count, n.attributes["id"].replace("vehicle-card-", ""))
                    tasks.append(car_details_scrape(
                        "https://www.cars.com/vehicledetail/" + n.attributes["id"].replace("vehicle-card-",
                                                                                           "") + "/",
                        make, browser))
                    count += 1

            await asyncio.gather(*tasks)
            print("task")
            if node_attrs.css_first("div.sds-page-section__content").css_first("div.vehicle-cards").css_first(
                    "nav.sds-pagination").css_first("div.sds-pagination__controls").css(".sds-button")[
                -1].attributes.get('href'):
                print("pagination")
                await scrape_search_page(link="https://www.cars.com" +
                                              node_attrs.css_first("div.sds-page-section__content").css_first(
                                                  "div.vehicle-cards").css_first(
                                                  "nav.sds-pagination").css_first(
                                                  "div.sds-pagination__controls").css(
                                                  ".sds-button")[
                                                  -1].attributes[
                                                  'href'], browser=browser, make=make, semaphore=semaphore)

    except Exception as e:
        print("search page")
        print(str(e))


async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            make = "acura"
            model = "acura-mdx"
            maximum_distance = "all"
            zip_code = ""
            base_url = f"https://www.cars.com/shopping/results/?stock_type=all&makes%5B%5D={make}&models%5B%5D={model}&maximum_distance={maximum_distance}&zip={zip_code}"
            # asyncio.run(scrape_search_page(link=base_url, browser=browser, make=make))
            semaphore = asyncio.Semaphore(10)
            await scrape_search_page(link=base_url, browser=browser, make=make, semaphore=semaphore)
            await browser.close()
        except Exception as e:
            print("main")
            print(str(e))


if __name__ == '__main__':
    asyncio.run(main())
