import datetime
import vk_api

from db_ops import Handling
from auth import login, passwd, vk_token


class VkBackend:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_user_info(self, user_id):
        # получение данных о пользователе по его id
        # vk = gr_session.get_api()
        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'relation,city,home_town,sex,bdate'
                                 })
        user_info = {
            'name': info['first_name'] + ' ' + info['last_name'],
            'id': info['id'],
            'bdate': info['bdate'] if 'bdate' in info else None,
            'home_town': info['home_town'] if 'home_town' in info else None,
            'sex': info['sex'],
            'city': info['city']['id'] if 'city' in info else None
        }
        return user_info

    def search_users(self, params):
        current_year = datetime.datetime.now().year
        # city = params['city']['id'],
        age_from = current_year - int(params['bdate'].split('.')[2]) - 4,
        age_to = current_year - int(params['bdate'].split('.')[2]) + 4,
        sex = 1 if params['sex'] == 2 else 2,
        status = params.get('relation', 6),
        home_town = params['home_town']

        users = self.api.method('users.search',
                                {'count': 30,
                                 'offset': 0,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 # 'city': city,
                                 'sex:': sex,
                                 'status': 6,
                                 'is_closed': False,
                                 'home_town': home_town
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []
        res = []
        for user in users:
            if not user['is_closed']:
                receive_data = self.get_top_photos(user['id'])
                search_results = {'person_id': int(user['id']), 'photo_url': receive_data[1]}
                res.append(search_results)
        return res

        # handler = Handling(user_id, search_results['person_id'], search_results['photo_url'])
        # if not handler.is_person_in_db():
        #     handler.save_search_results()
        #     # возвращаем ссылку на профиль и фотки
        #     front_api.write_msg(user_id, receive_data[0], receive_data[1])
        #     # send_photo(user_id, receive_data[1])

    def get_top_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
            top_photos = sorted_photos[:3]
            photo_links = [f"photo{p['owner_id']}_{p['id']}" for p in top_photos]
            attachment = ",".join(photo_links)
            message = f"Ссылка на профиль: https://vk.com/id{user_id} \n"
            return message, attachment
        except KeyError:
            return ()


def auth_handler():
    # При двухфакторной аутентификации вызывается эта функция.
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


# vk_session = vk_api.VkApi(login, passwd, auth_handler=auth_handler)
# # Попытка авторизации
# try:
#     vk_session.auth()
# except vk_api.exceptions.AuthError as error:
#     # Обработка ошибки авторизации
#     if error.code == 4:
#         code = input('Введите код двухфакторной аутентификации: ')
#         vk_session.auth(code=code)
#     else:
#         raise error
# except vk_api.exceptions.Captcha as captcha:
#     # это помогло мне избегать ошибки капчи
#     captcha.sid
#     captcha.get_url()
#     captcha.get_image()
# 
# access_token = vk_session.token['access_token']

# vk_long_poll()
if __name__ == '__main__':
    vk_bot = VkBackend(vk_token)
    params = vk_bot.get_user_info()
