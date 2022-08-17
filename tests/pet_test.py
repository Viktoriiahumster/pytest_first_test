from api import PetFriends
from settings import valid_email, valid_password, unvalid_password, unvalid_email
import os


pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert isinstance(result, object)
    assert 'key' in result

def test_get_api_key_for_unvalid_user(email=unvalid_email, password=unvalid_password):
    """Проверяем, что при неверно введенных данных выпадает ошибка 403, в ответе содержится сообщение 'This user wasn&#x27;t found in database'"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert isinstance(result, object)
    assert 'This user wasn&#x27;t found in database' in result

def test_create_pet_simple_correctly(name='Persik', animal_type='cat', age=5):
    """Проверяем создание записи на сайте с корректно введенными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

def test_create_pet_simple_failed(name='Persifal', animal_type='cat', age='five'):
    """Проверяем создание питомца с возможностью некорректного ввода данных: неверный тип данных"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    if type(age) == int:
       status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    else:
        raise Exception('There is a mistake')
    assert status == 200

def test_create_pet_simple_wrong_age(name='Persifal', animal_type='cat', age=-1):
    """Проверяем создание питомца с возможностью некорректного ввода данных: отрицательный возраст"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    if age > 0:
        status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    else:
        raise Exception('There is a mistake')
    assert status == 200

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

def test_get_all_pets_with_valid_key_filter(filter='my_pets'):
    """ Проверяем что запрос питомцев по фильтру 'my_pets' возвращает не пустой список"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert result['pets']

def test_add_new_pet_with_valid_data(name='Персик', animal_type='кот', age='5', pet_photo='images/original.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    """Проверяем что можно добавить питомца с корректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

def test_add_new_pet_with_wrong_file(name='Персик', animal_type='кот', age='5', pet_photo='images/test.txt'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    """Проверяем что можно добавить питомца с некорректными данными: неверный тип файла с фотографией"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, 'Лебовски', 'котяра', '4', 'images/original.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    assert status == 200
    assert pet_id not in my_pets.values()

def test_successful_update_self_pet_info(name='Пусик', animal_type='киса', age=2):
    """Проверяем возможность обновления информации о питомце"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception('There is no my pets')

def test_successful_update_self_pet_info_create_new(name='Пусик', animal_type='киса', age=-2):
    """Проверяем возможность обновления информации о питомце с некорректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, 'Лебовски', 'котяра', 4)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
    assert status == 403
    assert result['name'] == name

def test_update_self_pet_info_create_new_empty(name='', animal_type='', age=''):
    """Проверяем возможность обновления информации о питомце с нулевыми значениями данных"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, 'Лебовски', 'котяра', 4)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
    assert status == 200
    assert result['name'] == name

def test_successful_set_photo():
    """Проверяем возможность добавления фотографии в карточку питомца без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, 'Лебовски', 'котяра', 4)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.set_photo(auth_key, pet_id, 'images/original.jpg')
    assert status == 200

def test_successful_update_photo():
    """Проверяем возможность добавления фотографии в карточку питомца с имеющимся фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) > 0:
        pf.add_new_pet(auth_key, 'Лебовски', 'котяра', '4', 'images/original.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    pet_id = my_pets['pets'][len(my_pets['pets']) - 1]['id']
    status, _ = pf.set_photo(auth_key, pet_id, 'images/oboi-kot-zevaet.jpg')
    assert status == 200

