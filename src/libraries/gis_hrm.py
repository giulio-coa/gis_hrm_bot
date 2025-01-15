from requests import get, post
from typing import Any


class GIS_HRM_Exception(Exception):
    pass


class GIS_HRM_API:
    def __init__(self, url, username, password):
        if not url:
            raise GIS_HRM_Exception(
                'Missing url parameter in the initialization of the class GIS_HRM_API.'
            )
        elif not username:
            raise GIS_HRM_Exception(
                'Missing username parameter in the initialization of the class GIS_HRM_API.'
            )
        elif not password:
            raise GIS_HRM_Exception(
                'Missing password parameter in the initialization of the class GIS_HRM_API.'
            )

        self.url = url
        self.username = username
        self.password = password

        self.login()

    def __del__(self):
        self.logout()

    def _request(self, method='GET', endpoint=None, headers=None, body=None) -> "dict[str, Any]":
        if not endpoint:
            raise GIS_HRM_Exception(
                'Missing endpoint parameter in the request to the GIS HRM API.'
            )

        if method == 'GET':
            response = get(
                f'{self.url}{endpoint}',
                params=body,
                headers=headers
            )
        elif method == 'POST':
            response = post(
                f'{self.url}{endpoint}',
                json=body,
                headers=headers
            )
        else:
            raise GIS_HRM_Exception(
                f'{method} is an unsupported HTTP method from the GIS HRM API.'
            )

        if not response.ok:
            raise GIS_HRM_Exception(f'Failed to call the {endpoint} endpoint of the GIS HRM API.')

        return response.json()

    def login(self) -> None:
        response = self._request(
            method='POST',
            endpoint='login.php',
            headers={
                'Authorization': 'Basic',
            },
            body={
                'username': self.username,
                'password': self.password,
            }
        )

        if not response.get('success'):
            raise GIS_HRM_Exception(
                'Call the login.php endpoint of the GIS HRM API and got failed.'
            )
        elif not response.get('token'):
            raise GIS_HRM_Exception('Retrieved empty token from the GIS HRM API.')

        self.token = response.get('token')

    def logout(self) -> None:
        self._request(
            method='POST',
            endpoint='login.php',
            headers={
                'Authorization': f'Bearer {self.token}',
            },
            body={
                'action': 'logout',
            }
        )

    def punch(
        self,
        out: bool = False,
    ) -> None:
        response = self._request(
            endpoint='presenze.php',
            headers={
                'Authorization': f'Bearer {self.token}',
            },
            body={
                'action': 'timbra',
                'state': out,
            }
        )

        if not response.get('success'):
            raise GIS_HRM_Exception(
                'Call the presenze.php endpoint of the GIS HRM API and got failed.'
            )
