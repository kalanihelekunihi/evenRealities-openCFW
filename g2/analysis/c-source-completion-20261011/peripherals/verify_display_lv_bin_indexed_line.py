from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-indexed-line-round77/indexed_line_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
PAL,DATA,OUT=0x20003000,0x20008000,0x20009000
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decode_indexed_line_4c8c94',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(isc,cf,x,width,alias):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(PAL,struct.pack('<256I',*[((i*0x1020304)^0x87654321)&0xffffffff for i in range(256)]));u.mem_write(DATA,bytes((i*37+11)&255 for i in range(256)));u.mem_write(OUT,b'\xa5'*192)
  output={0:OUT,1:DATA+64,2:PAL}[alias];u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[cf,PAL,x&0xffffffff,width&0xffffffff]):u.reg_write(reg,v)
  u.mem_write(0x200ff000,struct.pack('<II',DATA+64,output));u.emu_start((syms['audio_uart_lv_bin_decode_indexed_line_4c8c94'] if isc else 0x4c8c94)|1,0x600000,count=3000)
  return u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(PAL,1024)),bytes(u.mem_read(DATA,256)),bytes(u.mem_read(OUT,192))
 cases=list(itertools.product(range(256),[0],[0,1,0x80000000,0xffffffff],[0]))
 cases += [(cf|upper,x,width,alias) for cf,upper,x,width,alias in itertools.product([7,8,9,10],[0,0xffffff00],[-31,-15,-7,-1,0,1,2,3,7,8,15],[0,1,7,8,17,31,0x80000000,0xffffffff],[0,1,2])]
 cases += [(cf,x,width,0) for cf,x,width in itertools.product([7,8,9,10],[0x7fffffff,0x80000000],[0,0x80000000,0xffffffff])]
 for cf,x,width,alias in cases:
  a=run(False,cf,x,width,alias);b=run(True,cf,x,width,alias);assert a==b,(cf,x,width,alias,a[:2],b[:2])
 r={'status':'PASS_COMPILED_ARM_NATIVE_INDEXED_LINE','cases':len(cases),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'child_cuts':0,'limits':['Bounded widths; invalid formats, signed negative x, high input bits and palette/input aliasing covered.','No full image layout/byte equality/hardware proof.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
