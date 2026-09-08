# SPDX-License-Identifier: MIT
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SuspendTests(unittest.TestCase):
    def test_null_dispatch_context_and_ignored_callback_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / 'fixture.c'
            fixture.write_text('''#include <lvp_app.h>
LVP_APP *open_cfw_gx8002_app_core_ops;
static LVP_APP app;
static unsigned calls;
static unsigned stops;
void open_cfw_gx8002_watchdog_stop(void) { ++stops; }
unsigned get_stops(void) { return stops; }
static void *seen;
static int callback(void *context) { if (stops != 1) return -99; ++calls; seen = context; return -57; }
void setup(int mode, void *context) {
 calls = 0; stops = 0; seen = 0;
 app.AppSuspend = mode == 2 ? callback : 0;
 app.suspend_priv = context;
 open_cfw_gx8002_app_core_ops = mode ? &app : 0;
}
unsigned get_calls(void) { return calls; }
void *get_seen(void) { return seen; }
''')
            library = root / 'suspend.dylib'
            subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror',
                            '-DOPEN_CFW_GX8002_APP_HOST_TEST', '-I',
                            str(ROOT / 'build/upstream-nationalchip-lvp-kws/lvp/app_core'),
                            str(ROOT / 'components/shared/gx8002/runtime_gx8002_app_suspend.c'),
                            str(fixture), '-o', str(library)], check=True)
            lib = ctypes.CDLL(str(library))
            lib.setup.argtypes = [ctypes.c_int, ctypes.c_void_p]
            lib.open_cfw_gx8002_app_suspend.argtypes = [ctypes.c_void_p]
            lib.get_seen.restype = ctypes.c_void_p
            for mode in range(3):
                for context in (0, 0x1234, 0x20026d38):
                    lib.setup(mode, context)
                    self.assertEqual(lib.open_cfw_gx8002_app_suspend(0xdead), 0)
                    self.assertEqual(lib.get_stops(), 1)
                    self.assertEqual(lib.get_calls(), int(mode == 2))
                    self.assertEqual(lib.get_seen() or 0, context if mode == 2 else 0)


if __name__ == '__main__':
    unittest.main()
