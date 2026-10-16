#!/usr/bin/env python3
"""Bounded native/C oracle for tracepoint phone and master transports."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]; G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_send_reply_5edfd8_5ee066.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-send-reply-5edfd8-5ee066'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:]; assert hashlib.sha256(blob).hexdigest()==PINNED
OUT.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as td:
 p=Path(td); shim=p/'shim.c'; elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_encoded_buffer[768];
uint32_t audio_tracepoint_encode_response_5eded0(const uint8_t*a,uint16_t*b){(void)a;*b=0;return 0;}
uint32_t audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const uint8_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_settings_send_peer_packet(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_send_to_phone_5edfd8',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f: segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,kind,encode_ret,length,send_ret,mask,event,command):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for addr,data in segs:u.mem_write(addr,data)
  u.mem_map(0x20000000,0x100000);record=0x20073000;u.mem_write(record,bytes((command,0x47,5,0,7,0xaa)))
  names={'encode':('audio_tracepoint_encode_response_5eded0',0x5eded0),'phone':('audio_ring_pb_tx_ble_475b14',0x475b14),'master':('audio_settings_send_peer_packet',0x465480),'flags':('audio_log_flags',0x43d0ce),'extended':('audio_log_extended',0x43d574),'compact':('compressed_log_output',0x43ce9e)}
  hooks={(syms[s]&~1 if compiled else a):n for n,(s,a) in names.items()}
  calls=[]
  def word(a):return int.from_bytes(u.mem_read(a,4),'little')
  def string(a):return bytes(u.mem_read(a,256)).split(b'\0')[0].decode('ascii')
  def hook(cpu,pc,size,data):
   n=hooks.get(pc)
   if not n:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3));sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if n=='encode':
    calls.append((n,r0==record));cpu.mem_write(r1,length.to_bytes(2,'little'));cpu.reg_write(A.UC_ARM_REG_R0,encode_ret)
   elif n=='phone':
    calls.append((n,r0,r1,r2==(syms['audio_tracepoint_encoded_buffer'] if compiled else 0x2037b6c0),r3));cpu.reg_write(A.UC_ARM_REG_R0,send_ret)
   elif n=='master':
    calls.append((n,r0,r1==(syms['audio_tracepoint_encoded_buffer'] if compiled else 0x2037b6c0),r2,r3,word(sp)));cpu.reg_write(A.UC_ARM_REG_R0,send_ret)
   elif n=='flags':cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif n=='extended':
    args=tuple(word(sp+4*i) for i in range(2,6) if kind=='master') if kind=='master' else tuple(word(sp+4*i) for i in range(2,5))
    calls.append((n,r0,string(r1),string(r2),string(r3),word(sp),string(word(sp+4)),args))
   else:
    args=(word(sp),word(sp+4),word(sp+8)) if kind=='master' else (word(sp),word(sp+4))
    calls.append((n,r0,string(r1),string(r2),r3,args))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=(syms['audio_tracepoint_send_to_master_5ee066'] if kind=='master' else syms['audio_tracepoint_send_to_phone_5edfd8']) if compiled else (0x5ee066 if kind=='master' else 0x5edfd8)
  u.reg_write(A.UC_ARM_REG_R0,event if kind=='master' else record)
  if kind=='master':u.reg_write(A.UC_ARM_REG_R1,record)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.emu_start(entry|1,0x600000,count=20000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for kind in ('phone','master'):
  for encode_ret in (0,1):
   for length in (0,17,767):
    for send_ret in (0,3,0xffffffff):
     for mask in (0,1,2,4,7):
      for event,command in ((0,0),(0xc,3),(0x12345,255)):
       n=run(False,kind,encode_ret,length,send_ret,mask,event,command)
       c=run(True,kind,encode_ret,length,send_ret,mask,event,command)
       if n!=c:raise AssertionError((kind,encode_ret,length,send_ret,mask,event,command,n,c))
       cases.append((kind,encode_ret,length,send_ret,mask,event,command))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_SEND_REPLY_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Encoder and transport bodies are call-boundary stubs; final RAM placement and hardware execution unproved.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
