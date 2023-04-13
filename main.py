import requests
import vk_api

class VkApiClient:
    def __init__(self, token: str, api_version: str, user_ids: str, base_url: str = "https://api.vk.com"):
        self.user_ids = user_ids
        self.token = token
        self.api_version = api_version
        self.base_url = base_url

    def general_params(self):
        return {
            'access_token': self.token,
            'v': self.api_version,
        }

    def get_photos(self, album_id='profile', extended=1, photo_sizes=1):
        """
        Метод получает список фотографий по выбранному альбому
        :param
        album_id:
            wall — фотографии со стены,
            profile — фотографии профиля,
            saved — сохраненные фотографии. Возвращается только с ключом доступа пользователя.
        extended=1 возвращаются дополнительные поля:
            likes — количество отметок Мне нравится и информация о том, поставил ли лайк текущий пользователь,
            comments — количество комментариев к фотографии,
            tags — количество отметок на фотографии,
            can_comment — может ли текущий пользователь комментировать фото (1 — может, 0 — не может),
            reposts — число репостов фотографии.
        """
        params = {
            'owner_id': self.user_ids,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes
        }
        response = requests.get(f'{self.base_url}/method/photos.get',
                                params={**params, **self.general_params()})
        check = response.json()
        if 'error' in check.keys():
            print('Ошибка:', check['error']['error_msg'])
        else:
            return response.json()

    with open('vktoken.txt', encoding='utf-8') as vk_file:
        # токен ВК из файла
        vk_token = vk_file.read()