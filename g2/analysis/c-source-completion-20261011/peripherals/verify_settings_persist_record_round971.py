#!/usr/bin/env python3
"""Compare native and C terminal-mode persistence record and child calls."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/settings-persist-record-round971';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_persist_terminal_record.c'
obj=out/'settings_persist_terminal_record.o'
base=root/'build/c-firmware/terminal-os-delay-bridge-round970/apollo-main-terminal-os-delay.o'
linked=out/'apollo-main-settings-persist-record.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x4b04c4-0x438000:0x4b052e-0x438000]
assert int.from_bytes(blob[0x4b0530-0x438000:0x4b0534-0x438000],'little')==0x20003808
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint16_t audio_uart_hand_checksum_49acd4(const void*a,uint32_t b,const uint16_t*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_settings_kvdb_blob_write(const char*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_persist_record',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'crc':'audio_uart_hand_checksum_49acd4','write':'audio_settings_kvdb_blob_write','flags':'audio_log_flags','log':'audio_log_extended','short':'compressed_log_output'}
 addresses={'crc':0x49acd4,'write':0x4d957e,'flags':0x43d0ce,'log':0x43d574,'short':0x43ce9e}
 cases=[]
 for word in (0,0x01020304,0xffffffff):
  for status in (0,5):
   for flags in (0,1,2,4,7):
    outputs=[]
    for compiled in (False,True):
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
     uc.mem_map(0x100000,0x100000)
     for addr,data in segs:uc.mem_write(addr,data)
     uc.mem_map(0x20000000,0x200000)
     state=syms['audio_settings_terminal_record'] if compiled else 0x20003808
     inp=0x20010000;uc.mem_write(inp,word.to_bytes(4,'little'));uc.mem_write(state,b'\xaa'*4)
     hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in addresses.items()}
     calls=[]
     def string(p):return bytes(uc.mem_read(p,160)).split(b'\0')[0].decode('ascii')
     def hook(cpu,address,size,user):
      name=hooks.get(address)
      if not name:return
      r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
      if name=='crc':calls.append(('crc',r[0]-state,r[1],r[2],bytes(cpu.mem_read(state,4))));ret=0x1234
      elif name=='write':calls.append(('write',string(r[0]),r[1]-state,r[2],bytes(cpu.mem_read(state,4))));ret=status
      elif name=='flags':calls.append(('flags',));ret=flags
      elif name=='log':calls.append(('log',r[0],string(r[1]),string(r[2]),string(r[3])));ret=0
      else:calls.append(('short',r[0],string(r[1]),string(r[2])));ret=0
      cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
     uc.hook_add(UC_HOOK_CODE,hook)
     for reg,val in ((A.UC_ARM_REG_R0,inp),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
     uc.emu_start((syms['audio_settings_persist_record'] if compiled else 0x4b04c4)|1,0x600000,count=200)
     outputs.append((calls,bytes(uc.mem_read(state,4)),uc.reg_read(A.UC_ARM_REG_R0)))
    assert outputs[0]==outputs[1],(word,status,flags,outputs)
    cases.append((word,status,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_settings_persist_record'}
assert after-before=={'audio_settings_kvdb_blob_write'}
receipt={'round':971,'status':'PASS_NATIVE_SETTINGS_PERSIST_RECORD','component':'Apollo terminal mode KV record 0x4b04c4',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C record bytes, checksum and KV arguments, logging gates and return',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['KV blob writer 0x4d957e remains open','Final terminal callback and 49 registry callbacks remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
