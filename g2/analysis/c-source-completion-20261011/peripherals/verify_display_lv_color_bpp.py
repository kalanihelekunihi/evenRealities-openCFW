from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR
ROOT=Path(__file__).resolve().parents[3]
SRC=Path(__file__).parent/'root-draw-helpers-round68/bpp_candidate.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_color_bpp_440f44',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for upper in [0,0x100,0x87654300,0xffffff00]:
  for cf in range(256):
   outputs=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,upper|cf)
    u.emu_start((syms['audio_uart_lv_color_bpp_440f44'] if isc else 0x440f44)|1,0x600000,count=1000)
    outputs.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)))
   assert outputs[0]==outputs[1],(hex(upper|cf),outputs)
   count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_ALL_BYTE_FORMATS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':['0x440f44','0x440fc4'],'child_cuts':0,'limits':['Leaf return and stack comparison; full image layout/byte equality/hardware unproven.']}
 (SRC.parent/'bpp-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
