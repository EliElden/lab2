import csv
import random
import xml.etree.ElementTree as ET
from collections import Counter


def load_books(path: str) -> list[dict]:
    with open(path, encoding='cp1251') as book_file:
        reader = csv.DictReader(book_file, delimiter=';')
        return list(reader)


def long_title_amount(data: list[dict], title_column: str) -> int:
    return sum(
        1 for entry in data
        if len(entry.get(title_column, '')) > 30
    )


def find_books_by_author(data: list[dict], author_query: str,
                         author_col: str, date_col: str) -> list[dict]:
    matches = []
    for book in data:
        raw_date = book.get(date_col, '')
        try:
            date, _ = raw_date.split(' ')
            day, mouth, year = date.split('.')
            year = int(year)
        except (ValueError, IndexError):
            print('error')
            continue

        if author_query.lower() in book.get(author_col, '').lower() and year >= 2018:
            matches.append(book)

    return matches


def save_bibliography(data: list[dict], filename: str,
                      author_col: str, title_col: str, date_col: str,
                      count: int = 20):
    selected = random.sample(data, count)

    with open(filename, 'w', encoding='utf-8') as out_file:
        for index, record in enumerate(selected, start=1):
            author = record.get(author_col, '')
            title = record.get(title_col, '')
            year = record.get(date_col, '')
            out_file.write(f'{index}. {author}. {title} - {year}\n')


def parse_currency_xml(path: str) -> dict[str, str]:
    tree = ET.parse(path)
    root = tree.getroot()
    mapping = {}

    for val_elem in root.findall('.//Valute'):
        name_tag = val_elem.find('Name')
        code_tag = val_elem.find('CharCode')

        if name_tag is not None and code_tag is not None:
            mapping[name_tag.text] = code_tag.text

    return mapping


def list_unique_publishers(data: list[dict], publisher_col: str) -> set:
    return {item[publisher_col] for item in data if item.get(publisher_col)}


def top_books(data: list[dict], title_col: str, limit: int = 20):
    title_counter = Counter(book[title_col] for book in data)
    return title_counter.most_common(limit)


books = load_books('books.csv')

COL_TITLE = 'Название'
COL_AUTHOR = 'Автор'
COL_DATE = 'Дата поступления'
COL_PUBLISHER = 'Издательство'

long_count = long_title_amount(books, COL_TITLE)
print(f'1) Количество длинных названий: {long_count}')

user_author = input('Введите автора: ')
matched_books = find_books_by_author(books, user_author, COL_AUTHOR, COL_DATE)
print(f'2) Найдено книг: {len(matched_books)}')

for entry in matched_books[:3]:
    print(f'{entry[COL_AUTHOR]} — {entry[COL_TITLE]} ({entry[COL_DATE]})')

save_bibliography(books, 'bibliography.txt', COL_AUTHOR, COL_TITLE, COL_DATE)
print('3) Файл bibliography.txt успешно создан.')

currency_map = parse_currency_xml('currency.xml')
print('4) Пример словаря Name -> CharCode:')

for idx, (name, code) in enumerate(currency_map.items()):
    if idx == 5:
        break
    print(f'{name} → {code}')

pubs = list_unique_publishers(books, COL_PUBLISHER)
print(f'\nУникальных издательств: {len(pubs)}')

print('\nТОП-20 популярных книг:')
for title, count in top_books(books, COL_TITLE):
    print(f'{title} — {count}')
