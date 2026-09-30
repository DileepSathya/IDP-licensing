import tempfile
import unittest
from pathlib import Path
import sys
import types
from unittest.mock import patch

sys.modules.setdefault("psycopg2", types.SimpleNamespace(connect=lambda **_kwargs: None))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *_args, **_kwargs: None))

from database import license_service
from keygen import license_generator


VALID_UPPER = "A" * 64
VALID_LOWER = "a" * 64


class LicenseIssuanceTests(unittest.TestCase):
    def test_normalizes_valid_sha256_fingerprint(self):
        self.assertEqual(license_generator.normalize_fingerprint(VALID_UPPER), VALID_LOWER)

    def test_rejects_malformed_fingerprint_before_loading_private_key(self):
        malformed = ("", "a" * 63, "a" * 65, "a" * 63 + "g", "aa aa" + "a" * 59)
        for value in malformed:
            with self.subTest(value=value), patch.object(
                license_generator, "_load_private_key"
            ) as load_key:
                with tempfile.TemporaryDirectory() as folder:
                    output = Path(folder) / "license.lic"
                    with self.assertRaises(ValueError):
                        license_generator.generate_license_file(
                            customer_id="42",
                            fingerprint=value,
                            plan="monthly",
                            expires_at="2026-12-31",
                            output=str(output),
                        )
                    self.assertFalse(output.exists())
                load_key.assert_not_called()

    def test_service_rejects_bad_fingerprint_before_creating_output_directory(self):
        with patch.object(license_service, "_build_output_path") as build_path:
            with self.assertRaises(ValueError):
                license_service.create_user_license(
                    user_id=42,
                    email="customer@example.com",
                    fingerprint_id="legacy-fingerprint",
                    plan="monthly",
                )
            build_path.assert_not_called()


if __name__ == "__main__":
    unittest.main()
