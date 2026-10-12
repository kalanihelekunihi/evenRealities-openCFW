from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
BASE=Path(__file__).parent; SRC=BASE/'root-postprocess-leaves-round89/leaves_candidate.c'; ROOT=BASE.parents[2]
blob=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'leaves.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_color_has_alpha_440fc4',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
 with elf.open('rb') as f:
  for s in ELFFile(f).iter_segments():
   if s['p_type']=='PT_LOAD':u.mem_write(s['p_vaddr'],s.data())
 def run(pc,a,b):
  u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start(pc|1,0x600000,count=100)
  assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 count=0
 for value in range(1024):
  assert run(0x440fc4,value,0)==run(syms['audio_uart_lv_color_has_alpha_440fc4'],value,0);count+=1
 rng=random.Random(89)
 pairs=[(f,m) for f in [0,1,32,65535,0x8000] for m in [0,1,32,65535,65536,0xffffffff,0x80000000]]+[(rng.getrandbits(16),rng.getrandbits(32)) for _ in range(2048)]
 for flags,mask in pairs:
  u.mem_write(0x20001000,struct.pack('<I',(flags<<16)|rng.getrandbits(16)))
  before=bytes(u.mem_read(0x20001000,4))
  assert run(0x48b73c,0x20001000,mask)==run(syms['audio_uart_lv_draw_buf_has_flag_48b73c'],0x20001000,mask)
  assert before==bytes(u.mem_read(0x20001000,4));count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_POSTPROCESS_LEAVES','cases':count,'payload_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_ranges':['440fc4..440fde','48b73c..48b750'],'dependency_commit':subprocess.check_output(['git','-C',str(ROOT.parent/'third-party/upstream/lvgl'),'rev-parse','HEAD'],text=True).strip(),'limits':['No child cuts. Exhaustive low-byte color formats; bounded flag masks.','Unselected candidates; full image and hardware compatibility not proven.']}
 (SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
