#!/usr/bin/env python3
"""Compare stock tracepoint filename normalization against C provider dispatch."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_validate_file_name_5ede30.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-validate-file-name-5ede30';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint32_t audio_tracepoint_role_char_5edadc(void){return 'R';}
uint32_t audio_uart_ring_parse_uint_48d874(const char*a,const char**b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_tracepoint_resolve_file_path_5eddf6(char*a,uint32_t*b){(void)a;(void)b;return 0;}
int32_t audio_tracepoint_parse_sequence_5edaf0(const char*a,uint32_t*b){(void)a;(void)b;return 0;}
void audio_tracepoint_format_file_path_5edba2(char*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_validate_file_name_5ede30',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'role':0x5edadc,'decimal':0x48d874,'resolve':0x5eddf6,'parse':0x5edaf0,'format':0x5edba2}
 source={'role':'audio_tracepoint_role_char_5edadc','decimal':'audio_uart_ring_parse_uint_48d874','resolve':'audio_tracepoint_resolve_file_path_5eddf6','parse':'audio_tracepoint_parse_sequence_5edaf0','format':'audio_tracepoint_format_file_path_5edba2'}
 def run(compiled,name,present,out_present,capacity,role,resolve_ok,parse_ok):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);nameptr=0x20073000 if present else 0;out=0x20073100 if out_present else 0
  if nameptr:u.mem_write(nameptr,name.encode()+b'\0')
  if out:u.mem_write(out,b'\xa5'*96)
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
  def string(a):return bytes(u.mem_read(a,96)).split(b'\0')[0].decode('ascii')
  def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
   if k=='role':calls.append(('role',));cpu.reg_write(A.UC_ARM_REG_R0,ord(role))
   elif k=='decimal':
    s=string(r0);m=re.match(r'[0-9]+',s);digits=m.group(0) if m else '';put(r1,r0+len(digits));calls.append(('decimal',s,r2,digits));cpu.reg_write(A.UC_ARM_REG_R0,int(digits or '0')&0xffffffff)
   elif k=='resolve':calls.append(('resolve',string(r0)));put(r1,42);cpu.reg_write(A.UC_ARM_REG_R0,1 if resolve_ok else 0)
   elif k=='parse':calls.append(('parse',string(r0)));put(r1,17);cpu.reg_write(A.UC_ARM_REG_R0,1 if parse_ok else 0)
   else:
    calls.append(('format',r0==out,r1,r2));cpu.mem_write(r0,b'PATH\0')
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,nameptr);u.reg_write(A.UC_ARM_REG_R1,out);u.reg_write(A.UC_ARM_REG_R2,capacity);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_validate_file_name_5ede30'] if compiled else 0x5ede30
  u.emu_start(entry|1,0x600000,count=10000)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,8)).hex() if out else None,calls
 cases=[]
 for name in ('','t0','t1','t42','t12x','R:t42','L:t42','R:tp_17.bin','tp_17.bin','/log/tp/t17.bin','x'):
  for role in ('R','L'):
   for resolve_ok,parse_ok in ((0,0),(0,1),(1,0)):
    for present,out_present,capacity in ((False,True,80),(True,False,80),(True,True,0),(True,True,80)):
     n=run(False,name,present,out_present,capacity,role,resolve_ok,parse_ok)
     c=run(True,name,present,out_present,capacity,role,resolve_ok,parse_ok)
     if n!=c:raise AssertionError((name,role,resolve_ok,parse_ok,present,out_present,capacity,n,c))
     cases.append((name,role,resolve_ok,parse_ok,present,out_present,capacity))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_FILENAME_VALIDATOR_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['Numeric conversion, path resolver, sequence parser and path formatter are checked at call boundaries.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
