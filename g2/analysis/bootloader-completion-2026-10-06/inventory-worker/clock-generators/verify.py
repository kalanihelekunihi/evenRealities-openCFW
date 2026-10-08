"""Bounded original-instruction comparison; PLL descendants are explicit cuts."""
import argparse,hashlib,json,struct,itertools
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5]
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-clock-generators.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('comparison.json'));args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with args.elf.open('rb') as f:
 elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
STOP=0x08000000;DEST=0x20001000;traces={};cuts=[]
def run(source,family,values,fixture):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_A15)
 u.mem_map(0x410000,0x25000);u.mem_map(0x08000000,0x30000);u.mem_map(0x20000000,0x40000)
 if source:
  mapped=set(range(0x410000,0x435000,4096))|set(range(0x08000000,0x08030000,4096))|set(range(0x20000000,0x20040000,4096))
  for address,data in segments:
   for page in range(address&~4095,(address+len(data)+4095)&~4095,4096):
    if page not in mapped:u.mem_map(page,4096);mapped.add(page)
   u.mem_write(address,data)
 else:u.mem_write(0x410000,blob)
 u.mem_write(DEST,bytes([0xa5])*16);u.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(a.UC_ARM_REG_FPEXC,0x40000000);u.reg_write(a.UC_ARM_REG_FPSCR,0)
 entries={'hf2':('opencfw_boot_startup_hf2_generate',0x426c24),'pll':('opencfw_boot_startup_pll_generate',0x427160),'min':('opencfw_boot_pll_min_generate',0x427040)};done=False;calls=[]
 def ret(value):u.reg_write(a.UC_ARM_REG_R0,value);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
 def hook(cpu,pc,size,unused):
  nonlocal done
  if pc==STOP:done=True;u.emu_stop();return
  if not source:traces[pc]=bytes(u.mem_read(pc,size)).hex()
  if family=='pll' and pc==((symbols['opencfw_boot_pll_min_generate']&~1) if source else 0x427040):
   index=len(calls);dest=u.reg_read(a.UC_ARM_REG_R0);calls.append([u.reg_read(r) for r in [a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]])
   u.mem_write(dest,fixture['cfg'][index]);ret(fixture['status'][index]);return
  if family=='min' and pc==((symbols['opencfw_boot_pll_gcd']&~1) if source else 0x426d48):
   calls.append(['gcd',u.reg_read(a.UC_ARM_REG_S0),u.reg_read(a.UC_ARM_REG_S1)]);u.reg_write(a.UC_ARM_REG_S0,struct.unpack('<I',struct.pack('<f',fixture['gcd']))[0]);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if family=='min' and pc==((symbols['opencfw_boot_pll_vco_generate']&~1) if source else 0x426f6c):
   calls.append(['vco',u.reg_read(a.UC_ARM_REG_S0),u.reg_read(a.UC_ARM_REG_S1)]);p=u.reg_read(a.UC_ARM_REG_R0);u.mem_write(p+1,fixture['cfg'][1:12]);ret(fixture['status']);return
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
 for r,v in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],values):u.reg_write(r,v)
 name,stock=entries[family];u.emu_start((symbols[name] if source else stock)|1,STOP+2,count=20000);assert done,(source,family,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return {'return':u.reg_read(a.UC_ARM_REG_R0),'destination':bytes(u.mem_read(DEST,16)).hex(),'calls':calls,'fpscr':u.reg_read(a.UC_ARM_REG_FPSCR)}
def cfg(vco=0,frac=1,refdiv=1,p1=1,p2=1):return struct.pack('<6BHI',0xee,vco,frac,refdiv,p1,p2,32,0x123456)
rows=[]
def compare(family,values,fixture):
 actual=run(False,family,values,fixture);reconstructed=run(True,family,values,fixture)
 assert actual==reconstructed,(family,values,fixture,actual,reconstructed)
 rows.append({'family':family,'arguments':values,'fixture':{k:([v.hex() for v in x] if k=='cfg' and isinstance(x,list) else x.hex() if isinstance(x,bytes) else x) for k,x in fixture.items()},'result':actual})
for ref,target,shift in itertools.product([0,32768,12000000,24000000,0xffffffff],[0,196608000,250000000,0xffffffff],[0,1,2,15,31,32,255,256]):compare('hf2',[ref,target,shift,DEST],{})
for statuses,low,high in itertools.product([(0,0),(0,5),(5,0),(5,5)],[cfg(),cfg(1,0,2,4,3)],[cfg(),cfg(1,1,3,2,4),cfg(1,0,3,2,4)]):
 for ref,target in [(12000000,48000000),(0xffffffff,0xffffffff)]:compare('pll',[DEST,ref,target],{'cfg':[low,high],'status':statuses})
for ref,target,minimum,gcd,status,frac,refdiv in itertools.product([12000000,12000001,24000000],[0,1,12000000,48000000,250000000],[60000000,240000000],[0.5,2.0],[0,5],[0,1],[1,3]):compare('min',[DEST,ref,target,minimum],{'cfg':cfg(frac=frac,refdiv=refdiv),'gcd':gcd,'status':status})
result={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/clock_generators.c').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in sorted(traces.items())},'limits':['HF2 original and reconstructed FP instructions execute under A15 Unicorn; FPSCR starts zero. No hardware or alternative rounding certification.','PLL selector cuts minimum-VCO child; minimum-VCO cuts GCD426d48 and VCO426f6c equally. Configurations are synthetic. No integrated source-closure claim.','No SRAM memory-write hooks; preserved prior Unicorn copy negative controls unchanged.']};args.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows))
