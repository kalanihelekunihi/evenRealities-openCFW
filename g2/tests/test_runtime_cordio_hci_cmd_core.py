#!/usr/bin/env python3
"""Host and target tests for the HCI command queue/timeout/reset core."""
from __future__ import annotations
import ctypes, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"components/shared/cordio/runtime_cordio_hci_cmd.c"; INC=ROOT/"components/shared/cordio"
HARNESS=r"""
#include <stdint.h>
#include <stdlib.h>
#include "runtime_cordio_hci_cmd.h"
typedef struct node{struct node*n;void*p;uint8_t h;}node_t;static node_t*head,*tail;static unsigned allocs,frees,enqs,starts,stops,writes,shutdowns,boots,resets,callbacks;static uint16_t write_result=1,last_opcode;static uint8_t callback_event,last_command[258],last_command_len;
void*WsfMsgAlloc(uint16_t n){++allocs;return calloc(1,n);}void WsfMsgFree(void*p){++frees;free(p);}void WsfMsgEnq(void*q,uint8_t h,void*p){node_t*n=calloc(1,sizeof(*n));(void)q;n->p=p;n->h=h;if(tail)tail->n=n;else head=n;tail=n;++enqs;}
void*WsfMsgPeek(void*q,uint8_t*h){(void)q;if(!head)return 0;*h=head->h;return head->p;}void*WsfMsgDeq(void*q,uint8_t*h){node_t*n=head;void*p;(void)q;if(!n)return 0;*h=n->h;p=n->p;head=n->n;if(!head)tail=0;free(n);return p;}
void WsfTimerStartSec(void*t,uint32_t s){(void)t;if(s==10)++starts;}void WsfTimerStop(void*t){(void)t;++stops;}uint16_t hciTrSendCmd(const uint8_t*p){unsigned i;++writes;last_opcode=(uint16_t)(p[0]|p[1]<<8);last_command_len=(uint8_t)(p[2]+3u);for(i=0;i<last_command_len;++i)last_command[i]=p[i];return write_result;}
void HciDrvShutdown(void){++shutdowns;}void HciDrvRadioBoot(uint8_t c){if(c==0)++boots;}void DmDevReset(void){++resets;}static void cb(void*p){++callbacks;callback_event=((uint8_t*)p)[2];}
void test_reset(void){uint8_t h;void*p;unsigned i;while((p=WsfMsgDeq(0,&h)))free(p);open_cfw_hci_cmd_reset_for_test();allocs=frees=enqs=starts=stops=writes=shutdowns=boots=resets=callbacks=0;write_result=1;last_opcode=callback_event=last_command_len=0;for(i=0;i<sizeof(last_command);++i)last_command[i]=0;open_cfw_hci_cmd_set_callback_for_test(cb);}
void test_write(uint16_t r){write_result=r;}unsigned test_count(unsigned i){unsigned v[]={allocs,frees,enqs,starts,stops,writes,shutdowns,boots,resets,callbacks};return i<10?v[i]:0;}uint16_t test_opcode(void){return last_opcode;}uint8_t test_event(void){return callback_event;}uint8_t test_state(unsigned i){return open_cfw_hci_cmd_state_for_test()[i];}uint8_t test_command_len(void){return last_command_len;}uint8_t test_command_byte(unsigned i){return i<sizeof(last_command)?last_command[i]:0;}
"""
class HciCmdCoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();d=Path(cls.tmp.name);h=d/"h.c";h.write_text(HARNESS);so=d/"x.so";subprocess.run(["clang","-std=c11","-Wall","-Wextra","-Werror","-shared","-fPIC","-DOPEN_CFW_HCI_CMD_TEST=1","-I",str(INC),str(SRC),str(h),"-o",str(so)],check=True);cls.l=ctypes.CDLL(str(so));p=ctypes.POINTER(ctypes.c_uint8);cls.l.hciCmdAlloc.restype=p;cls.l.hciCmdAlloc.argtypes=[ctypes.c_uint16,ctypes.c_uint16];cls.l.hciCmdSend.argtypes=[p];cls.l.hciCmdSend.restype=ctypes.c_bool;cls.l.HciDisconnectCmd.argtypes=[ctypes.c_uint16,ctypes.c_uint8];cls.l.HciLeSetAdvDataCmd.argtypes=[ctypes.c_uint8,p];cls.l.HciLeSetScanRespDataCmd.argtypes=[ctypes.c_uint8,p];cls.l.HciSetEventMaskCmd.argtypes=[p];cls.l.HciLeStartEncryptionCmd.argtypes=[ctypes.c_uint16,p,ctypes.c_uint16,p];cls.l.HciLeGenerateDHKey.argtypes=[p,p];cls.l.HciLeSetHostFeatureCmd.argtypes=[ctypes.c_uint8,ctypes.c_bool]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):self.l.test_reset();self.l.hciCmdInit()
 def command(self):return bytes(self.l.test_command_byte(i) for i in range(self.l.test_command_len()))
 def complete(self):self.l.hciCmdRecvCmpl(1)
 def test_alloc_send_and_completion_ownership(self):
  p=self.l.hciCmdAlloc(0x1234,2);self.assertEqual([p[i] for i in range(3)],[0x34,0x12,2]);self.assertTrue(self.l.hciCmdSend(p));self.assertEqual((self.l.test_count(0),self.l.test_count(1),self.l.test_count(2),self.l.test_count(3),self.l.test_count(5)),(1,1,1,1,1));self.assertEqual(self.l.test_opcode(),0x1234);self.assertEqual(self.l.test_state(0x1a),0)
  q=self.l.hciCmdAlloc(0x5678,0);self.assertFalse(self.l.hciCmdSend(q));self.l.hciCmdRecvCmpl(7);self.assertEqual(self.l.test_opcode(),0x5678);self.assertEqual(self.l.test_count(4),1)
 def test_transport_failure_preserves_queue(self):
  self.l.test_write(0);p=self.l.hciCmdAlloc(0xabcd,0);self.assertFalse(self.l.hciCmdSend(p));self.assertEqual(self.l.test_count(1),0);self.l.test_write(1);self.l.hciCmdRecvCmpl(1);self.assertEqual((self.l.test_count(1),self.l.test_opcode()),(1,0xabcd))
 def test_timeout_clear_and_reset(self):
  p=self.l.hciCmdAlloc(1,0);self.l.test_write(0);self.l.hciCmdSend(p);self.l.hciCmdTimeout(None);self.assertEqual([self.l.test_count(i) for i in (6,7,8)],[1,1,1]);self.l.HciResetCmd();self.assertEqual((self.l.test_count(9),self.l.test_event(),self.l.test_opcode()),(1,0x14,0x0c03))
 def test_bounds_and_target_compile(self):
  self.assertFalse(self.l.hciCmdAlloc(1,256))
  with tempfile.TemporaryDirectory() as d:
   o=Path(d)/"x.o";subprocess.run(["clang","--target=thumbv7em-none-eabi","-mcpu=cortex-m55","-mthumb","-O2","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_HCI_CMD_PRODUCTION=1","-I",str(INC),"-c",str(SRC),"-o",str(o)],check=True);s=subprocess.run(["nm","-g",str(o)],capture_output=True,text=True,check=True).stdout
   expected={line.split("\t")[1] for line in (ROOT/"tools/manifests/ambiq-cordio-hci-cmd-function-map.tsv").read_text().splitlines()[1:]};self.assertEqual({line.split()[-1] for line in s.splitlines() if len(line.split())==3 and line.split()[1]=="T"},expected)
 def test_standard_encoder_payloads(self):
  self.l.HciDisconnectCmd(0x1234,0x13);self.assertEqual(self.command(),bytes([0x06,0x04,3,0x34,0x12,0x13]));self.complete()
  data=(ctypes.c_uint8*3)(0xaa,0xbb,0xcc);self.l.HciLeSetAdvDataCmd(3,data);self.assertEqual(self.command()[:7],bytes([0x08,0x20,32,3,0xaa,0xbb,0xcc]));self.assertEqual(self.command()[7:],bytes(28));self.complete()
  mask=(ctypes.c_uint8*8)(*range(8));self.l.HciSetEventMaskCmd(mask);self.assertEqual(self.command(),bytes([0x01,0x0c,8,*range(8)]));self.complete()
  key=(ctypes.c_uint8*16)(*range(16));rnd=(ctypes.c_uint8*8)(*range(8));self.l.HciLeStartEncryptionCmd(0x2211,rnd,0x4433,key);self.assertEqual(self.command(),bytes([0x19,0x20,28,0x11,0x22,*range(8),0x33,0x44,*range(16)]));self.complete()
  self.l.HciLeSetHostFeatureCmd(7,True);self.assertEqual(self.command(),bytes([0x74,0x20,2,7,1]))
 def test_no_parameter_encoder_inventory(self):
  cases=(("HciLeClearWhiteListCmd",0x2010),("HciLeCreateConnCancelCmd",0x200e),("HciLeReadDefDataLen",0x2023),("HciLeReadLocalP256PubKey",0x2025),("HciLeReadMaxDataLen",0x202f),("HciLeRandCmd",0x2018),("HciLeReadAdvTXPowerCmd",0x2007),("HciLeReadBufSizeCmd",0x2002),("HciLeReadLocalSupFeatCmd",0x2003),("HciLeReadSupStatesCmd",0x201c),("HciLeReadWhiteListSizeCmd",0x200f),("HciReadBdAddrCmd",0x1009),("HciReadBufSizeCmd",0x1005),("HciReadLocalSupFeatCmd",0x1003),("HciReadLocalVerInfoCmd",0x1001),("HciLeClearResolvingList",0x2029),("HciLeReadResolvingListSize",0x202a),("HciLeTestEndCmd",0x201f),("HciLeReadBufSizeCmdV2",0x2060))
  for name,opcode in cases:
   getattr(self.l,name)();self.assertEqual(self.command(),bytes([opcode&255,opcode>>8,0]),name);self.complete()
 def test_bounds_and_null_encoders_fail_closed(self):
  before=self.l.test_count(0);data=(ctypes.c_uint8*32)(*range(32));self.l.HciLeSetAdvDataCmd(32,data);self.l.HciLeSetScanRespDataCmd(1,None);self.l.HciLeGenerateDHKey(None,None);self.assertEqual(self.l.test_count(0),before)
if __name__=="__main__":unittest.main()
