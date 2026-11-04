"""
Test suite for Study Material Upload & Document Vault API.
"""

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException, UploadFile

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from api import upload_study_material, get_documents, remove_document
from db import init_db


class TestUploadAPI(unittest.TestCase):

    def setUp(self):
        init_db()
        self.patcher = patch("api._index_uploaded_pdf_task")
        self.mock_index_task = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_reject_non_pdf_extension(self):
        """Verify upload endpoint rejects .docx or .txt files."""
        f_bad = UploadFile(filename="notes.docx", file=io.BytesIO(b"PK\x03\x04 fake docx"))
        with self.assertRaises(HTTPException) as ctx:
            upload_study_material(
                file=f_bad,
                scheme="2022 Scheme",
                subject_code="BCS502",
                sem="Sem 5",
                material_type="Question Paper",
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Only PDF files", ctx.exception.detail)

    def test_reject_invalid_pdf_header(self):
        """Verify upload endpoint rejects files with .pdf extension but invalid header."""
        f_bad_hdr = UploadFile(filename="fake.pdf", file=io.BytesIO(b"This is plain text not pdf"))
        with self.assertRaises(HTTPException) as ctx:
            upload_study_material(
                file=f_bad_hdr,
                scheme="2022 Scheme",
                subject_code="BCS502",
                sem="Sem 5",
                material_type="Study Material",
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Header missing %PDF-", ctx.exception.detail)

    def test_upload_valid_pdf_and_list_and_delete(self):
        """Verify successful upload of valid PDF, retrieval in document list, and deletion."""
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\ntrailer\n<<\n>>\n%%EOF"
        f_valid = UploadFile(filename="BCS502_QP_2024.pdf", file=io.BytesIO(pdf_bytes))
        data = upload_study_material(
            file=f_valid,
            scheme="2022 Scheme",
            subject_code="BCS502",
            sem="Sem 5",
            material_type="Question Paper",
            title="BCS502 Jan 2024 Exam Paper",
        )
        self.assertEqual(data["status"], "ok")
        doc = data["document"]
        self.assertEqual(doc["subject_code"], "BCS502")
        self.assertEqual(doc["scheme"], "2022 Scheme")
        self.assertEqual(doc["sem"], "Sem 5")
        self.assertEqual(doc["material_type"], "Question Paper")

        doc_id = doc["id"]

        # Verify listing
        list_res = get_documents(subject_code="BCS502")
        matching = [d for d in list_res["documents"] if d["id"] == doc_id]
        self.assertEqual(len(matching), 1)

        # Verify deletion
        del_res = remove_document(doc_id)
        self.assertEqual(del_res["status"], "ok")

        # Confirm deleted
        list_res2 = get_documents(subject_code="BCS502")
        matching2 = [d for d in list_res2["documents"] if d["id"] == doc_id]
        self.assertEqual(len(matching2), 0)


if __name__ == "__main__":
    unittest.main()
