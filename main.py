import requests
from bs4 import BeautifulSoup
import re
import csv
import os.path
from fake_useragent import UserAgent
from time import sleep


def get_info(i):
    url = "https://www.kinopoisk.ru/lists/movies/popular/?page=" + str(i)
    data = requests.get(url, headers={'User-Agent': UserAgent().chrome})
    data.encoding = 'utf-8'

    sleep(3)

    soup = BeautifulSoup(data.text, 'lxml')
    films = soup.findAll('div', class_="styles_root__ti07r")

    result = []
    for film in films:
        number = film.find('div', class_="styles_root__j_C_S") \
            .find('span', class_="styles_position__TDe4E").getText()
        russian_name = film.find('div', class_="styles_content__nT2IG") \
            .find('div', class_="styles_upper__j8BIs") \
            .find('div', class_="styles_main__Y8zDm styles_mainWithNotCollapsedBeforeSlot__x4cWo") \
            .find('div', class_="base-movie-main-info_mainInfo__ZL_u3") \
            .find('span', class_="styles_mainTitle__IFQyZ styles_activeMovieTittle__kJdJj").getText()
        is_english_name = film.find('div', class_="styles_content__nT2IG") \
            .find('div', class_="styles_upper__j8BIs") \
            .find('div', class_="styles_main__Y8zDm styles_mainWithNotCollapsedBeforeSlot__x4cWo") \
            .find('div', class_="desktop-list-main-info_secondaryTitleSlot__mc0mI") \
            .find('span', class_="desktop-list-main-info_secondaryTitle__ighTt")
        if is_english_name:
            english_name = is_english_name.getText()
        else:
            english_name = None
        year = film.find('div', class_="styles_content__nT2IG") \
            .find('div', class_="styles_upper__j8BIs") \
            .find('div', class_="styles_main__Y8zDm styles_mainWithNotCollapsedBeforeSlot__x4cWo") \
            .find('div', class_="desktop-list-main-info_secondaryTitleSlot__mc0mI") \
            .find('span', class_="desktop-list-main-info_secondaryText__M_aus").getText()

        if re.findall('\d{4}–...', year):
            year = re.findall('\d{4}–...', year)[0]
        else:
            year = re.findall('\d{4}', year)[0]

        is_rate = film.find('div', class_="styles_content__nT2IG") \
            .find('div', class_="styles_upper__j8BIs") \
            .find('div', class_="styles_user__2wZvH") \
            .find('div', class_="styles_rating__LU3_x") \
            .find('div', class_="styles_kinopoisk__JZttS")
        if is_rate:
            rate = is_rate.find('div', class_="styles_kinopoiskValueBlock__qhRaI").getText()
        else:
            rate = None

        result.append((number, russian_name, english_name, year, rate))

    if result:
        with open('data.csv', mode='a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(result)
        return True
    else:
        return False


if __name__ == '__main__':
    if os.path.exists('data.csv'):
        os.remove('data.csv')

    cnt = 1
    while cnt <= 20:
        if get_info(cnt):
            print("Successful parsing of page " + str(cnt))
            cnt += 1
            sleep(3)
        else:
            print("Whoops, got a captcha! Sleeping for a minute...")
            sleep(60)

    print("Successfully parsed 20 pages!")
