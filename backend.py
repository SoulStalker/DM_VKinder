import datetime
import vk_api

from auth import vk_token


class VkBackend:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_user_info(self, user_id):

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'home_town,bdate,sex,relation,home_town'
                                 })
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'] if 'bdate' in info else None,
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     # 'home_town': info['home_town'] if 'home_town' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     'home_town': info['home_town'] if 'home_town' in info else None,
                     }
        return user_info

    def search_users(self, params, offset=0):
        current_year = datetime.datetime.now().year
        age_from = current_year - int(params['bdate'].split('.')[2]) - 10,
        age_to = current_year - int(params['bdate'].split('.')[2]) + 10,
        sex = 1 if params['sex'] == 2 else 2,
        status = params.get('relation', 6),
        home_town = params['home_town']

        users = self.api.method('users.search',
                                    {'count': 50,
                                     'offset': offset,
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

        return res

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
