import unittest
import sys

try:
    from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

class TestAuthAndSecurity(unittest.TestCase):

    @unittest.skipUnless(HAS_JWT, "PyJWT or Passlib dependencies not installed on local host environment")
    def test_password_hashing_and_verification(self):
        raw_pwd = "SuperSecretPassword123"
        hashed = get_password_hash(raw_pwd)
        self.assertNotEqual(raw_pwd, hashed)
        self.assertTrue(verify_password(raw_pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    @unittest.skipUnless(HAS_JWT, "PyJWT or Passlib dependencies not installed on local host environment")
    def test_jwt_token_generation_and_decoding(self):
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        role = "candidate"
        token = create_access_token(subject=user_id, role=role)
        self.assertIsInstance(token, str)

        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.get("sub"), user_id)
        self.assertEqual(decoded.get("role"), role)

if __name__ == "__main__":
    unittest.main()
