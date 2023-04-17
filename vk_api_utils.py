from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# class VkApiClient:


with open('vktoken.txt', encoding='utf-8') as vk_file:
    # токен ВК из файла
    token = vk_file.read()

vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)


def write_msg(user_id, message):
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    })


def vk_long_poll():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if request == "привет":
                    write_msg(user_id, f"Хай, {event.user_id}")
                elif request == "пока":
                    write_msg(user_id, "Пока((")
                else:
                    write_msg(user_id, "Не поняла вашего ответа...")