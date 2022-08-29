# -*- coding:utf-8 -*-

import os
import logging
from unicodedata import name
import pdfkit
import requests
from bs4 import BeautifulSoup
import os.path

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""

def get_url_list():
    response = requests.get("http://www.yinwang.org/")
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="list-group")[0] 
    urls = []
    for li in menu_tag.find_all("li"):
        url = "http://www.yinwang.org" + li.a.get('href')
        urls.append(url)
    return urls

def parse_url_to_html(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        inner = soup.find_all(class_="inner")
        if inner.__len__() == 0:
            return ""
        body = inner[0]
        
        title = soup.find('h2').get_text()
        soup.select_one("h2").decompose()

        center_tag = soup.new_tag("center")
        title_tag = soup.new_tag('h1')
        title_tag.string = title
        center_tag.insert(1, title_tag)
        body.insert(1, center_tag)

        for img in body.find_all("img"):
            img['style'] = "display: block; margin-left: auto; margin-right: auto;"

        html = str(body)
        html = html_template.format(content=html)

        name = title + ".html"
        name = os.path.join("html", name)
        with open(name, 'wb') as f:
            f.write(html.encode())
        return name

    except Exception as e:
        logging.error("parse error:", exc_info=True)

def save_pdf(htmls, file_name):
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'minimum-font-size': 12,
    }
    try:
        pdfkit.from_file(htmls, file_name, options=options)
    except Exception as e:
        logging.error("covert error: ", exc_info=True)

def main():
    os.mkdir("html") if not os.path.exists("html") else None
    os.mkdir("pdf") if not os.path.exists("pdf") else None

    urls = get_url_list()
    for index, url in enumerate(urls):
        html_name = parse_url_to_html(url)
        print("download index {} finished name {}".format(index, html_name))

        if html_name == "":
            continue

        pdf_name = html_name.replace("html", "pdf")
        save_pdf(html_name, pdf_name)
        print("convert index {} finished name {}".format(index, pdf_name))

if __name__ == '__main__':
    main()
