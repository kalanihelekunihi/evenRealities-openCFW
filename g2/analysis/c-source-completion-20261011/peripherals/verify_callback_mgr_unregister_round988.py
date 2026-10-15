#!/usr/bin/env python3
"""Native/C callback-manager unregister list and logging contract."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/callback-mgr-unregister-round988';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/display_callback_manager_unregister.c'
obj=out/'display_callback_manager_unregister.o'
base=root/'build/c-firmware/ble-status-callbacks-round987/apollo-main-ble-status-callbacks.o'
linked=out/'apollo-main-callback-mgr-unregister.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5103c4-0x438000:0x510546-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_callback_mgr_delete_node(void*a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_callback_mgr_unregister',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'delete':'audio_callback_mgr_delete_node','flags':'audio_log_flags','log':'audio_log_extended','short':'compressed_log_output'}
 addrs={'delete':0x5100fc,'flags':0x43d0ce,'log':0x43d574,'short':0x43ce9e}
 cases=[]
 for scenario in ('null_mgr','null_cb','empty','head','middle','absent'):
  for flags in (0,1,2,4,7):
   outputs=[]
   for compiled in (False,True):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
    uc.mem_map(0x100000,0x100000)
    for addr,data in segs:uc.mem_write(addr,data)
    uc.mem_map(0x20000000,0x200000)
    mgr=0x20010000;n1=0x20011000;n2=0x20011100;name=0x20012000;cb=0x20013001;other=0x20013005
    uc.mem_write(mgr,b'\0'*12);uc.mem_write(mgr+8,name.to_bytes(4,'little'));uc.mem_write(mgr+4,b'\x02');uc.mem_write(name,b'ble_status\0')
    uc.mem_write(n1,(cb if scenario=='head' else other).to_bytes(4,'little')+n2.to_bytes(4,'little'))
    uc.mem_write(n2,(cb if scenario=='middle' else other).to_bytes(4,'little')+b'\0'*4)
    if scenario!='empty':uc.mem_write(mgr,n1.to_bytes(4,'little'))
    hooks={((syms[names[k]] if compiled else v)&~1):k for k,v in addrs.items()}
    calls=[]
    def string(p):return bytes(uc.mem_read(p,180)).split(b'\0')[0].decode('ascii')
    def hook(cpu,pc,size,user):
     kind=hooks.get(pc)
     if not kind:return
     r=[cpu.reg_read(getattr(A,'UC_ARM_REG_R'+str(i))) for i in range(4)]
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     if kind=='delete':calls.append(('delete',r[0]-n1));ret=0
     elif kind=='flags':calls.append(('flags',));ret=flags
     elif kind=='log':
      line=int.from_bytes(cpu.mem_read(sp,4),'little');fmt=string(int.from_bytes(cpu.mem_read(sp+4,4),'little'))
      extras=()
      if '%s' in fmt:extras+=(string(int.from_bytes(cpu.mem_read(sp+8,4),'little')),)
      if '%d' in fmt:extras+=(int.from_bytes(cpu.mem_read(sp+12,4),'little'),)
      calls.append(('log',r[0],string(r[1]),string(r[2]),string(r[3]),line,fmt,extras));ret=0
     else:
      fmt=string(r[1]);extras=()
      if '%s' in fmt:extras+=(string(r[3]),)
      if '%d' in fmt:extras+=(int.from_bytes(cpu.mem_read(sp,4),'little'),)
      calls.append(('short',r[0],fmt,string(r[2]),extras));ret=0
     cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE,hook)
    uc.reg_write(A.UC_ARM_REG_R0,0 if scenario=='null_mgr' else mgr)
    uc.reg_write(A.UC_ARM_REG_R1,0 if scenario=='null_cb' else cb)
    uc.reg_write(A.UC_ARM_REG_SP,0x201ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
    uc.emu_start((syms['audio_callback_mgr_unregister'] if compiled else 0x5103c4)|1,0x600000,count=280)
    outputs.append((calls,bytes(uc.mem_read(mgr,12)),bytes(uc.mem_read(n1,8)),bytes(uc.mem_read(n2,8))))
   assert outputs[0]==outputs[1],(scenario,flags,outputs)
   cases.append((scenario,flags))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_callback_mgr_unregister'}
assert after-before=={'audio_callback_mgr_delete_node'}
receipt={'round':988,'status':'PASS_NATIVE_CALLBACK_MGR_UNREGISTER','component':'Apollo callback-manager unregister 0x5103c4',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C null/empty/head/middle/absent paths, list bytes, node release call and logging',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Node delete 0x5100fc remains open','Scheduler/heap and final RAM layout remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
