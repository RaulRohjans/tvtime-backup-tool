from typing import Dict, List, Any
import requests

from src.etc import Config



def get_tvtime_cookies():
    return {'symfony': session['username']['symfony'], 'tvstRemember': session['username']['tvstRemember']}


def update_tvtime_cookies(cookies: Any) -> None:
    old_session_cookie = session['username']['symfony']
    old_remember_cookie = session['username']['tvstRemember']
    session['username']['symfony'] = cookies.get('symfony', old_session_cookie)
    session['username']['tvstRemember'] = cookies.get('tvstRemember', old_remember_cookie)


def ok_response() -> Any:
    return jsonify({'status': 'OK'})


def get(url: str, headers, update_session=True, **kwargs: Any) -> requests.Response:
    resp = requests.get(url, headers=headers, cookies=kwargs.get('cookies', {}))
    resp.raise_for_status()
    if update_session:
        update_tvtime_cookies(resp.cookies)
    return resp


def post(url: str, data: Dict[str, Any], update_session=True, **kwargs: Any) -> requests.Response:
    resp = requests.post(url, data=data, headers=Config.HEADERS, cookies=kwargs.get('cookies', {}))
    resp.raise_for_status()
    if update_session:
        update_tvtime_cookies(resp.cookies)
    return resp


def put(url: str, data: Dict[str, Any], update_session=True, **kwargs: Any) -> requests.Response:
    resp = requests.put(url, data=data, headers=Config.HEADERS, cookies=kwargs.get('cookies', {}))
    resp.raise_for_status()
    if update_session:
        update_tvtime_cookies(resp.cookies)
    return resp


def delete(url: str, data: Dict[str, Any], update_session=True, **kwargs: Any) -> requests.Response:
    resp = requests.delete(url, data=data, headers=Config.HEADERS, cookies=kwargs.get('cookies', {}))
    resp.raise_for_status()
    if update_session:
        update_tvtime_cookies(resp.cookies)
    return resp
