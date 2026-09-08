# SPDX-License-Identifier: MIT
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class UartTickTests(unittest.TestCase):
    def test_crc_gate_and_first_matching_registration(self):
        sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'lvp_attr.h').write_text('#define DRAM0_STAGE2_SRAM_ATTR\n')
            fixture=p/'fixture.c';fixture.write_text('''#include <stdint.h>
#include <string.h>
#include <uart_message_v2.h>
#include <lvp_queue.h>
LVP_QUEUE open_cfw_gx8002_uart_receive_queue;
UART_MSG_REGIST open_cfw_gx8002_uart_registrations[16];
static unsigned char storage[sizeof(MSG_PACK)*3];
static int crc_calls, logs, calls, matched;
uint32_t open_cfw_gx8002_crc32(uint32_t initial,const unsigned char *data,unsigned int len) {
 ++crc_calls; return initial==0 && data==storage && len==5 ? 0x1234 : 0;
}
int open_cfw_gx8002_printf(const char *format,...) { (void)format; ++logs; return 0; }
static int callback(MSG_PACK *packet,void *priv) { ++calls; matched=(int)(uintptr_t)priv; return packet->port+100; }
void setup(int queued,int flags,int valid,int registration) {
 crc_calls=logs=calls=matched=0;
 memset(open_cfw_gx8002_uart_registrations,0,sizeof(open_cfw_gx8002_uart_registrations));
 LvpQueueInit(&open_cfw_gx8002_uart_receive_queue,storage,sizeof(storage),sizeof(MSG_PACK));
 if(registration) {
  for(int i=2;i<4;++i) {
   UART_MSG_REGIST *r=&open_cfw_gx8002_uart_registrations[i];
   r->port=7; r->msg_id=0x102; r->priv=(void*)(uintptr_t)i; r->msg_pack_callback=callback;
  }
 }
 if(queued) {
  MSG_PACK packet={0}; packet.msg_header.flags=flags; packet.msg_header.cmd=0x102;
  packet.port=7; packet.len=5; packet.body_addr=storage; packet.body_vef=valid?0x1234:0x5678;
  LvpQueuePut(&open_cfw_gx8002_uart_receive_queue,(const unsigned char*)&packet);
 }
}
int counts(void) { return crc_calls*1000+logs*100+calls*10+matched; }
''')
            libpath=p/'uart.dylib'
            subprocess.run(['cc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
                            '-DOPEN_CFW_GX8002_UART_HOST_TEST','-I',str(p),'-I',str(sdk/'lvp/common'),
                            str(sdk/'lvp/common/lvp_queue.c'),str(fixture),
                            str(ROOT/'components/shared/gx8002/runtime_gx8002_uart_async_tick.c'),'-o',str(libpath)],check=True)
            lib=ctypes.CDLL(str(libpath));lib.setup.argtypes=[ctypes.c_int]*4
            for queued in (0,1):
                for flags in (0,1,2,255):
                    for valid in (0,1):
                        for registration in (0,1):
                            lib.setup(queued,flags,valid,registration)
                            crc=bool(queued and flags==1);bad=crc and not valid
                            dispatch=bool(queued and not bad and registration)
                            self.assertEqual(lib.open_cfw_gx8002_uart_async_tick(),107 if dispatch else -1)
                            self.assertEqual(lib.counts(),1000*crc+100*bad+12*dispatch)

if __name__=='__main__':unittest.main()
