from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.cars.com/vehicledetail/6bf3e342-a74d-4ff0-8c6d-647bcf2329d6/", timeout=0)
    html = HTMLParser(page.content())
    info = {'title': html.css_first("h1.listing-title").text(),
            'price': html.css_first('span.primary-price').text().strip()}
    dt = html.css_first("dl.fancy-description-list").css("dt")
    dd = html.css_first("dl.fancy-description-list").css("dd")
    for data in range(len(dt)):
        if dt[data].text() != 'MPG':
            info[dt[data].text()] = dd[data].text().strip()

    info['dealer name'] = html.css_first("h3.seller-name").text().strip()
    info['dealer address'] = html.css_first("div.dealer-address").text().strip()
    print(info)

    browser.close()
