from pathlib import Path
import subprocess,tempfile,json,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-open-round65/open_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);names=re.findall(r'extern[^;]*?\b(audio_\w+)\(',SRC.read_text());shim=td/'shim.c';shim.write_text('\n'.join('unsigned '+n+'(void){return 0;}' for n in names));elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_open_4c7b24',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for typ in [0]+list(range(2,256)):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;image=0x20004000;u.mem_write(dsc+12,image.to_bytes(4,'little'));u.mem_write(dsc+16,bytes([typ]));calls=[];cut=(syms['audio_uart_lv_bin_decoder_data_free_4c8210'] if isc else 0x4c8210)&~1
   def hook(uc,a,size,user):
    if a!=cut:return
    calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,dsc);u.emu_start((syms['audio_uart_lv_bin_decoder_open_4c7b24'] if isc else 0x4c7b24)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(typ,outputs);count+=1
 r={'status':'PASS_EARLY_PATHS_ONLY_NOT_FULL_OPEN_QUALIFICATION','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Only variable null-data return and unsupported source-type cleanup paths are executed.','Other link shims are unexecuted; full file/format/postprocess/cache comparisons remain required.','Candidate remains unselected.']};(SRC.parent/'open-early-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
