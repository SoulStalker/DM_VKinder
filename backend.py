import datetime
import vk_api

from db_ops import Handling
from auth import vk_token


class VkBackend:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_user_info(self, user_id):

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation,home_town'
                                 })
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['city']['id']
                     }
        return user_info

    def search_users(self, params, user_id):

        current_year = datetime.datetime.now().year
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
                                     'sex:': sex,
                                     'status': status,
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
                search_results = {'id': user['id'], 'name': user['first_name'] + ' ' + user['last_name'], 'photo_url': receive_data[1]}
                res.append(search_results)

            # handler = Handling(user_id, search_results[user['id']], search_results['photo_url'])
            # if not handler.is_person_in_db():
            #     handler.save_search_results()

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


if __name__ == '__main__':
    vk_bot = VkBackend(vk_token)