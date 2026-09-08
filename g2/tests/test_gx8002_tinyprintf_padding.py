# SPDX-License-Identifier: MIT
import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PaddingEquivalenceTests(unittest.TestCase):
    def test_upstream_and_patch_output_and_failure_counts(self):
        source = (ROOT / 'build/upstream-nationalchip-lvp-kws/utility/libc/tinyprintf.c').read_text()
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            original = tmp / 'original.c'
            patched = tmp / 'patched.c'
            original.write_text(source)
            patched.write_text(source)
            subprocess.run(['patch', '--batch', str(patched), str(ROOT / 'tools/upstream-patches/tinyprintf-padding-loop.patch')], check=True, capture_output=True)
            (tmp / 'stdio.h').write_text('#include <stddef.h>\n#include <stdarg.h>\ntypedef void FILE;\n#define EOF (-1)\n')
            (tmp / 'libc_port.h').write_text('int fputc(int, void *);\n')
            (tmp / 'autoconf.h').write_text('')
            libraries = []
            bridge = '''
static unsigned attempts, fail_at;
static char captured[4096];
int fputc(int c, void *stream) {
    (void)stream;
    if (attempts >= sizeof(captured)) __builtin_trap();
    captured[attempts++] = c;
    return attempts == fail_at ? -1 : c;
}
unsigned run(int width, int lz, int sign, int alt, int base, int uc, char *text, unsigned fail) {
    struct param p = {width, lz, sign, alt, base, uc, text};
    attempts = 0; fail_at = fail;
    return putchw(0, &p);
}
unsigned count(void) { return attempts; }
const char *output(void) { return captured; }
'''
            for path in (original, patched):
                path.write_text(path.read_text().split('size_t tfp_format(')[0] + bridge)
                library = path.with_suffix('.dylib')
                subprocess.run(['clang', '-shared', '-fPIC', '-O2', '-fno-builtin', '-I', str(tmp), str(path), '-o', str(library)], check=True)
                lib = ctypes.CDLL(str(library))
                lib.run.argtypes = [ctypes.c_int] * 6 + [ctypes.c_char_p, ctypes.c_uint]
                lib.run.restype = ctypes.c_uint
                lib.count.restype = ctypes.c_uint
                lib.output.restype = ctypes.c_void_p
                libraries.append(lib)
            for width in (-3, 0, 1, 2, 8, 32):
                for lz in (0, 1):
                    for sign in (0, 45, 43):
                        for alt in (0, 1):
                            for base in (8, 10, 16):
                                for uc in (0, 1):
                                    for text in (b'', b'0', b'123', b'abcdef'):
                                        for fail in (0, 1, 3, 9):
                                            results = []
                                            for lib in libraries:
                                                result = lib.run(width, lz, sign, alt, base, uc, text, fail)
                                                results.append((result, ctypes.string_at(lib.output(), lib.count())))
                                            self.assertEqual(*results)


if __name__ == '__main__':
    unittest.main()
