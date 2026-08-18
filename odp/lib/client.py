from typing import Any

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session


class ODPAPIError(Exception):
    def __init__(self, status_code, error_detail):
        self.status_code = status_code
        self.error_detail = error_detail


class ODPBaseClient:
    """Base class for ODP API access using an authorized OAuth2 client."""

    def __init__(
            self,
            api_url: str,
            hydra_url: str = None,
            client_id: str = None,
            client_secret: str = None,
            scope: list[str] = None,
            auth_url: str = None,
    ) -> None:
        self.api_url = api_url
        self.auth_url = auth_url or hydra_url
        self.hydra_url = self.auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope or []

    @property
    def token(self) -> dict:
        raise NotImplementedError

    def get(self, path: str, **params: Any) -> Any:
        return self.request('GET', path, data=None, **params)

    def post(self, path: str, data: dict, **params: Any) -> Any:
        return self.request('POST', path, data=data, **params)

    def stream_post(self, path: str, data: dict, **params: Any) -> Any:
        return self.request('POST', path, data=data, stream=True, **params)

    def put(self, path: str, data: dict, **params: Any) -> Any:
        return self.request('PUT', path, data=data, **params)

    def delete(self, path: str, **params: Any) -> Any:
        return self.request('DELETE', path, None, **params)

    def request(
            self,
            method: str,
            path: str,
            *,
            data: dict = None,
            return_bytes: bool = False,
            stream: bool = False,
            **params: Any,
    ) -> Any:
        api_url = params.pop('api_url', self.api_url)
        headers = {}
        if data is not None:
            headers |= {'Content-Type': 'application/json'}
        if not return_bytes and not stream:
            headers |= {'Accept': 'application/json'}

        try:
            r = self._send_request(
                method,
                api_url + path,
                data,
                params,
                headers,
                stream=stream
            )
            r.raise_for_status()

            if stream:
                return r
            return r.content if return_bytes else r.json()

        except requests.RequestException as e:
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    error_detail = e.response.json()
                except ValueError:
                    error_detail = e.response.text
            else:
                status_code = 503
                error_detail = str(e)

            raise ODPAPIError(status_code, error_detail) from e

        except OAuthError as e:
            raise ODPAPIError(401, str(e)) from e

    def _send_request(
            self,
            method: str,
            url: str,
            data: dict | None,
            params: dict,
            headers: dict,
            stream: bool = False,
    ) -> requests.Response:
        raise NotImplementedError


class ODPClient(ODPBaseClient):
    """A client for ODP API access with a client credentials grant."""

    def __init__(
            self,
            api_url: str,
            hydra_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
    ):
        super().__init__(api_url, hydra_url, client_id, client_secret, scope)
        self._token = None

    @property
    def token(self) -> dict:
        if self._token is None:
            token_url = f'{self.auth_url}/protocol/openid-connect/token'
            session = OAuth2Session(
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=' '.join(self.scope),
            )
            try:
                self._token = session.fetch_token(
                    url=token_url,
                    grant_type='client_credentials',
                    timeout=10.0,
                )
            except Exception:
                self._token = session.fetch_token(
                    url=f'{self.auth_url}/oauth2/token',
                    grant_type='client_credentials',
                    timeout=10.0,
                )

        return self._token

    def _send_request(
            self,
            method: str,
            url: str,
            data: dict | None,
            params: dict,
            headers: dict,
            stream: bool = False,
    ) -> requests.Response:
        for _ in range(2):
            headers |= {
                'Authorization': 'Bearer ' + self.token['access_token']
            }
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                stream=stream,
            )
            if response.status_code == 403:
                # the token has probably expired; fetch a new one and try once more
                self._token = None
            else:
                break

        return response
