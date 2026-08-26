#!/usr/bin/env python3
"""Host behavior and Cortex-M55 compile tests for the common HCI core."""
from __future__ import annotations
import ctypes, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"components/shared/cordio/runtime_cordio_hci_core.c"; INC=ROOT/"components/shared/cordio"
HARNESS=r"""
#include <stdint.h>
#include <stdlib.h>
#include "runtime_cordio_hci_core.h"
static uint16_t buf_size=8, write_result=1; static unsigned frees,allocs,enqs,resets,inits,flows; static uint8_t *queued;
uint16_t hciTrSendAclData(void *c,const uint8_t*d){(void)c;(void)d;return write_result;}
uint16_t HciGetBufSize(void){return buf_size;} void hciCoreInit(void){++inits;} void hciCoreResetStart(void){++resets;}
void WsfMsgEnq(void*q,uint8_t h,void*m){(void)q;(void)h;queued=m;++enqs;} void*WsfMsgDeq(void*q,uint8_t*h){void*p=queued;(void)q;*h=0;queued=0;return p;}
void WsfMsgFree(void*m){(void)m;++frees;} void*WsfMsgDataAlloc(uint16_t n,uint8_t t){(void)t;++allocs;return calloc(1,n);}
static void flow(uint16_t h,_Bool d){(void)h;if(d)++flows;}
void test_reset(void){extern void open_cfw_hci_core_reset_for_test(void);open_cfw_hci_core_reset_for_test();frees=allocs=enqs=resets=inits=flows=0;queued=0;buf_size=8;write_result=1;open_cfw_hci_core_set_flow_callback_for_test(flow);}
void test_controller(uint16_t s,uint8_t n){open_cfw_hci_core_set_controller_for_test(s,n);} void test_write(uint16_t n){write_result=n;}
unsigned test_count(unsigned i){unsigned v[]={frees,allocs,enqs,resets,inits,flows};return i<6?v[i]:0;}
"""
class HciCoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(); d=Path(cls.tmp.name); h=d/"h.c";h.write_text(HARNESS); so=d/"x.so"
  subprocess.run(["clang","-std=c11","-Wall","-Wextra","-Werror","-shared","-fPIC","-DOPEN_CFW_HCI_CORE_TEST=1","-I",str(INC),str(SRC),str(h),"-o",str(so)],check=True)
  cls.l=ctypes.CDLL(str(so)); cls.l.hciCoreConnByHandle.restype=ctypes.c_void_p; cls.l.hciCoreCisByHandle.restype=ctypes.c_void_p; cls.l.hciCoreAclReassembly.restype=ctypes.POINTER(ctypes.c_uint8); cls.l.hciCoreAclReassembly.argtypes=[ctypes.POINTER(ctypes.c_uint8)]; cls.l.HciSendAclData.argtypes=[ctypes.POINTER(ctypes.c_uint8)]
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def setUp(self): self.l.test_reset()
 @staticmethod
 def b(x): return (ctypes.c_uint8*len(x))(*x)
 def test_init_connection_and_cis_lifecycle(self):
  self.l.HciCoreInit(); self.assertEqual(self.l.test_count(4),1)
  self.l.hciCoreConnOpen(0x1234); self.assertTrue(self.l.hciCoreConnByHandle(0x234)); self.l.hciCoreConnClose(0x234); self.assertFalse(self.l.hciCoreConnByHandle(0x234))
  self.l.hciCoreCisOpen(0x456); self.assertTrue(self.l.hciCoreCisByHandle(0x456)); self.l.hciCoreCisClose(0x456); self.assertFalse(self.l.hciCoreCisByHandle(0x456))
 def test_send_success_failure_queue_and_unknown(self):
  self.l.HciCoreInit(); self.l.test_controller(8,1); self.l.hciCoreConnOpen(1); p=self.b([1,0,3,0,1,2,3]); self.l.test_write(7); self.l.HciSendAclData(p); self.assertEqual(self.l.test_count(0),1)
  q=self.b([2,0,1,0,9]); self.l.HciSendAclData(q); self.assertEqual(self.l.test_count(0),2)
  self.l.open_cfw_hci_core_set_queue_empty_for_test(False); r=self.b([1,0,2,0,4,5]); self.l.HciSendAclData(r); self.assertEqual(self.l.test_count(2),1)
 def test_acl_reassembly_and_overlong_rejection(self):
  self.l.HciCoreInit(); self.l.HciSetMaxRxAclLen(64); self.l.hciCoreConnOpen(1)
  first=self.b([1,0x20,4,0,6,0,0x40,0]); self.assertFalse(self.l.hciCoreAclReassembly(first)); self.assertEqual(self.l.test_count(1),1)
  cont=self.b([1,0x10,6,0,1,2,3,4,5,6]); out=self.l.hciCoreAclReassembly(cont); self.assertTrue(out); self.assertEqual([out[i] for i in range(10)],[1,0,10,0,6,0,0x40,0,1,2]);
  self.l.WsfMsgFree(out)
  complete=self.b([1,0x20,5,0,1,0,0x40,0,9]); self.assertTrue(self.l.hciCoreAclReassembly(complete))
 def test_reset_setters_and_target_compile(self):
  self.l.HciSetMaxRxAclLen(1); self.l.HciSetAclQueueWatermarks(8,3); self.l.HciSetLeSupFeat(4,True); self.l.HciResetSequence(); self.assertEqual(self.l.test_count(3),1)
  with tempfile.TemporaryDirectory() as d:
   o=Path(d)/"x.o"; subprocess.run(["clang","--target=thumbv7em-none-eabi","-mcpu=cortex-m55","-mthumb","-O2","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_HCI_CORE_PRODUCTION=1","-I",str(INC),"-c",str(SRC),"-o",str(o)],check=True); s=subprocess.run(["nm","-g",str(o)],capture_output=True,text=True,check=True).stdout
   for n in ("hciCoreConnAlloc","hciCoreConnFree","hciCoreConnByHandle","hciCoreNextConnFragment","hciCoreConnOpen","hciCoreConnClose","hciCoreSendAclData","hciCoreTxReady","hciCoreTxAclStart","hciCoreTxAclContinue","hciCoreTxAclComplete","hciCoreAclReassembly","hciCoreTxAclDataFragmented","HciCoreInit","HciResetSequence","HciSetMaxRxAclLen","HciSetAclQueueWatermarks","HciSetLeSupFeat","HciSendAclData","hciCoreCisAlloc","hciCoreCisFree","hciCoreCisByHandle","hciCoreCisOpen","hciCoreCisClose"): self.assertIn(n,s)
if __name__=="__main__":unittest.main()
