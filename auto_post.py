from bs4 import BeautifulSoup
import time

import vk_api
import requests

import pymysql


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)


LOGIN = 'ypur_login_vk'
PASSWORD = 'your_pass_vk'#изм. данные
OWNER_ID = 'your_id_vk'
vk = vk_api.VkApi(LOGIN, PASSWORD, captcha_handler=captcha_handler)
vk.auth()
global igh, href, flag

t2 = ['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
      '15:00',
      '16:00', '17:00', '18:00', '19:00', '20:00']

headers1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
}
data = {
    'Password': 'your_pass',
    'Email': 'your_mail',
    '__RequestVerificationToken': 'your token'
}

url = 'https://tatarlove.ru/Profile/Login'
session = requests.Session()  # Сессия
r = session.get(url, headers=headers1)
session.headers.update({'Referer': url})
_xsrf = session.cookies.get('_xsrf', domain=".tatarlove.ru")
post_request = session.post(url, data)
scr = session.get('https://tatarlove.ru/Users/Popular', headers=headers1)
soup = BeautifulSoup(scr.text, 'lxml')
f = soup.find('h1', class_="card-title black-text").find_parent().find_all('div', class_='card-stacked')


def s(t, file):
    connection = pymysql.connect(
        host='your_host',#изм. данные
        port=3306,
        user='user_name',#изм. данные
        password='your_password',#изм. данные
        database='db_name',#изм. данные
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        name = t.find('a').text.strip()
        link = str(t.find('a', class_='uNameLnk').get('href'))
        link = link.replace('/', '')
        if link != '4' and link != '710232':
            link1 = f'https://tatarlove.ru/{link}'
            age = t.find('span').next.next.text.strip()
            city = t.find('br').next.text.strip()
            scr1 = session.get(f'https://tatarlove.ru/{link}', headers=headers1)
            soup1 = BeautifulSoup(scr1.text, 'lxml')
            gender = soup1.find('div', class_='col s3 sidepanel', id='rightColumn').find(
                class_='card-title black-text offset-s3')
            if 'её' in gender.text.strip(''):
                gender = 'ж'
            else:
                gender = 'м'
            link_image = soup1.find('div', class_='toggleRotate').find('a', class_='br').get('href')
            link_image = link_image.replace(f'/Profile/Photo/{link}#', '')
            select_all_rows = f'SELECT name FROM users'
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            p = []
            for row in rows:
                p.append(row['name'])
            len1 = len(p) + 1
            if len1 >= 500:
                delete_all_rows = "DELETE FROM users"
                cursor.execute(delete_all_rows)
                connection.commit()
            if len(file) < 18:
                if len(
                        name) < 12 and f'https://st.tatarlove.ru/690x590xR/{link_image[0:2]}/{link_image[2:4]}/{link_image[4:6]}' \
                                       f'/{link_image}.jpg|||{name}, {age}. {city}|||{link1}|||{gender}' not in p:
                    file.append(f'https://st.tatarlove.ru/690x590xR/{link_image[0:2]}/{link_image[2:4]}/'
                                f'{link_image[4:6]}/{link_image}.jpg|||{name}, {age}. {city}|||{link1}|||{gender}')
                    val = (f'https://st.tatarlove.ru/690x590xR/{link_image[0:2]}/{link_image[2:4]}/'
                           f'{link_image[4:6]}/{link_image}.jpg|||{name}, {age}. {city}|||{link1}|||{gender}', len1)
                    cursor.execute('INSERT INTO users(name,id) values(%s,%s)', val)
                    connection.commit()
        return file


named_tuple = time.localtime()
time_string = time.strftime("%H:%M", named_tuple)


def vk_post(href):
    global igh, jk
    href = href.split('|||')
    rs1 = vk.method('photos.getWallUploadServer', {
        'group_id': 'group_id'#изм. данные
    })['upload_url']
    p = requests.get(href[0])
    image_data = p.content
    e = eval(requests.post(rs1, files={'photo': (f'image.jpg', image_data)}).text)
    rs2 = vk.method('photos.saveWallPhoto', {
        'group_id': 'group_id',#изм. данные
        'server': e['server'],
        'hash': e['hash'],
        'photo': e['photo']
    })
    rs = vk.method('wall.post', {
        'owner_id': 'owner_id',#изм. данные
        'message': f'{href[1]}',
        'server': e['server'],
        'attachment': f'photo{rs2[0]["owner_id"]}_{rs2[0]["id"]},{href[2]}'
    })
    igh += 1


def fil(file):
    scr = session.get(f'https://tatarlove.ru/Users/Popular', headers=headers1)
    soup = BeautifulSoup(scr.text, 'lxml')
    f = soup.find('h1', class_="card-title black-text").find_parent().find_all('div', class_='card-stacked')
    for t in f:
        file = s(t, file)
        if len(file) > 17:
            break
    kl = 2
    while len(file) < 18:
        scr = session.get(f'https://tatarlove.ru/Users/Popular?p={kl}', headers=headers1)
        soup = BeautifulSoup(scr.text, 'lxml')
        f = soup.find('h1', class_="card-title black-text").find_parent().find_all('div', class_='card-stacked')
        for t in f:
            file = s(t, file)
            if len(file) > 17:
                break
        kl += 1

    return (file)


file1 = []

file1 = fil(file1)

connection = pymysql.connect(
    host='your_host',
    port=3306,
    user='user_name',
    password='your_password',
    database='db_name',
    cursorclass=pymysql.cursors.DictCursor
)
flag1 = 0
print('Работает')
flag2 = 0
flag3 = 0
flag5 = 0
flag999 = 0
with connection.cursor() as cursor:
    while 1:
        named_tuple4 = time.localtime()
        time_string4 = time.strftime("%H:%M", named_tuple4)
        time_string5 = time.strftime("%S", named_tuple4)
        if time_string4 == "03:58":
            while (time_string4 == "03:58") and int(time_string5) < 30:
                flag1 = 0
                file1 = []
                named_tuple4 = time.localtime()
                time_string5 = time.strftime("%S", named_tuple4)
            time.sleep(10)
        named_tuple4 = time.localtime()
        time_string4 = time.strftime("%H:%M", named_tuple4)
        time_string5 = time.strftime("%S", named_tuple4)
        if time_string4 == '03:59':
            while (time_string4 == '03:59') and int(time_string5) < 10:
                if flag1 == 0:
                    file1 = fil(file1)
                    flag1 = 1
                break

        for href in file1:
            try:
                igh = 0
                flag = 0
                while 1:
                    named_tuple2 = time.localtime()
                    time_string1 = time.strftime("%H:%M", named_tuple2)
                    if (str(time_string1) in t2) or time_string1 == '03:57':
                        break
                if time_string1 == '03:57':
                    break
                while time_string1 in t2:
                    named_tuple2 = time.localtime()
                    time_string1 = time.strftime("%H:%M", named_tuple2)
                    vk_post(href)
                    break
                time.sleep(120)

            except:
                continue
