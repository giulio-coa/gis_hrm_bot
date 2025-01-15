from json import dumps
from typing import Any

from requests import get, post


class GIS_HRM_Exception(Exception):
    pass


class GIS_HRM_API:
    def __init__(
        self,
        url: str,
        username: str,
        password: str
    ):
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

        self.url = f"{url.rstrip('/')}/"
        self.username = username
        self.password = password
        self.token = None

        self.login()

    def __del__(self):
        if self.token:
            self.logout()

    def _request(
        self,
        method: str = 'GET',
        endpoint: str = None,
        headers: "dict[str, str]" = None,
        body: "dict[str, Any]" = None
    ) -> "dict[str, Any]":
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
                data=body,
                headers=headers
            )
        else:
            raise GIS_HRM_Exception(
                f'{method} is an unsupported HTTP method from the GIS HRM API.'
            )

        response.raise_for_status()

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
                'Call the login.php endpoint of the GIS HRM API and got failed.\n\t{}'.format(
                    response.get('message')
                )
            )
        elif not response.get('token'):
            raise GIS_HRM_Exception(
                'Retrieved empty token from the GIS HRM API.\n\t{}'.format(
                    dumps(response, indent=2, default=str)
                )
            )

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
                'state': 1 if out else 0,
            }
        )

        if not response.get('success'):
            raise GIS_HRM_Exception(
                'Call the presenze.php endpoint of the GIS HRM API and got failed.\n\t{}'.format(
                    response.get('message')
                )
            )
