from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import defaultdict, OrderedDict
import pandas as pd
import datetime
import os
from dotenv import load_dotenv


def get_year_word(number):
    exceptions = range(11, 21)
    last_digit = number % 10
    if number % 100 in exceptions:
        return "лет"
    elif last_digit == 1:
        return "год"
    elif 2 <= last_digit <= 4:
        return "года"
    else:
        return "лет"


def main():
    current_year = datetime.datetime.now().year
    winery_start_year = 1920
    winery_age = current_year - winery_start_year

    load_dotenv()

    file_path = os.getenv("DATA_PATH", "wine3.xlsx")

    try:
        wines_data = pd.read_excel(file_path)
    except (FileNotFoundError, Exception) as e:
        print(f"Ошибка при чтении файла: {e}")
        wines_data = pd.DataFrame()

    wines_data = wines_data.where(pd.notna(wines_data), None)

    grouped_products = defaultdict(list)
    for _, row in wines_data.iterrows():
        category = row['Категория']
        product = {
            'Название': row['Название'],
            'Сорт': row['Сорт'] or '',
            'Цена': row['Цена'] or '',
            'Картинка': f"images/{row['Картинка']}" if row['Картинка'] else '',
            'Акция': row['Акция'] == 'Выгодное предложение'
        }
        grouped_products[category].append(product)

    desired_order = ["Белые вина", "Красные вина", "Напитки"]

    grouped_products_ordered = OrderedDict(
        {category: grouped_products[category] for category in desired_order if category in grouped_products}
    )

    sale_image = "assets/profitable.png"

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("template.html")
    rendered_page = template.render(
        grouped_products=grouped_products_ordered,
        winery_age=winery_age,
        get_year_word=get_year_word,
        sale_image=sale_image
    )

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    print("Сервер запущен на http://0.0.0.0:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()