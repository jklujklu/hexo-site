import requests
from requests.cookies import cookiejar_from_dict

base_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'
}


def do_get(url, params=None, headers=None, is_json=False, call_back=''):
    if headers is not None:
        headers = base_header
    rs = requests.get(url, params=params, headers=headers)
    rs.encoding = 'utf-8'
    if rs.status_code == 200:
        if call_back != '':
            return rs.text.replace(call_back + '=', '').strip(';')
        elif is_json:
            return rs.json()
        else:
            return rs.text
    else:
        return False


def dict_2_str(cookies_dict):
    cookie_str = ''
    for key in cookies_dict.keys():
        cookie_str += '{}={};'.format(key.strip(), cookies_dict[key].strip())
    return cookie_str


def str_2_jar(cookies_str):
    cookies_dict = {}
    cookies = cookies_str.split(';')
    for item in cookies:
        if item == '':
            continue
        name, key = item.split('=', 1)
        cookies_dict.update({name: key})
    return cookiejar_from_dict(cookies_dict)


def dict_2_jar(cookies_dict):
    return cookiejar_from_dict(cookies_dict)


def check_url(url):
    if url.startswith('//'):
        return 'https:' + url
    elif url.startswith('http'):
        return url
