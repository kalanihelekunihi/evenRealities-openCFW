"""Bounded actual ARM C/native grid col/row preparation with named child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_grid_track_prepare.c'
NATIVE_SPECIAL={'audio_uart_lv_malloc':0x44f718,'audio_uart_lv_free':0x44f758,
 'audio_uart_lvgl_log':0x44d25c}
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'prep.o';shim=Path(td)/'shim.c';elf=Path(td)/'prep.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(SRC),'-o',str(obj)],check=True)
 imports=[x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
 shim.write_text('#include <stdint.h>\n'+''.join('uint32_t '+n+
     '(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n' for n in imports))
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_basic_prepare_b_48cbf8',str(obj),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[('fixed',(10,20,0x1fffffff)),('fraction',(0x1fffff9d,10,0x1fffffff)),
        ('content',(0x1fffff9a,10,0x1fffffff)),
        ('content_child',(0x1fffff9a,10,0x1fffffff)),('inherited',(10,20,0x1fffffff)),
        ('missing',(10,20,0x1fffffff))]
 total=0
 for axis in ('col','row'):
  for case,values in cases:
   outs=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    object,parent,state,desc=0x20003000,0x20003100,0x20003200,0x20003400
    u.mem_write(desc,struct.pack('<III',*values));u.mem_write(state,b'\x55'*32)
    sp=0x200ff000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,object);u.reg_write(UC_ARM_REG_R1,state)
    u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0x12345678)
    mapping={(syms[n]&~1 if is_c else NATIVE_SPECIAL.get(n,int(n.rsplit('_',1)[1],16) if n not in NATIVE_SPECIAL else 0)):n for n in imports}
    calls=[];alloc_count=[0]
    def hook(uc,a,size,_):
     if a not in mapping:return
     n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     short=n.rsplit('_',1)[-1];ret=0
     if short in ('48c97c','48c986'):
      ret=desc if case not in ('inherited','missing') or (case=='inherited' and r0==parent) else 0
      calls.append((short,r0))
     elif short=='44dca2':ret=parent;calls.append((short,r0))
     elif short in ('48c990','48c99a'):ret=0;calls.append((short,r0))
     elif short in ('48c9a4','48c9ae'):
      ret=1 if r0 in (0x20005000,0x20005100) else 2
      calls.append((short,r0))
     elif n=='audio_uart_lv_malloc':
      ret=0x20004000+alloc_count[0]*0x100;alloc_count[0]+=1;calls.append(('malloc',r0,ret))
     elif short=='454738':
      uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));ret=r0;calls.append((short,r0,r1,r2))
     elif short=='48d4d0':
      ret=2;calls.append((short,r0))
     elif short in ('43fe16','43fe70'):ret=100;calls.append((short,r0))
     elif short in ('48c860','48c856'):ret=5;calls.append((short,r0,r1))
     elif short=='44ddea':ret=2 if case=='content_child' else 0;calls.append((short,r0))
     elif short=='44dce2':ret=(0x20005000,0x20005100)[r1] if r1<2 else 0;calls.append((short,r0,r1))
     elif short=='43e11c':ret=1 if r0==0x20005000 else 0;calls.append((short,r0,r1))
     elif short in ('43fd9e','43fdda'):ret=20;calls.append((short,r0))
     elif short=='48ca18':
      ret=(r0+r1//2)//r1;calls.append((short,r0,r1))
     elif n=='audio_uart_lv_free':calls.append(('free',r0))
     elif n=='audio_uart_lvgl_log':calls.append(('log',r0,uc.reg_read(UC_ARM_REG_R2)))
     else:calls.append((short,r0,r1))
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    entry='audio_uart_lv_basic_prepare_b_48cbf8' if axis=='col' else 'audio_uart_lv_basic_prepare_a_48cdec'
    native=0x48cbf8 if axis=='col' else 0x48cdec
    u.emu_start((syms[entry] if is_c else native)|1,0x600000,count=2000)
    state_bytes=bytes(u.mem_read(state,32));allocs=alloc_count[0]
    alloc_bytes=[bytes(u.mem_read(0x20004000+i*0x100,12)) for i in range(allocs)]
    effects=[x for x in calls if x[0] in ('malloc','free','454738','48ca18','log')]
    getters=sorted(x for x in calls if x[0] not in ('malloc','free','454738','48ca18','log'))
    returned=(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),80)).split(b'\0')[0]
              if case=='missing' else u.reg_read(UC_ARM_REG_R0))
    outs.append((effects,getters,state_bytes,alloc_bytes,returned))
   assert outs[0]==outs[1],(axis,case,outs)
   total+=1
 print(f'PASS {total} compiled-C/native LV grid track preparation cases')
