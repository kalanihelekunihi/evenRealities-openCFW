#!/usr/bin/env python3
"""Compare stock tracepoint prefix/sequence dispatch to C at provider calls."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_resolve_file_path_5eddf6.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-resolve-file-path-5eddf6';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t g2_log_candidate_module_length(const char*a){(void)a;return 8;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_tracepoint_parse_sequence_5edaf0(const char*a,uint32_t*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_resolve_file_path_5eddf6',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,present,cmp_ret,parse_ret,path_text):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);path=0x20073000 if present else 0;seq=0x20073100
  if path:u.mem_write(path,path_text.encode()+b'\0')
  u.mem_write(seq,b'\x55'*4)
  hooks={(syms[k]&~1 if compiled else n):kind for kind,k,n in [('length','g2_log_candidate_module_length',0x44a43c),('compare','audio_ble_hci_vendor_compare_44b610',0x44b610),('parse','audio_tracepoint_parse_sequence_5edaf0',0x5edaf0)]};calls=[]
  def string(a):return bytes(u.mem_read(a,100)).split(b'\0')[0].decode('ascii')
  def hook(cpu,pc,size,data):
   kind=hooks.get(pc)
   if not kind:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   if kind=='length':calls.append(('length',string(r0)));cpu.reg_write(A.UC_ARM_REG_R0,8)
   elif kind=='compare':calls.append(('compare',r0==path,string(r1),r2));cpu.reg_write(A.UC_ARM_REG_R0,cmp_ret)
   else:calls.append(('parse',r0==path+8,string(r0),r1==seq));cpu.reg_write(A.UC_ARM_REG_R0,parse_ret)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,path);u.reg_write(A.UC_ARM_REG_R1,seq);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_resolve_file_path_5eddf6'] if compiled else 0x5eddf6
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 cases=[]
 for present in (False,True):
  for cmp_ret in (0,1,0xffffffff):
   for parse_ret in (0,1,42,0xffffffff):
    for path_text in ('/log/tp/t42','unrelated'):
     n=run(False,present,cmp_ret,parse_ret,path_text)
     c=run(True,present,cmp_ret,parse_ret,path_text)
     if n!=c:raise AssertionError((present,cmp_ret,parse_ret,path_text,n,c))
     cases.append((present,cmp_ret,parse_ret,path_text))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_RESOLVE_FILE_PATH_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Prefix length, byte compare and sequence parser are checked at call boundaries.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
