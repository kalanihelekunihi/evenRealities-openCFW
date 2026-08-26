#!/usr/bin/env python3
"""Host behavior and Cortex-M55 compile tests for the G2 HCI reset sequence."""
from __future__ import annotations
import ctypes, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"components/shared/cordio/runtime_cordio_hci_vs.c"; INC=ROOT/"components/shared/cordio"
HARNESS=r"""
#include <stdint.h>
#include <string.h>
#include "runtime_cordio_hci_vs.h"
static uint16_t logv[128]; static unsigned logn,reset_callbacks,extended_callbacks; static uint16_t last_extended,last_a,last_b;
static void add(uint16_t v){if(logn<128)logv[logn++]=v;}
enum{RL=1,MAX=2,RAND=3,RESET=4,BDUP=5,NVDS=6,RF=7,EM=8,LEM=9,EM2=10,BD=11,LBUF=12,STATES=13,WL=14,LFEAT=15,WDEF=16};
void HciLeReadResolvingListSize(void){add(RL);} void HciLeReadMaxDataLen(void){add(MAX);} void HciLeRandCmd(void){add(RAND);}
void HciResetCmd(void){add(RESET);} void HciVscUpdateBDAddress(void){add(BDUP);} void HciVscUpdateNvdsParam(void){add(NVDS);}
void HciVscSetRfPowerLevelEx(uint8_t n){add(RF);last_a=n;} void HciSetEventMaskCmd(const uint8_t*p){(void)p;add(EM);}
void HciLeSetEventMaskCmd(const uint8_t*p){(void)p;add(LEM);} void HciSetEventMaskPage2Cmd(const uint8_t*p){(void)p;add(EM2);}
void HciReadBdAddrCmd(void){add(BD);} void HciLeReadBufSizeCmd(void){add(LBUF);} void HciLeReadSupStatesCmd(void){add(STATES);}
void HciLeReadWhiteListSizeCmd(void){add(WL);} void HciLeReadLocalSupFeatCmd(void){add(LFEAT);}
void HciLeWriteDefDataLen(uint16_t a,uint16_t b){add(WDEF);last_a=a;last_b=b;}
static void reset_cb(void*p){uint8_t*b=p;++reset_callbacks;last_a=b[0];}
static void ext_cb(const uint8_t*p,uint16_t op){(void)p;++extended_callbacks;last_extended=op;}
void test_reset(void){open_cfw_hci_vs_reset_for_test();logn=reset_callbacks=extended_callbacks=0;last_extended=last_a=last_b=0;open_cfw_hci_vs_set_callbacks_for_test(reset_cb,ext_cb);}
void test_features(uint64_t c,uint64_t r){open_cfw_hci_vs_set_features_for_test(c,r);} uint16_t test_log(unsigned i){return i<logn?logv[i]:0;} unsigned test_logn(void){return logn;}
uint8_t test_core(unsigned i){return open_cfw_hci_vs_core_for_test()[i];} uint8_t test_hci(unsigned i){return open_cfw_hci_vs_hci_cb_for_test()[i];}
unsigned test_reset_callbacks(void){return reset_callbacks;} unsigned test_extended_callbacks(void){return extended_callbacks;} uint16_t test_extended(void){return last_extended;} uint16_t test_a(void){return last_a;} uint16_t test_b(void){return last_b;}
void test_no_extended(void){open_cfw_hci_vs_set_callbacks_for_test(reset_cb,0);}
void test_event(uint16_t opcode,const uint8_t*p,uint8_t n){uint8_t m[40]={0x0e,0,1,0,0,0};m[3]=(uint8_t)opcode;m[4]=(uint8_t)(opcode>>8);if(n>34)n=34;if(p)memcpy(m+6,p,n);hciCoreResetSequence(m);}
"""

class HciVsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(); d=Path(cls.tmp.name); h=d/"h.c"; h.write_text(HARNESS); so=d/"x.so"
  subprocess.run(["clang","-std=c11","-Wall","-Wextra","-Werror","-shared","-fPIC","-DOPEN_CFW_HCI_VS_TEST=1","-I",str(INC),str(SRC),str(h),"-o",str(so)],check=True)
  cls.l=ctypes.CDLL(str(so)); cls.l.test_features.argtypes=[ctypes.c_uint64,ctypes.c_uint64]; cls.l.test_event.argtypes=[ctypes.c_uint16,ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint8]
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def setUp(self): self.l.test_reset()
 @staticmethod
 def p(values): return (ctypes.c_uint8*len(values))(*values)
 def event(self,opcode,values=()):
  p=self.p(values) if values else None; self.l.test_event(opcode,p,len(values))
 def log(self): return [self.l.test_log(i) for i in range(self.l.test_logn())]
 def test_feature_gates_and_reset_start(self):
  self.l.test_features(0,0); self.l.hciCoreReadResolvingListSize(); self.assertEqual(self.log(),[3]); self.assertEqual(self.l.test_core(0x91),0)
  self.l.test_reset(); self.l.test_features(1<<6,1<<6); self.l.hciCoreReadResolvingListSize(); self.assertEqual(self.log(),[1])
  self.l.test_reset(); self.l.test_features(1<<5,1<<5); self.l.hciCoreReadMaxDataLen(); self.assertEqual(self.log(),[2])
  self.l.test_reset(); self.l.hciCoreResetStart(); self.assertEqual(self.log(),[4,5])
 def test_product_reset_command_chain(self):
  self.event(0x0c03); self.assertEqual(self.log(),[6])
  self.event(0xfff2); self.assertEqual(self.log(),[6,7]); self.assertEqual(self.l.test_a(),6)
  self.event(0xfcc4); self.event(0x0c01); self.event(0x2001); self.event(0x0c63); self.event(0x1009,[1,2,3,4,5,6])
  self.assertEqual(self.log(),[6,7,8,9,10,11,12]); self.assertEqual([self.l.test_core(0x68+i) for i in range(6)],[1,2,3,4,5,6])
 def test_capabilities_random_completion_and_extension(self):
  self.event(0x2002,[0x34,0x12,7]); self.assertEqual(self.log(),[13]); self.assertEqual((self.l.test_core(0x7e),self.l.test_core(0x7f),self.l.test_core(0x82),self.l.test_core(0x83)),(0x34,0x12,7,7))
  self.event(0x201c,range(8)); self.event(0x200f,[9]); self.assertEqual(self.log(),[13,14,15])
  self.event(0x202f,[0x11,0x22,0x33,0x44]); self.assertEqual((self.l.test_a(),self.l.test_b()),(0x2211,0x4433))
  self.event(0x203a,[1]); self.assertEqual((self.l.test_extended_callbacks(),self.l.test_extended()),(1,0x203a))
  self.l.test_no_extended(); self.event(0x2024,[1,2,3,4]); self.assertEqual(self.log()[-1],3)
  for _ in range(4): self.event(0x2018,[0]*8)
  self.assertEqual(self.l.test_reset_callbacks(),1); self.assertEqual(self.l.test_hci(0x21),0)
 def test_noop_hooks_and_target_compile(self):
  self.assertEqual(self.l.hciCoreVsCmdCmplRcvd(1,None,0),0); self.assertEqual(self.l.hciCoreVsEvtRcvd(None,0),0); self.assertEqual(self.l.hciCoreHwErrorRcvd(None),0); self.l.HciVsInit(1)
  with tempfile.TemporaryDirectory() as d:
   o=Path(d)/"x.o"; subprocess.run(["clang","--target=thumbv7em-none-eabi","-mcpu=cortex-m55","-mthumb","-O2","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_HCI_VS_PRODUCTION=1","-I",str(INC),"-c",str(SRC),"-o",str(o)],check=True); s=subprocess.run(["nm","-g",str(o)],capture_output=True,text=True,check=True).stdout
   for n in ("hciCoreReadResolvingListSize","hciCoreReadMaxDataLen","hciCoreResetStart","hciCoreResetSequence","hciCoreVsCmdCmplRcvd","hciCoreVsEvtRcvd","hciCoreHwErrorRcvd","HciVsInit"): self.assertIn(n,s)

if __name__=="__main__": unittest.main()
