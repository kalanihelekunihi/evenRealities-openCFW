#!/usr/bin/env python3
"""Compare stock tracepoint delete-file control flow with bounded C source."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_delete_file_5ee488.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-delete-file-5ee488';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_reply_buffer[0x206];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_tracepoint_role_char_5edadc(void){return 'R';}
int32_t audio_tracepoint_validate_file_name_5ede30(const char*a,char*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_tracepoint_resolve_file_path_5eddf6(char*a,uint32_t*b){(void)a;(void)b;return 0;}
void audio_tracepoint_storage_lock_47e088(void){}
int32_t audio_tracepoint_storage_unlink_47498c(const char*a){(void)a;return 0;}
void audio_tracepoint_make_result_message_5ee10a(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_tracepoint_reply_result_5ee134(const uint8_t*a){(void)a;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_delete_file_5ee488',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'flags':0x43d0ce,'extended':0x43d574,'compact':0x43ce9e,'role':0x5edadc,'validate':0x5ede30,'map':0x5eddf6,'lock':0x47e088,'unlink':0x47498c,'result':0x5ee10a,'reply':0x5ee134}
 source={'flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output','role':'audio_tracepoint_role_char_5edadc','validate':'audio_tracepoint_validate_file_name_5ede30','map':'audio_tracepoint_resolve_file_path_5eddf6','lock':'audio_tracepoint_storage_lock_47e088','unlink':'audio_tracepoint_storage_unlink_47498c','result':'audio_tracepoint_make_result_message_5ee10a','reply':'audio_tracepoint_reply_result_5ee134'}
 def run(compiled,magic,present,validate_ok,map_ok,unlink_ret,mask):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x400000)
  name=0x20073000 if present else 0
  if name:u.mem_write(name,b'abc.txt\0')
  reply=syms['audio_tracepoint_reply_buffer'] if compiled else 0x2037bbc8
  hooks={(syms[source[k]]&~1 if compiled else v):k for k,v in native.items()};calls=[]
  def word(a):return int.from_bytes(u.mem_read(a,4),'little')
  def put(a,x):u.mem_write(a,(x&0xffffffff).to_bytes(4,'little'))
  def string(a):return None if a==0 else bytes(u.mem_read(a,128)).split(b'\0')[0].decode('ascii')
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3));sp=cpu.reg_read(A.UC_ARM_REG_SP)
   if k=='flags':cpu.reg_write(A.UC_ARM_REG_R0,mask)
   elif k=='role':calls.append(('role',));cpu.reg_write(A.UC_ARM_REG_R0,ord('R'))
   elif k=='validate':
    calls.append(('validate',string(r0),r2));cpu.mem_write(r1,b'file/path\0');cpu.reg_write(A.UC_ARM_REG_R0,0 if validate_ok else 1)
   elif k=='map':
    calls.append(('map',string(r0)));cpu.mem_write(r0,b'mapped/path\0');put(r1,42);cpu.reg_write(A.UC_ARM_REG_R0,1 if map_ok else 0)
   elif k=='lock':calls.append(('lock',))
   elif k=='unlink':calls.append(('unlink',string(r0)));cpu.reg_write(A.UC_ARM_REG_R0,unlink_ret)
   elif k=='result':calls.append(('result',r0,r1,r2))
   elif k=='reply':calls.append(('reply',r0==reply))
   elif k=='extended':
    fmt=string(word(sp+4));msg=[]
    if fmt.startswith('tracepoint delete request'):
     msg=[word(sp+8),word(sp+12),string(word(sp+16))]
    elif fmt.startswith('tracepoint delete mapped') or fmt.startswith('tracepoint delete file'):
     msg=[string(word(sp+8)),word(sp+12)]
    else:msg=[string(word(sp+8))]
    calls.append(('extended',r0,string(r1),string(r2),string(r3),word(sp),fmt,*msg))
   else:
    fmt=string(r1);msg=[]
    if fmt.startswith('[tp.setting]tracepoint delete request'):
     msg=[r3,word(sp),string(word(sp+4))]
    elif fmt.startswith('[tp.setting]tracepoint delete mapped') or fmt.startswith('[tp.setting]tracepoint delete file'):
     msg=[string(r3),word(sp)]
    else:msg=[string(r3)]
    calls.append(('compact',r0,fmt,string(r2),*msg))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,magic);u.reg_write(A.UC_ARM_REG_R1,name);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_delete_file_5ee488'] if compiled else 0x5ee488
  u.emu_start(entry|1,0x600000,count=20000)
  return calls
 cases=[]
 for magic in (0,1,255):
  for present in (False,True):
   for validate_ok,map_ok,unlink_ret in ((False,False,0),(True,False,0),(True,True,0),(True,True,1)):
    for mask in (0,1,2,4,7):
     n=run(False,magic,present,validate_ok,map_ok,unlink_ret,mask)
     c=run(True,magic,present,validate_ok,map_ok,unlink_ret,mask)
     if n!=c:raise AssertionError((magic,present,validate_ok,map_ok,unlink_ret,mask,n,c))
     cases.append((magic,present,validate_ok,map_ok,unlink_ret,mask))
 receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_DELETE_FILE_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'limits':['File validator, mapper, storage lock and unlink effects compared at call boundaries; filesystem and hardware behavior unproved.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
