#!/usr/bin/env python3
"""Compare stock/C tracepoint file-list request at controlled child boundaries."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_request_file_name_5ee1f8.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-request-file-name-5ee1f8';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
 shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_reply_buffer[0x206];uint8_t audio_tracepoint_file_inventory[0x88];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_tracepoint_role_char_5edadc(void){return 'L';}
void audio_tracepoint_reset_pull_478110(uint8_t a){(void)a;}
int32_t audio_tracepoint_prepare_pull_48ec9e(void){return 0;}
int32_t audio_tracepoint_scan_files_5edc5a(void){return 0;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_tracepoint_format_list_name_5eddc8(uint32_t a,uint32_t b,char*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint8_t audio_uart_device_role_get(void){return 1;}
uint32_t audio_tracepoint_send_to_master_5ee066(uint32_t a,const uint8_t*b){(void)a;(void)b;return 0;}
''')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_request_file_name_5ee1f8',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'flags':0x43d0ce,'rolechar':0x5edadc,'reset':0x478110,'prepare':0x48ec9e,
         'scan':0x5edc5a,'zero':0x43c0e4,'format':0x5eddc8,'role':0x45a568,'send':0x5ee066}
 source={'flags':'audio_log_flags','rolechar':'audio_tracepoint_role_char_5edadc',
         'reset':'audio_tracepoint_reset_pull_478110','prepare':'audio_tracepoint_prepare_pull_48ec9e',
         'scan':'audio_tracepoint_scan_files_5edc5a','zero':'audio_uart_buffer_zero',
         'format':'audio_tracepoint_format_list_name_5eddc8','role':'audio_uart_device_role_get',
         'send':'audio_tracepoint_send_to_master_5ee066'}
 def run(compiled,count,role,prepared,scan_result,send_result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x20300000,0x100000)
  reply=syms['audio_tracepoint_reply_buffer'] if compiled else 0x2037bbc8
  inv=syms['audio_tracepoint_file_inventory'] if compiled else 0x2037cd24
  ready=syms['audio_tracepoint_local_file_list_ready'] if compiled else 0x20074ae4
  u.mem_write(reply,b'\xa5'*0x206)
  data=bytearray(0x88)
  for i in range(16):
   data[i*8:i*8+4]=(i+1).to_bytes(4,'little');data[i*8+4:i*8+8]=(100+i).to_bytes(4,'little')
  data[0x80:0x84]=count.to_bytes(4,'little');u.mem_write(inv,bytes(data));u.mem_write(ready,b'\x7f')
  hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
  def hook(cpu,pc,size,data):
   k=hooks.get(pc)
   if not k:return
   r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
   value=0
   if k=='flags':pass
   elif k=='rolechar':value=ord('L')
   elif k=='reset':calls.append(('reset',r0))
   elif k=='prepare':calls.append(('prepare',));value=prepared
   elif k=='scan':calls.append(('scan',));value=scan_result
   elif k=='zero':calls.append(('zero',r0==reply,r1,r2));cpu.mem_write(r0,b'\0'*r1)
   elif k=='format':
    calls.append(('format',r0,r1,r2==reply+6+32*(r0-1),r3))
    cpu.mem_write(r2,('L:t%d'%r0).encode()+b'\0');value=5
   elif k=='role':value=role
   elif k=='send':calls.append(('send',r0,r1==reply));value=send_result
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_R0,0x5a);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_request_file_name_5ee1f8'] if compiled else 0x5ee1f8
  u.emu_start(entry|1,0x600000,count=100000)
  return bytes(u.mem_read(reply,0x206)).hex(),bytes(u.mem_read(ready,1)).hex(),calls
 cases=[]
 for count in (0,1,16,17):
  for role in (1,2):
   for prepared in (0,-5):
    for scan_result in (0,-1):
     for send_result in (0,-5):
      n=run(False,count,role,prepared,scan_result,send_result)
      c=run(True,count,role,prepared,scan_result,send_result)
      if n!=c:raise AssertionError((count,role,prepared,scan_result,send_result,n,c))
      cases.append((count,role,prepared,scan_result,send_result))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_REQUEST_FILE_NAME_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'Reply clear, capped inventory names, prepare/scan errors, master-ready and slave-send paths with controlled child calls and logging disabled.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
