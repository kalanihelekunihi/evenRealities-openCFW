from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ec


SCRIPT = Path(__file__).resolve().parents[1] / "tools/sign_r1_firmware.py"
SPEC = importlib.util.spec_from_file_location("sign_r1_firmware", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
signing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(signing)


class R1FirmwareSigningTests(unittest.TestCase):
    def test_owner_signature_round_trip_and_dfu_archive(self) -> None:
        image = bytes(range(256)) * 17
        private = ec.generate_private_key(ec.SECP256R1())
        command = signing.build_application_init_command(
            image,
            application_version=3,
            hardware_version=52,
            sd_requirements=[0x0100],
            is_debug=True,
        )
        packet = signing.sign_init_command(command, private)

        self.assertEqual(signing.verify_init_packet(packet, private.public_key()), command)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "openr1-owner-signed.zip"
            signing.write_package(package, image, packet)
            with zipfile.ZipFile(package) as archive:
                self.assertEqual(
                    set(archive.namelist()),
                    {"application.bin", "application.dat", "manifest.json"},
                )
                self.assertEqual(archive.read("application.bin"), image)
                self.assertEqual(archive.read("application.dat"), packet)

    def test_tampered_init_packet_is_rejected(self) -> None:
        private = ec.generate_private_key(ec.SECP256R1())
        command = signing.build_application_init_command(
            b"firmware",
            application_version=3,
            hardware_version=52,
            sd_requirements=[0x0100],
            is_debug=True,
        )
        packet = bytearray(signing.sign_init_command(command, private))
        packet[-1] ^= 1
        with self.assertRaisesRegex(ValueError, "signature verification failed"):
            signing.verify_init_packet(bytes(packet), private.public_key())


if __name__ == "__main__":
    unittest.main()
