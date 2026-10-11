#!/usr/bin/env python3
"""Stock VFP wrapper versus archive soft-float math entry semantics."""
import hashlib, itertools, json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/float_runtime_offline/math.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK=Path('/tmp/audio-soft-float-math.ld');ELF=Path('/tmp/audio-soft-float-math.elf')
LINK.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Og',
 '-ffreestanding','-fno-builtin','-nostdlib','-T',str(LINK),str(SOURCE),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);code=e.get_section_by_name('.text').data()
 syms={s.name:s['st_value']|1 for s in e.get_section_by_name('.symtab').iter_symbols()}
original={'floorf':0x43a5a1,'roundf':0x577d09,'ceilf':0x577d41,'fmodf':0x577c3d}

def run(stock,op,a,b,fpscr):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x2000);u.mem_write(0x100000,code)
 u.mem_map(0x20000000,0x80000);u.mem_map(0xe000e000,0x2000)
 u.mem_write(0xe000ed88,struct.pack("<I",0xf00000))
 u.reg_write(UC_ARM_REG_S0,0)
 u.emu_start(0x43a5a1,0,count=1)
 u.reg_write(UC_ARM_REG_FPSCR,fpscr)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 u.reg_write(UC_ARM_REG_S0,a);u.reg_write(UC_ARM_REG_S1,b)
 u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b)
 u.mem_write(0x20074f14,struct.pack('<I',0xa5a55a5a))
 writes=[]
 def wr(_cpu,_access,addr,size,value,_):writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x20074f14,end=0x20074f17)
 u.emu_start(original[op] if stock else syms['audio_'+op],0x2007f000,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(result=u.reg_read(UC_ARM_REG_S0) if stock else u.reg_read(UC_ARM_REG_R0),
             fpscr=u.reg_read(UC_ARM_REG_FPSCR),errno=struct.unpack('<I',u.mem_read(0x20074f14,4))[0],
             errno_writes=writes,sp=u.reg_read(UC_ARM_REG_SP))

values=[0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,
 0x3e800000,0xbe800000,0x3f000000,0xbf000000,0x3f800000,0xbf800000,0x3fc00000,
 0xbfc00000,0x40000000,0xc0000000,0x4b800000,0xcb800000,0x7f7fffff,0xff7fffff,
 0x7f800000,0xff800000,0x7fc01234,0xffc01234,0x7f801234,0xff801234]
profiles=[0,1<<22,2<<22,3<<22,1<<24,1<<25,(1<<24)|(1<<25),0xa000009f]
cases=[]
def compare(op,a,b,profile):
 old=run(True,op,a,b,profile);new=run(False,op,a,b,profile)
 assert old==new,(op,hex(a),hex(b),hex(profile),old,new)
 cases.append(dict(op=op,a=a,b=b,fpscr=profile,state=old))
for op,a,profile in itertools.product(('floorf','roundf','ceilf'),values,profiles):compare(op,a,0,profile)
for a,b,profile in itertools.product(values,values,(0,1<<24,1<<25,0xa000009f)):compare('fmodf',a,b,profile)
rng=random.Random(0x577c3c)
for i in range(400):compare('fmodf',rng.getrandbits(32),rng.getrandbits(32),profiles[i%len(profiles)])
result=dict(status='PASS',fresh_cases=len(cases),original_entries=original,
 stock_abi='single/dual float arguments and float result in S0/S1',archive_abi='same IEEE754 bits in R0/R1 and result R0',
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 link_script=LINK.read_text(),cases=cases,
 limits=['Archive source-side soft-float ABI only; not a binary drop-in for original hard-float callers.',
         'Cortex-M4 source oracle; complete M55 behavior and exception/scheduler effects outside fixture.'])
Path(__file__).with_name('soft-float-math-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'soft-float math original/source ABI-adapted cases')
