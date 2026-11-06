"""
Test suite for Google Email Authentication & Session Management.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from fastapi import HTTPException
from api import (
    app,
    auth_config,
    auth_google,
    auth_me,
    auth_logout,
    auth_dev_login,
    verify_google_id_token,
    GoogleAuthRequest,
    DevLoginRequest,
)
from db import (
    init_db,
    upsert_google_user,
    create_user_session,
    get_user_from_session,
    delete_session,
    DB_PATH,
)


class TestAuthDatabase(unittest.TestCase):
    """Unit tests for SQLite authentication schema and session management."""

    def setUp(self):
        init_db()

    def test_upsert_google_user(self):
        u1 = upsert_google_user(
            google_id="gid_99901",
            email="scholar@vtu.ac.in",
            name="VTU Student",
            picture="https://example.com/pic.jpg",
            email_verified=True,
        )
        self.assertEqual(u1["email"], "scholar@vtu.ac.in")
        self.assertEqual(u1["google_id"], "gid_99901")
        self.assertEqual(u1["name"], "VTU Student")

        # Update existing user
        u2 = upsert_google_user(
            google_id="gid_99901",
            email="scholar@vtu.ac.in",
            name="VTU Senior Scholar",
            picture="https://example.com/pic2.jpg",
        )
        self.assertEqual(u2["id"], u1["id"])
        self.assertEqual(u2["name"], "VTU Senior Scholar")

    def test_session_lifecycle(self):
        u = upsert_google_user(
            google_id="gid_session_test",
            email="session_test@vtu.ac.in",
            name="Session Tester",
        )
        token = create_user_session(u["id"], duration_days=7)
        self.assertTrue(len(token) > 20)

        # Retrieve valid session
        found = get_user_from_session(token)
        self.assertIsNotNone(found)
        self.assertEqual(found["id"], u["id"])
        self.assertEqual(found["email"], "session_test@vtu.ac.in")

        # Delete session
        deleted = delete_session(token)
        self.assertTrue(deleted)
        self.assertIsNone(get_user_from_session(token))

    def test_invalid_and_expired_session(self):
        self.assertIsNone(get_user_from_session("non_existent_token"))
        self.assertIsNone(get_user_from_session(""))

        u = upsert_google_user(
            google_id="gid_expired_test",
            email="expired@vtu.ac.in",
            name="Expired Tester",
        )
        # Create expired session with negative duration
        token = create_user_session(u["id"], duration_days=-1)
        self.assertIsNone(get_user_from_session(token))


class TestAuthAPI(unittest.TestCase):
    """API endpoint tests for Google Identity & Session endpoints."""

    def setUp(self):
        init_db()

    def test_auth_config_unconfigured(self):
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": ""}):
            cfg = auth_config()
            self.assertFalse(cfg["configured"])
            self.assertTrue(cfg["dev_mode"])

    def test_auth_config_configured(self):
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "12345.apps.googleusercontent.com"}):
            cfg = auth_config()
            self.assertTrue(cfg["configured"])
            self.assertEqual(cfg["google_client_id"], "12345.apps.googleusercontent.com")

    def test_verify_google_id_token_empty_reject(self):
        with self.assertRaises(ValueError):
            verify_google_id_token("")
        with self.assertRaises(ValueError):
            verify_google_id_token("   ")

    def test_verify_google_id_token_invalid(self):
        with self.assertRaises(ValueError):
            verify_google_id_token("invalid_header.invalid_payload.invalid_signature")

    def test_auth_google_endpoint_rejects_invalid(self):
        req = GoogleAuthRequest(credential="bogus.jwt.token")
        with self.assertRaises(HTTPException) as ctx:
            auth_google(req)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_auth_google_valid_flow(self):
        # Use simulated test token format supported by verify_google_id_token
        test_cred = "test_token_:google.user@gmail.com:Google Student:sub_google_12345"
        req = GoogleAuthRequest(credential=test_cred)
        resp = auth_google(req)

        self.assertTrue(resp["success"])
        self.assertIn("token", resp)
        self.assertEqual(resp["user"]["email"], "google.user@gmail.com")
        self.assertEqual(resp["user"]["name"], "Google Student")

        # Test auth_me with Bearer token
        me_resp = auth_me(authorization=f"Bearer {resp['token']}")
        self.assertTrue(me_resp["authenticated"])
        self.assertEqual(me_resp["user"]["email"], "google.user@gmail.com")

        # Test auth_logout
        logout_resp = auth_logout(authorization=f"Bearer {resp['token']}")
        self.assertTrue(logout_resp["success"])

        # After logout, auth_me should fail with 401
        with self.assertRaises(HTTPException) as ctx:
            auth_me(authorization=f"Bearer {resp['token']}")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_auth_me_unauthorized(self):
        with self.assertRaises(HTTPException) as ctx:
            auth_me(authorization=None)
        self.assertEqual(ctx.exception.status_code, 401)

        with self.assertRaises(HTTPException) as ctx:
            auth_me(authorization="Bearer invalid_token_123")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_dev_login(self):
        req = DevLoginRequest(email="devstudent@vtu.ac.in", name="Dev VTU Scholar")
        resp = auth_dev_login(req)
        self.assertTrue(resp["success"])
        self.assertEqual(resp["user"]["email"], "devstudent@vtu.ac.in")
        self.assertEqual(resp["user"]["name"], "Dev VTU Scholar")

        # Verify session is active
        me_resp = auth_me(authorization=f"Bearer {resp['token']}")
        self.assertTrue(me_resp["authenticated"])
        self.assertEqual(me_resp["user"]["email"], "devstudent@vtu.ac.in")


if __name__ == "__main__":
    unittest.main()
