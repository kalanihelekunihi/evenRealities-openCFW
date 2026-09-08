# SPDX-License-Identifier: MIT
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class TriggerTests(unittest.TestCase):
    def test_full_queue_failure_is_not_propagated(self):
        sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            (out/'lvp_attr.h').write_text('#define DRAM0_STAGE2_SRAM_ATTR\n')
            fixture=out/'fixture.c'
            fixture.write_text('''#include <lvp_queue.h>
LVP_QUEUE open_cfw_gx8002_app_event_queue;
static unsigned char storage[64];
void setup(void) { LvpQueueInit(&open_cfw_gx8002_app_event_queue, storage, 64, 8); }
int read_event(void *event) { return LvpQueueGet(&open_cfw_gx8002_app_event_queue, event); }
''')
            library=out/'trigger.dylib'
            subprocess.run(['cc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
                            '-I',str(out),'-I',str(sdk/'lvp/common'),'-I',str(sdk/'lvp/app_core'),
                            str(sdk/'lvp/common/lvp_queue.c'),
                            str(ROOT/'components/shared/gx8002/runtime_gx8002_trigger_app_event.c'),
                            str(fixture),'-o',str(library)],check=True)
            lib=ctypes.CDLL(str(library));lib.setup()
            lib.LvpTriggerAppEvent.argtypes=[ctypes.c_void_p]
            lib.read_event.argtypes=[ctypes.c_void_p]
            for cycle in range(64):
                for i in range(8):
                    event=(ctypes.c_uint32*2)(cycle*8+i,0xa000+i)
                    original=bytes(event)
                    self.assertEqual(lib.LvpTriggerAppEvent(event),0)
                    self.assertEqual(bytes(event),original)
                for i in range(7):
                    event=(ctypes.c_uint32*2)()
                    self.assertEqual(lib.read_event(event),1)
                    self.assertEqual(list(event),[cycle*8+i,0xa000+i])
                self.assertEqual(lib.read_event(event),0)

if __name__=='__main__':unittest.main()
