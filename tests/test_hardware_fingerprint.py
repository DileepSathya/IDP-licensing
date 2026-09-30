import json
import unittest

from licensing import hardware_fingerprint as fingerprint


class HardwareFingerprintTests(unittest.TestCase):
    def test_normalizes_and_hashes_only_cpu_and_disk(self):
        self.assertEqual(
            fingerprint.fingerprint_from_parts(" ab c123 ", " disk 987\n"),
            "8aea289b7577613b5804540488393070caf4ba16dc1331e2d449fe19ce517970",
        )

    def test_rejects_missing_or_placeholder_identifiers(self):
        for value in ("", "unknown", "Default String", "0" * 16):
            with self.subTest(value=value):
                with self.assertRaises(fingerprint.HardwareIdentityError):
                    fingerprint.normalize_hardware_id(value, "hardware identifier")

    def test_collects_cpu_and_system_disk_from_json(self):
        parts = fingerprint.collect_hardware_parts(
            runner=lambda _script: json.dumps({"cpuId": "CPU-1", "diskSerial": "DISK-1"})
        )
        self.assertEqual(parts, {"cpu": "CPU-1", "disk": "DISK-1"})
        self.assertNotIn("mac", parts)


if __name__ == "__main__":
    unittest.main()
