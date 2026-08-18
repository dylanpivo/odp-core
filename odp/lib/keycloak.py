from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import jwt
from jwt import PyJWKClient
import requests


@dataclass
class ValidatedToken:
    active: bool
    sub: Optional[str] = None
    client_id: Optional[str] = None
    scope: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = None


class JWTVerifier:
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self.jwk_client = PyJWKClient(jwks_url)

    def verify_token(self, token: str) -> ValidatedToken:
        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "HS256"],
                options={"verify_aud": False},
            )
            sub = payload.get("sub")
            client_id = payload.get("client_id") or payload.get("azp") or sub
            scope = payload.get("scope", "")
            email = payload.get("email")
            realm_access = payload.get("realm_access", {})
            roles = realm_access.get("roles", [])

            return ValidatedToken(
                active=True,
                sub=sub,
                client_id=client_id,
                scope=scope,
                email=email,
                roles=roles,
            )
        except Exception:
            return ValidatedToken(active=False)


class KeycloakAdminAPI:
    def __init__(self, auth_url: str, admin_user: str = "admin", admin_pass: str = "admin"):
        self.auth_url = auth_url.rstrip("/")
        self.realm = self.auth_url.split("/realms/")[-1] if "/realms/" in self.auth_url else "odp"
        self.base_admin_url = self.auth_url.split("/realms/")[0]
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self._token: Optional[str] = None

    def _get_admin_token(self) -> str:
        if not self._token:
            token_url = f"{self.base_admin_url}/realms/master/protocol/openid-connect/token"
            res = requests.post(
                token_url,
                data={
                    "client_id": "admin-cli",
                    "username": self.admin_user,
                    "password": self.admin_pass,
                    "grant_type": "password",
                },
                timeout=10,
            )
            if res.status_code == 200:
                self._token = res.json().get("access_token")
        return self._token or ""

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_admin_token()}",
            "Content-Type": "application/json",
        }

    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_admin_url}/admin/realms/{self.realm}/clients?clientId={client_id}"
        try:
            res = requests.get(url, headers=self._headers(), timeout=10)
            if res.status_code == 200 and res.json():
                return res.json()[0]
        except Exception:
            pass
        return None

    def create_or_update_client(
        self,
        id: str,
        name: str,
        secret: Optional[str] = None,
        redirect_uris: Optional[List[str]] = None,
        allowed_cors_origins: Optional[List[str]] = None,
    ) -> None:
        existing = self.get_client(id)
        payload = {
            "clientId": id,
            "name": name,
            "enabled": True,
            "protocol": "openid-connect",
            "redirectUris": redirect_uris or ["*"],
            "webOrigins": allowed_cors_origins or ["*"],
        }
        if secret:
            payload["secret"] = secret
            payload["serviceAccountsEnabled"] = True
            payload["directAccessGrantsEnabled"] = True

        if existing:
            kc_id = existing["id"]
            url = f"{self.base_admin_url}/admin/realms/{self.realm}/clients/{kc_id}"
            requests.put(url, json=payload, headers=self._headers(), timeout=10)
        else:
            url = f"{self.base_admin_url}/admin/realms/{self.realm}/clients"
            requests.post(url, json=payload, headers=self._headers(), timeout=10)

    def delete_client(self, client_id: str) -> None:
        existing = self.get_client(client_id)
        if existing:
            kc_id = existing["id"]
            url = f"{self.base_admin_url}/admin/realms/{self.realm}/clients/{kc_id}"
            requests.delete(url, headers=self._headers(), timeout=10)
