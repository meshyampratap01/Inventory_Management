import unittest
from unittest.mock import patch

from fastapi import status

from app.utils.jwt_verifier import verify_access_token
from app.app_exception.app_exception import AppException


class TestVerifyAccessToken(unittest.TestCase):
    def setUp(self):
        self.token = "fake.jwt.token"
        self.issuer = "https://cognito-idp.ap-south-1.amazonaws.com/pool-id"

        self.jwks = {"keys": [{"kid": "test-kid", "kty": "RSA"}]}

        self.headers = {"kid": "test-kid"}

        self.valid_payload = {
            "sub": "user-id",
            "token_use": "access",
            "iss": self.issuer,
        }

    @patch("app.utils.jwt_verifier.jwt.decode")
    @patch("app.utils.jwt_verifier.jwt.get_unverified_header")
    def test_verify_access_token_success(
        self,
        mock_get_header,
        mock_decode,
    ):
        mock_get_header.return_value = self.headers
        mock_decode.return_value = self.valid_payload

        result = verify_access_token(
            token=self.token,
            jwks=self.jwks,
            COGNITO_ISSUER=self.issuer,
        )

        self.assertEqual(result, self.valid_payload)

        mock_decode.assert_called_once_with(
            self.token,
            self.jwks["keys"][0],
            algorithms=["RS256"],
            issuer=self.issuer,
            options={"verify_aud": False},
        )

    @patch("app.utils.jwt_verifier.jwt.decode")
    @patch("app.utils.jwt_verifier.jwt.get_unverified_header")
    def test_verify_access_token_invalid_token_use(
        self,
        mock_get_header,
        mock_decode,
    ):
        mock_get_header.return_value = self.headers
        mock_decode.return_value = {
            "token_use": "id",
            "iss": self.issuer,
        }

        with self.assertRaises(AppException) as ctx:
            verify_access_token(
                token=self.token,
                jwks=self.jwks,
                COGNITO_ISSUER=self.issuer,
            )

        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ctx.exception.message, "Invalid or expired token")

    @patch("app.utils.jwt_verifier.jwt.get_unverified_header")
    def test_verify_access_token_kid_not_found(self, mock_get_header):
        mock_get_header.return_value = {"kid": "unknown-kid"}

        with self.assertRaises(StopIteration):
            verify_access_token(
                token=self.token,
                jwks=self.jwks,
                COGNITO_ISSUER=self.issuer,
            )

    @patch("app.utils.jwt_verifier.jwt.decode")
    @patch("app.utils.jwt_verifier.jwt.get_unverified_header")
    def test_verify_access_token_decode_failure(
        self,
        mock_get_header,
        mock_decode,
    ):
        mock_get_header.return_value = self.headers
        mock_decode.side_effect = Exception("JWT decode failed")

        with self.assertRaises(Exception):
            verify_access_token(
                token=self.token,
                jwks=self.jwks,
                COGNITO_ISSUER=self.issuer,
            )
