import requests
import fake_headers
import bs4
import json


headers = fake_headers.Headers(browser='firefox', os='win')
headers_dict = headers.generate()

link = 'https://spb.hh.ru/search/vacancy'
params = {'area': ['1', '2'],
          'text': 'Python',
          'items_on_page': '20',
          'search_field': 'description'}


def get_vacancys():
    request = requests.get(link, params=params, headers=headers_dict)
    html = request.text
    soup = bs4.BeautifulSoup(html, "lxml")
    all_vacancy = soup.find_all('div', class_='serp-item')

    vacancy_list = {}

    for vacancy in all_vacancy:
        href = vacancy.find(class_='serp-item__title').get('href')
        vacancy_request = requests.get(href, headers=headers_dict)
        vacancy_html = vacancy_request.text
        vacancy_soup = bs4.BeautifulSoup(vacancy_html, "lxml")
        description = vacancy_soup.find('div', class_='vacancy-description')
        description_text = description.text
        if description_text.count('Django') or description_text.count('Flask'):
            company_name = vacancy_soup.find('span', class_='vacancy-company-name').text
            salary = vacancy_soup.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary is None:
                salary = 'Большая, наверное...'
            else:
                salary = salary.text.replace('\u202f', '')
            city = vacancy_soup.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]

            vacancy_list.setdefault(company_name)
            vacancy_list[company_name] = {'salary': salary}
            vacancy_list[company_name].update({'city': city})
            vacancy_list[company_name].update({'link': href})
    return vacancy_list


def write_json():
    with open('job.json', 'w', encoding='utf-8') as f:
        json.dump(get_vacancys(), f, ensure_ascii=False, indent=2)


write_json()
