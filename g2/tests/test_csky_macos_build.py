# SPDX-License-Identifier: MIT
"""Check the pinned macOS compiler backport admission boundary."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('csky_build', ROOT / 'tools/build_g2_csky_macos.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class MacOSBuildTests(unittest.TestCase):
    def test_modified_header_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            header = source / 'gcc/gcc/system.h'
            header.parent.mkdir(parents=True)
            header.write_text('unreviewed local compiler change\n')
            with patch.object(build.subprocess, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'differs from the pinned'):
                    build.apply_macos_fix(source)
                run.assert_not_called()
            self.assertEqual(header.read_text(), 'unreviewed local compiler change\n')

    def test_modified_patch_is_rejected_before_header_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / 'tools/toolchain-patches/gcc-safe-ctype.patch'
            artifact.parent.mkdir(parents=True)
            artifact.write_text('modified patch\n')
            with patch.object(build, 'ROOT', root):
                with self.assertRaisesRegex(RuntimeError, 'patch changed'):
                    build.apply_macos_fix(root / 'absent-source')

    def test_build_stays_freestanding_and_uses_host_zlib(self):
        for component in ('gcc', 'binutils'):
            args = build.configure_arguments(Path('/src'), Path('/out'), component)
            self.assertIn('--with-system-zlib', args)
            self.assertIn('--target=csky-unknown-elf', args)
            self.assertIn('--prefix=/out/install', args)
        self.assertIn('--without-headers', build.configure_arguments(Path('/src'), Path('/out'), 'gcc'))


if __name__ == '__main__':
    unittest.main()
