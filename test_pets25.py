import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math
import numpy as np

def chrome_options(chrome_options):
    chrome_options.binary_location = 'c:\Chrome\chromedriver.exe'
    chrome_options.add_extension('c:\Chrome\extension.crx')
    chrome_options.add_argument('--kiosk')
    return chrome_options


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # This function helps to detect that some test failed
    # and pass this information to teardown:

    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep

@pytest.fixture(autouse=True)
def testing():
    pytest.driver = webdriver.Chrome('c:\Chrome\chromedriver.exe')
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')

    yield

    pytest.driver.quit()


def test_show_my_pets():
    # Вводим email
    pytest.driver.find_element("id", 'email').send_keys('')
    # Вводим пароль

    pytest.driver.find_element("id", 'pass').send_keys('')
    # Нажимаем на кнопку входа в аккаунт

    pytest.driver.find_element("css selector", 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя

    assert pytest.driver.find_element("tag name", 'h1').text == "PetFriends"

    pytest.driver.find_element("class name", 'nav-link').click()

    # Ищем на странице все фотографии, имена, породу (вид) и возраст питомцев:
    pytest.driver.implicitly_wait(10)
    images = pytest.driver.find_elements("css selector", 'tbody>tr>th>img')
    pytest.driver.implicitly_wait(10)
    names = pytest.driver.find_elements("css selector", 'tbody>tr>td:nth-child(2)')
    pytest.driver.implicitly_wait(10)
    breed = pytest.driver.find_elements("css selector", 'tbody>tr>td:nth-child(3)')
    pytest.driver.implicitly_wait(10)
    age = pytest.driver.find_elements("css selector", 'tbody>tr>td:nth-child(4)')

    # 1. Ищем на странице общее количество питомцев
    pets_line = WebDriverWait(pytest.driver, 10).until(
        EC.visibility_of((pytest.driver.find_element("xpath", '//div[@class=".col-sm-4 left"]')))).get_attribute('innerText').splitlines()
    pets = pets_line[1].split(': ')
    pets_quantity = pets[1]

    # 1. Проверяем, что общее количество питомцев равно отдельному количеству имен животных
    assert pets_quantity == str(len(names))

    # 2. Проверяем что хотя бы у половины питомцев есть фото
    images_exists = 0
    for i in range(len(images)):
        if images[i].get_attribute('src') != '':
            images_exists += 1

    assert images_exists >= int(math.ceil(len(names) / 2)), "Животных без фото больше половины! Добавьте фото!"

    # 3. Проверяем, что на странице есть имена, порода (вид) и возраст для каждого
    for i in range(int(pets_quantity)):
        assert names[i].text != ''
        assert breed[i].text != ''
        assert age[i].text != ''

    # 4. Проверяем что у всех животных разные имена
    list_of_names = []
    for i in range(len(names)):
        list_of_names.append(names[i].get_attribute('innerText'))
    list_of_unique_names = set(list_of_names)

    assert len(list_of_names) == len(list_of_unique_names), "Некоторые животные имеют одинаковое имя!"

    # 5. Собираем массив из животных с соответствующими им характеристиками
    pets_array = []
    for i in range(int(pets_quantity)):
        pet_characteristics = []
        pet_characteristics.append(names[i].get_attribute('innerText'))
        pet_characteristics.append(breed[i].get_attribute('innerText'))
        pet_characteristics.append(age[i].get_attribute('innerText'))
        pets_array.append(pet_characteristics)

    # Дефинируем массив со всеми и массив с уникальными животными
    all_pets = np.array(pets_array)
    unique_pets = np.unique(all_pets, axis=0)

    # Проверяем, что массивы равны, чтобы исключить наличие повторяющихся питомцев
    assert len(all_pets) == len(unique_pets), "В списке есть повторяющиеся питомцы!"
