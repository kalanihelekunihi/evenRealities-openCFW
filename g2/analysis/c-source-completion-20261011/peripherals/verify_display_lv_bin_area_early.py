from pathlib import Path
import subprocess,tempfile,json,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-area-round66/area_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);names=re.findall(r'extern[^;]*?\b(audio_\w+)\(',SRC.read_text());shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512];\n'+'\n'.join('unsigned '+n+'(void){return 0;}' for n in names));elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_get_area_4c7e4c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']

 count=0
 for cf in range(256):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;u.mem_write(dsc+32,(cf<<8).to_bytes(4,'little'));calls=[];cut=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1
   def string(a):
    data=bytearray()
    while (v:=bytes(u.mem_read(a+len(data),1)))!=b'\0':data.extend(v)
    return data.decode()
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def hook(uc,a,size,user):
    if a!=cut:return
    args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);fmt=string(word(sp));calls.append((args[0],string(args[1]),args[2],string(args[3]),fmt,word(sp+4) if fmt.startswith('CF:') else None));uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,dsc);u.reg_write(UC_ARM_REG_R2,0x20006000);u.reg_write(UC_ARM_REG_R3,0x20007000);u.emu_start((syms['audio_uart_lv_bin_decoder_get_area_4c7e4c'] if isc else 0x4c7e4c)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(cf,outputs);count+=1
 r={'status':'PASS_REJECTION_AND_NULL_DATA_PATHS_ONLY','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['All256 formats with null user_data; logger controlled cut.','Supported-format scanline allocation/decoding remains unverified; candidate unselected.']};(SRC.parent/'area-early-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
