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
        if len(str(entry.get(title_column, ''))) > 30
    )


def find_books_by_author(data: list[dict], author_query: str, author_col: str, date_col: str) -> list[dict]:
    matches = []
    for book in data:
        raw_date = book.get(date_col, '').strip()
        try:
            date_part = raw_date.split()[0]  
            year = int(date_part.split('.')[2])  
        except (ValueError, IndexError, AttributeError):
            continue

        if author_query.lower() in str(book.get(author_col, '')).lower() and year >= 2018:
            matches.append(book)

    return matches


def save_bibliography(data: list[dict], filename: str, author_col: str, title_col: str, date_col: str, count: int = 20):
    actual_count = min(count, len(data))
    selected = random.sample(data, actual_count)

    with open(filename, 'w', encoding='utf-8') as out_file:
        for index, record in enumerate(selected, start=1):
            author = record.get(author_col, 'Неизвестный автор')
            title = record.get(title_col, 'Без названия')
            
            raw_date = record.get(date_col, '')
            try:
                year = raw_date.split()[0].split('.')[2]
            except (IndexError, AttributeError):
                year = raw_date  

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


def get_unique_xml_tags(path: str) -> set[str]:
    """Допзадание: перечень всех тегов без повторений для XML"""
    tree = ET.parse(path)
    return {elem.tag for elem in tree.iter()}


def top_books(data: list[dict], title_col: str, downloads_col: str = 'Кол-во выдач', limit: int = 20):
    """
    Умный поиск популярных книг. Если есть колонка с выдачами - сортирует по ней.
    Если колонки нет - считает частоту появления названия в файле.
    """
    if data and downloads_col in data[0]:
        def get_downloads(book):
            try:
                return int(book.get(downloads_col, 0))
            except ValueError:
                return 0
                
        sorted_books = sorted(data, key=get_downloads, reverse=True)
        return [(book.get(title_col, ''), get_downloads(book)) for book in sorted_books[:limit]]
    else:
        title_counter = Counter(book.get(title_col, '') for book in data if book.get(title_col))
        return title_counter.most_common(limit)


if __name__ == '__main__':
    COL_TITLE = 'Название'
    COL_AUTHOR = 'Автор'
    COL_DATE = 'Дата поступления'

    try:
        books = load_books('books.csv')
    except FileNotFoundError:
        print("Ошибка: Файл books.csv не найден!")
        exit()

    # Задание 1
    long_count = long_title_amount(books, COL_TITLE)
    print(f'1) Количество книг с длинным названием (>30 симв.): {long_count}')

    # Задание 2
    user_author = input('\nВведите автора для поиска: ')
    matched_books = find_books_by_author(books, user_author, COL_AUTHOR, COL_DATE)
    print(f'2) Найдено книг автора (от 2018 года): {len(matched_books)}')
    for entry in matched_books[:3]:
        print(f'   - {entry.get(COL_AUTHOR)} — {entry.get(COL_TITLE)} ({entry.get(COL_DATE)})')

    # Задание 3
    save_bibliography(books, 'bibliography.txt', COL_AUTHOR, COL_TITLE, COL_DATE)
    print('\n3) Файл bibliography.txt успешно создан.')

    # Задание 4
    try:
        currency_map = parse_currency_xml('currency.xml')
        print('\n4) Пример словаря Name -> CharCode (первые 5):')
        for idx, (name, code) in enumerate(currency_map.items()):
            if idx == 5:
                break
            print(f'   {name} → {code}')
            
        # Допзадание 1: Уникальные теги
        xml_tags = get_unique_xml_tags('currency.xml')
        print(f'\nДоп 1) Уникальные теги в currency.xml: {", ".join(xml_tags)}')
    except FileNotFoundError:
        print("\nОшибка: Файл currency.xml не найден!")

    # Допзадание 2: ТОП-20 книг
    print('\nДоп 2) ТОП-20 популярных книг:')
    top_20 = top_books(books, COL_TITLE)
    for idx, (title, count) in enumerate(top_20, start=1):
        print(f'   {idx}. {title[:60]}... (Очки популярности: {count})')