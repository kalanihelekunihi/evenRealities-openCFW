from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/align_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512];void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_align_48ab04',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for kind,present,cf,ret in itertools.product(['align','align_ex','zero'],[0,1],[0,1,255,256,0x87654321],[0,0x20005003]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   handlers=(syms['audio_uart_display_lv_root']+0xc8 if isc else 0x2006f610) if kind=='align' else 0x20003000;data=0x20004000;callback=0x600100;u.mem_write(handlers+8,((callback|1) if present else 0).to_bytes(4,'little'));calls=[];clear=(syms['audio_uart_lv_basic_box_clear_454746'] if isc else 0x454746)&~1
   def hook(uc,a,size,user):
    if a not in [callback,clear]:return
    regs=[UC_ARM_REG_R0,UC_ARM_REG_R1] if a==callback else [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2];calls.append(tuple(uc.reg_read(r) for r in regs));uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   args=[handlers,data,cf] if kind=='align_ex' else [data,cf]
   for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
   name,native={'align':('audio_uart_lv_draw_align_48ab04',0x48ab04),'align_ex':('audio_uart_lv_draw_align_ex_48ab16',0x48ab16),'zero':('audio_uart_lv_draw_memzero_48aa54',0x48aa54)}[kind];u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0) if kind!='zero' else None,u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(kind,present,cf,ret,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_ZERO_ALIGN','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Clear child and indirect alignment callback controlled cuts; callback installation and hardware remain unproven.','Null handler returns null; native byte-format truncation and default owner address checked.','Void zero-wrapper scratch R0 not qualified as return API.']};(SRC.parent/'align-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
