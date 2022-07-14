import requests
from bs4 import BeautifulSoup

# Global Vars
user_obj = {}


def do_login(username, password, headers):
    global user_obj

    resp_login = requests.get('https://www.tvtime.com/login', headers=headers)
    resp_login.raise_for_status()

    post_data = {
        'symfony': resp_login.cookies['symfony'],
        'username': username,
        'password': password
    }
    resp_signin = requests.post('https://www.tvtime.com/signin',
                                data=post_data,
                                headers=headers)
    resp_signin.raise_for_status()

    if len(resp_signin.history) == 0 or 'symfony' not in resp_signin.history[0].cookies or 'tvstRemember' not in \
            resp_signin.history[0].cookies:
        return None

    user_id = __get_user_id(resp_signin.text)
    if len(user_id) > 0:
        return {'symfony': resp_signin.history[0].cookies['symfony'],
                    'tvstRemember': resp_signin.history[0].cookies['tvstRemember'],
                    'user_id': user_id}
    return None


def __get_user_id(html_page):
    parser = BeautifulSoup(html_page, 'html.parser')
    return parser.select_one('li.profile > a[href*="user/"]')['href'].split('/')[3]
