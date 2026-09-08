# SPDX-License-Identifier: MIT
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class TickTests(unittest.TestCase):
    def test_callback_replacement_and_service_order(self):
        sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'lvp_attr.h').write_text('#define DRAM0_STAGE2_SRAM_ATTR\n')
            fixture=path/'fixture.c'
            fixture.write_text('''#include <lvp_app.h>
#include <lvp_queue.h>
LVP_APP *open_cfw_gx8002_app_core_ops;
LVP_QUEUE open_cfw_gx8002_app_event_queue;
static LVP_APP first, second;
static unsigned char storage[64];
static int mode, trace, seen;
static int old_loop(void) { trace=trace*10+2; return -2; }
static int new_loop(void) { trace=trace*10+3; return -3; }
static int event(APP_EVENT *e) {
 trace=trace*10+1; seen=e->event_id;
 if(mode==1) open_cfw_gx8002_app_core_ops=&second;
 if(mode==2) open_cfw_gx8002_app_core_ops=0;
 return -1;
}
int open_cfw_gx8002_uart_async_tick(void) { trace=trace*10+4; return -1; }
void open_cfw_gx8002_watchdog_ping(void) { trace=trace*10+5; }
void setup(int m, int queued) {
 mode=m; trace=seen=0;
 first.AppEventResponse=event; first.AppTaskLoop=old_loop;
 second.AppTaskLoop=new_loop;
 open_cfw_gx8002_app_core_ops=m==3?0:&first;
 LvpQueueInit(&open_cfw_gx8002_app_event_queue,storage,64,8);
 if(queued) { APP_EVENT e={71,9}; LvpQueuePut(&open_cfw_gx8002_app_event_queue,(const unsigned char*)&e); }
}
int get_trace(void) { return trace; }
int get_seen(void) { return seen; }
''')
            libpath=path/'tick.dylib'
            subprocess.run(['cc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror','-I',str(path),
                            '-I',str(sdk/'lvp/app_core'),'-I',str(sdk/'lvp/common'),
                            str(sdk/'lvp/common/lvp_queue.c'),str(fixture),
                            str(ROOT/'components/shared/gx8002/runtime_gx8002_app_tick.c'),'-o',str(libpath)],check=True)
            lib=ctypes.CDLL(str(libpath));lib.setup.argtypes=[ctypes.c_int,ctypes.c_int]
            for mode in range(4):
                for queued in range(2):
                    lib.setup(mode,queued)
                    self.assertEqual(lib.LvpAppEventTick(),0)
                    expected=45 if mode==3 else 245 if not queued else (1245,1345,145)[mode]
                    self.assertEqual(lib.get_trace(),expected)
                    self.assertEqual(lib.get_seen(),71 if queued and mode!=3 else 0)

if __name__=='__main__':unittest.main()
