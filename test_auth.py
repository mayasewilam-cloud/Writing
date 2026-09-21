import unittest
import json
import os
import sys
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app
from core.auth_store import register_student, authenticate_student, get_student_user


class TestStudentAuth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_seeded_demo_students(self):
        # Demo user ST-2026-01 should exist with password 'bio123'
        res = authenticate_student("ST-2026-01", "bio123")
        self.assertTrue(res["success"])
        self.assertEqual(res["user"]["student_id"], "ST-2026-01")

        # Wrong password rejected
        res_fail = authenticate_student("ST-2026-01", "wrongpassword")
        self.assertFalse(res_fail["success"])
        self.assertIn("Incorrect password", res_fail["error"])

    def test_register_new_student_and_login(self):
        test_id = f"TEST-USER-{uuid.uuid4().hex[:6].upper()}"
        test_pwd = "safePassword123"
        
        # Register
        resp = self.client.post("/api/auth/register", json={
            "student_id": test_id,
            "student_name": "Test Student Dynamic",
            "password": test_pwd
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["student_id"], test_id)

        # Check me (session persisted)
        me_resp = self.client.get("/api/auth/me")
        me_data = json.loads(me_resp.data)
        self.assertTrue(me_data["authenticated"])
        self.assertEqual(me_data["user"]["student_id"], test_id)

        # Logout
        logout_resp = self.client.post("/api/auth/logout")
        self.assertEqual(logout_resp.status_code, 200)

        # Check me after logout
        me_resp2 = self.client.get("/api/auth/me")
        me_data2 = json.loads(me_resp2.data)
        self.assertFalse(me_data2["authenticated"])

        # Login again
        login_resp = self.client.post("/api/auth/login", json={
            "student_id": test_id,
            "password": test_pwd
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = json.loads(login_resp.data)
        self.assertTrue(login_data["success"])
        self.assertEqual(login_data["user"]["student_id"], test_id)

    def test_duplicate_registration_prevented(self):
        # ST-2026-01 is already seeded
        resp = self.client.post("/api/auth/register", json={
            "student_id": "ST-2026-01",
            "student_name": "Duplicate Attempt",
            "password": "somepassword"
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data["success"])
        self.assertIn("already registered", data["error"])

    def test_invalid_credentials_rejected(self):
        # Non-existent user
        resp = self.client.post("/api/auth/login", json={
            "student_id": "NON-EXISTENT-ID-XYZ",
            "password": "password"
        })
        self.assertEqual(resp.status_code, 401)
        data = json.loads(resp.data)
        self.assertFalse(data["success"])

        # Short password on register
        resp2 = self.client.post("/api/auth/register", json={
            "student_id": f"SHORT-{uuid.uuid4().hex[:4].upper()}",
            "student_name": "Short Pwd",
            "password": "12"
        })
        self.assertEqual(resp2.status_code, 400)



    def test_faculty_passcode_auth(self):
        # 1. Unauthenticated faculty status
        resp = self.client.get("/api/faculty/me")
        data = json.loads(resp.data)
        self.assertFalse(data["authenticated"])

        # 2. Invalid passcode
        resp = self.client.post("/api/faculty/login", json={"passcode": "wrong_code"})
        self.assertEqual(resp.status_code, 401)

        # 3. Valid passcode (IntroKingss)
        resp = self.client.post("/api/faculty/login", json={"passcode": "IntroKingss"})
        self.assertEqual(resp.status_code, 200)

        # 4. Check faculty status
        resp = self.client.get("/api/faculty/me")
        data = json.loads(resp.data)
        self.assertTrue(data["authenticated"])

        # 5. Access faculty page as authenticated faculty
        resp = self.client.get("/faculty")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Cohort Roster", resp.data)

        # 6. Logout faculty
        resp = self.client.post("/api/faculty/logout")
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get("/api/faculty/me")
        data = json.loads(resp.data)
        self.assertFalse(data["authenticated"])

    def test_student_blocked_from_faculty_studio(self):
        # Log in as demo student
        resp = self.client.post("/api/auth/login", json={
            "student_id": "ST-2026-01",
            "password": "bio123"
        })
        self.assertEqual(resp.status_code, 200)

        # Student attempts to visit /faculty
        resp = self.client.get("/faculty")
        self.assertEqual(resp.status_code, 403)
        self.assertIn(b"Access Restricted: Student Account", resp.data)
        self.assertIn(b"ST-2026-01", resp.data)

    def test_faculty_rate_limiting_and_lockout(self):
        from core.auth_store import reset_faculty_rate_limit
        reset_faculty_rate_limit("127.0.0.1")

        # 4 failed attempts should return 401 with remaining tries
        for i in range(1, 5):
            resp = self.client.post("/api/faculty/login", json={"passcode": f"bad_code_{i}"})
            self.assertEqual(resp.status_code, 401)
            data = json.loads(resp.data)
            self.assertFalse(data["success"])
            self.assertFalse(data["locked"])
            self.assertEqual(data["attempts"], i)

        # 5th attempt triggers lockout
        resp5 = self.client.post("/api/faculty/login", json={"passcode": "bad_code_5"})
        self.assertEqual(resp5.status_code, 429)
        data5 = json.loads(resp5.data)
        self.assertTrue(data5["locked"])
        self.assertIn("locked", data5["error"].lower())

        # 6th attempt during lockout immediately blocked
        resp6 = self.client.post("/api/faculty/login", json={"passcode": "IntroKingss"})
        self.assertEqual(resp6.status_code, 429)
        data6 = json.loads(resp6.data)
        self.assertTrue(data6["locked"])

        # Reset rate limit for subsequent tests
        reset_faculty_rate_limit("127.0.0.1")

    def test_faculty_submission_deletion(self):
        from core.draft_store import save_student_draft, get_student_draft

        # 1. Create a temporary proposal draft
        test_sid = "DEL-TEST-99"
        save_student_draft(test_sid, {
            "student_id": test_sid,
            "student_name": "Temporary Test Proposal",
            "title": "A Sample Test Proposal to be Deleted"
        })
        self.assertIsNotNone(get_student_draft(test_sid))

        # 2. Unauthenticated deletion attempt should be blocked
        resp = self.client.delete(f"/api/faculty/submission/{test_sid}")
        self.assertEqual(resp.status_code, 403)

        # 3. Authenticate as faculty
        from core.auth_store import reset_faculty_rate_limit
        reset_faculty_rate_limit("127.0.0.1")
        resp_login = self.client.post("/api/faculty/login", json={"passcode": "IntroKingss"})
        self.assertEqual(resp_login.status_code, 200)

        # 4. Authenticated deletion should succeed
        resp_del = self.client.delete(f"/api/faculty/submission/{test_sid}")
        self.assertEqual(resp_del.status_code, 200)
        data_del = json.loads(resp_del.data)
        self.assertTrue(data_del["success"])

        # 5. Draft should now be gone from server
        self.assertIsNone(get_student_draft(test_sid))

        # 6. Deleting non-existent draft returns 404
        resp_del_again = self.client.delete(f"/api/faculty/submission/{test_sid}")
        self.assertEqual(resp_del_again.status_code, 404)

        # Logout faculty
        self.client.post("/api/faculty/logout")

    def test_interactive_checklist_persistence(self):
        from core.draft_store import save_student_draft, get_student_draft

        test_sid = "ST-CHECKLIST-01"
        save_student_draft(test_sid, {
            "student_id": test_sid,
            "student_name": "Checklist Test Student",
            "title": "Checklist Persistence Verification",
            "faculty_review": {
                "standing": "Minor Revisions",
                "action_items": [
                    "Fix Aim 2 control",
                    "Add buffer formulation details",
                    "Update references with recent 2024 citation"
                ]
            },
            "completed_feedback_items": ["0", "2"]
        })

        draft = get_student_draft(test_sid)
        self.assertIsNotNone(draft)
        self.assertEqual(draft["completed_feedback_items"], ["0", "2"])

        # Clean up
        from core.draft_store import delete_student_draft
        delete_student_draft(test_sid)


if __name__ == "__main__":
    unittest.main()

