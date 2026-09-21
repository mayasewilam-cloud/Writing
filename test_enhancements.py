import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, sanitize_draft_for_student
from core.draft_store import (
    save_student_draft,
    get_student_draft,
    toggle_draft_lock,
    dispatch_faculty_feedback
)

class TestProposalEnhancements(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.test_sid = 'TEST-ENHANCE-01'
        self.sample_data = {
            'student_id': self.test_sid,
            'student_name': 'Test Researcher',
            'title': 'Synthetic Biosensor for Water Analysis',
            'modality': 'Cell-Free Diagnostics',
            'chassis': 'Cell-free Tx-Tl lysate',
            'tool': 'Cas12a fluorescent assay',
            'target': 'Antimicrobial resistance marker'
        }
        save_student_draft(self.test_sid, self.sample_data)

    def tearDown(self):
        drafts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'drafts'))
        fpath = os.path.join(drafts_dir, f'{self.test_sid}.json')
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

    def test_toggle_draft_lock_direct(self):
        draft = get_student_draft(self.test_sid)
        self.assertFalse(draft.get('is_locked_for_grading', False))

        res = toggle_draft_lock(self.test_sid, True)
        self.assertTrue(res['success'])
        self.assertTrue(res['is_locked_for_grading'])

        draft = get_student_draft(self.test_sid)
        self.assertTrue(draft.get('is_locked_for_grading'))
        self.assertIsNotNone(draft.get('locked_at'))

        res = toggle_draft_lock(self.test_sid, False)
        self.assertTrue(res['success'])
        self.assertFalse(res['is_locked_for_grading'])

        draft = get_student_draft(self.test_sid)
        self.assertFalse(draft.get('is_locked_for_grading'))

    def test_toggle_draft_lock_api(self):
        resp = self.client.post('/api/student/toggle_lock', json={
            'student_id': self.test_sid,
            'is_locked': True
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_locked_for_grading'])

        draft = get_student_draft(self.test_sid)
        self.assertTrue(draft.get('is_locked_for_grading'))

    def test_dispatch_feedback_requires_faculty_auth(self):
        resp = self.client.post('/api/instructor/dispatch_feedback', json={
            'student_id': self.test_sid,
            'gpa': 9.2,
            'raw_total': 78.0,
            'standing': '🌟 Grant-Ready'
        })
        self.assertEqual(resp.status_code, 401)

    def test_dispatch_feedback_authenticated_faculty(self):
        with self.client.session_transaction() as sess:
            sess['faculty_authenticated'] = True

        resp = self.client.post('/api/instructor/dispatch_feedback', json={
            'student_id': self.test_sid,
            'instructor_name': 'Dr. Biosensor',
            'gpa': 8.8,
            'raw_total': 75.0,
            'standing': '🌟 Grant-Ready',
            'criterion_overrides': {
                'background': {'score': 18.0, 'notes': 'Clear gap'}
            },
            'manual_notes': 'Well formulated biophysical gap.',
            'action_items': ['Include positive control details.'],
            'memo_text': 'Formal Faculty Memo: Excellent proposal.'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

        draft = get_student_draft(self.test_sid)
        self.assertIn('faculty_review', draft)
        self.assertEqual(draft['faculty_review']['gpa'], 8.8)
        self.assertEqual(draft['faculty_review']['raw_total'], 75.0)
        self.assertEqual(draft['faculty_review']['standing'], '🌟 Grant-Ready')
        self.assertEqual(len(draft['faculty_review']['action_items']), 1)

    def test_student_grade_sanitization(self):
        raw_draft = {
            'student_id': self.test_sid,
            'student_name': 'Test Student',
            'faculty_review': {
                'gpa': 8.7,
                'raw_total': 74.0,
                'standing': '🌟 Grant-Ready',
                'criterion_overrides': {
                    'background': {'score': 18.5, 'notes': 'Deep literature context'},
                    'title': 2.0
                },
                'action_items': ['Clarify Aim 2 contingency plan.'],
                'memo_text': 'Great work on the proposal structure.'
            }
        }

        sanitized = sanitize_draft_for_student(raw_draft)
        rev = sanitized.get('faculty_review', {})

        self.assertNotIn('gpa', rev)
        self.assertNotIn('raw_total', rev)

        overrides = rev.get('criterion_overrides', {})
        self.assertNotIn('score', overrides.get('background', {}))
        self.assertEqual(overrides.get('background', {}).get('notes'), 'Deep literature context')

        self.assertEqual(rev.get('standing'), '🌟 Grant-Ready')
        self.assertEqual(rev.get('action_items'), ['Clarify Aim 2 contingency plan.'])
        self.assertEqual(rev.get('memo_text'), 'Great work on the proposal structure.')

    def test_student_api_endpoint_redacts_grades(self):
        dispatch_faculty_feedback(self.test_sid, {
            'gpa': 9.0,
            'raw_total': 76.5,
            'standing': '🌟 Grant-Ready',
            'action_items': ['Proceed to viva preparation.']
        })

        resp = self.client.get(f'/api/student/draft/{self.test_sid}')
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()['draft']
        rev = payload.get('faculty_review', {})
        self.assertNotIn('gpa', rev)
        self.assertNotIn('raw_total', rev)
        self.assertEqual(rev.get('standing'), '🌟 Grant-Ready')

        with self.client.session_transaction() as sess:
            sess['faculty_authenticated'] = True

        resp_fac = self.client.get(f'/api/student/draft/{self.test_sid}')
        self.assertEqual(resp_fac.status_code, 200)
        payload_fac = resp_fac.get_json()['draft']
        rev_fac = payload_fac.get('faculty_review', {})
        self.assertIn('gpa', rev_fac)
        self.assertEqual(rev_fac['gpa'], 9.0)
        self.assertIn('raw_total', rev_fac)
        self.assertEqual(rev_fac['raw_total'], 76.5)

if __name__ == '__main__':
    unittest.main()
