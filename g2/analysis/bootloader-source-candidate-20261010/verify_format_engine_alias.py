#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
alias=R/'g2/components/bootloader/source_candidate_20261010/format_engine_alias.c';bounded=R/'g2/components/bootloader/initializer_callbacks/bounded_format_native/bounded_format.c';engine=R/'g2/components/bootloader/initializer_callbacks/iar_format_native'
sources=[alias,bounded]+sorted(engine.glob('*.c'));cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'format-engine-alias-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_elog_snprintf','-Wl,--gc-sections',*[str(s) for s in sources],'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_boot_elog_snprintf');segs=[(s['p_vaddr'],s.data(),s['p_memsz']) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DST=0x20011000;FMT=0x20010000;TEXT=0x20010100;SP=0x2003eff0
def run(source,fmt,arg,n):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b,sz in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_write(FMT,fmt+b'\0');u.mem_write(TEXT,b'sample\0');u.mem_write(DST,b'\xa5'*64)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(DST,n,FMT,TEXT if arg=='text' else arg)):u.reg_write(r,v)
 u.emu_start((entry if source else 0x41b218)|1,0x10000000,count=1000000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000,(source,fmt,hex(u.reg_read(UC_ARM_REG_PC)))
 return dict(ret=u.reg_read(UC_ARM_REG_R0),dst=bytes(u.mem_read(DST,64)).hex(),sp=u.reg_read(UC_ARM_REG_SP))
cases=[]
for fmt,arg in ((b'plain',0),(b'n=%d',0),(b'n=%d',42),(b'%u',0xffffffff),(b'%08X',0x1234),(b'%s','text')):
 for n in (0,1,8,32):
  a,b=run(False,fmt,arg,n),run(True,fmt,arg,n)
  assert a==b,(fmt,arg,n,a,b)
  cases.append((fmt.decode(),arg,n))
receipt=dict(status='PASS',cases=len(cases),image_sha256=hashlib.sha256(blob).hexdigest(),alias_sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),bounded_sha256=hashlib.sha256(bounded.read_bytes()).hexdigest(),engine_sha256={s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sorted(engine.glob('*.c'))},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Original stock snprintf 0x41b218 versus source bounded wrapper + full source IAR engine, scalar formats only. Full floating path is covered by prior M55 QEMU receipts, not this Unicorn oracle; arbitrary formatting, trap paths and hardware not claimed.')
(H/'format-engine-alias-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS format engine alias',len(cases))
