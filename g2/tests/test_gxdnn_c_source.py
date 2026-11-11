"""Compare the C-generated KWS build artifact with the authenticated stream."""
import hashlib
import shutil
import sys
import unittest
from pathlib import Path

from tests.official_payloads import require as require_official

require_official('firmware_codec.bin')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_kws_command_stream import build_stream  # noqa: E402
from gxdnn_command_emitter import decode_program  # noqa: E402
from open_cfw import wrap_codec_binh_a  # noqa: E402


class KwsCSourceOracleTests(unittest.TestCase):
    def test_c_generated_stream_matches_locked_records(self):
        compiler = shutil.which('clang')
        if compiler is None:
            self.skipTest('host clang is unavailable')
        stock = (ROOT / 'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         'b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0')
        command_stream = stock[0x18d90:0x1b15c]
        self.assertEqual(hashlib.sha256(command_stream).hexdigest(),
                         'c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9')
        generated = build_stream(compiler)
        self.assertEqual(len(decode_program(generated)), 212)
        self.assertEqual(generated, command_stream)
        image_a = stock[0x958C:0x958C + 0x2F3B0]
        self.assertEqual(wrap_codec_binh_a(
            image_a[24:0x3000 - 4], image_a[0x3004:0xBE88],
            image_a[0xBE88:0xF804], generated, image_a[0x11BD0:]), image_a)


if __name__ == '__main__':
    unittest.main()
