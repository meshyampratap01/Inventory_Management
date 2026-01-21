from jose import jwt, JWTError


def verify_access_token(token: str) -> dict:
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    key = next(k for k in jwks["keys"] if k["kid"] == kid)

    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        options={"verify_aud": False},  # Cognito access tokens don't use aud
    )

    if payload.get("token_use") != "access":
        raise ValueError("Not an access token")

    return payload
