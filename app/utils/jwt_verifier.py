from fastapi import status
from jose import jwt

from app.app_exception.app_exception import AppException


def verify_access_token(token: str, jwks, COGNITO_ISSUER) -> dict:
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    key = next(k for k in jwks["keys"] if k["kid"] == kid)

    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        options={"verify_aud": False},
    )

    if payload.get("token_use") != "access":
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token",
        )

    return payload
