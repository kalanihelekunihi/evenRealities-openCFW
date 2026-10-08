"""Native stock/source math comparison. No child answer stubs or stock source fallback."""
import argparse,hashlib,json,random,struct,collections
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-clock-math-native.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('math-comparison.json'));args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with args.elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
STOP=0x08000000;DEST=0x20001000;trace={}
ENTRIES={'floor':('opencfw_boot_pll_floor',0x427c90),'round':('opencfw_boot_pll_round',0x427d98),'ceil':('opencfw_boot_pll_ceil',0x427dd0),'mod':('opencfw_boot_pll_mod',0x427ccc),'gcd':('opencfw_boot_pll_gcd',0x426d48),'integer':('opencfw_boot_pll_integer',0x426db4),'fraction':('opencfw_boot_pll_fraction',0x426eac),'vco':('opencfw_boot_pll_vco_generate',0x426f6c),'min':('opencfw_boot_pll_min_generate',0x427040),'pll':('opencfw_boot_startup_pll_generate',0x427160)}
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def run(source,name,floats,ints):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_A15);u.mem_map(0x410000,0x25000);u.mem_map(0x08000000,0x30000);u.mem_map(0x20000000,0x40000)
 if source:
  mapped=set(range(0x410000,0x435000,4096))|set(range(0x08000000,0x08030000,4096))|set(range(0x20000000,0x20040000,4096))
  for address,data in segments:
   for page in range(address&~4095,(address+len(data)+4095)&~4095,4096):
    if page not in mapped:u.mem_map(page,4096);mapped.add(page)
   u.mem_write(address,data)
 else:u.mem_write(0x410000,blob)
 u.mem_write(DEST,bytes([0xa5])*32);u.mem_write(0x20027194,struct.pack('<I',0xa5a5a5a5));u.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(a.UC_ARM_REG_FPEXC,0x40000000);u.reg_write(a.UC_ARM_REG_FPSCR,0)
 done=False
 def hook(cpu,pc,size,unused):
  nonlocal done
  if pc==STOP:done=True;u.emu_stop();return
  if not source:trace[pc]=bytes(u.mem_read(pc,size)).hex()
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
 for reg,value in zip([a.UC_ARM_REG_S0,a.UC_ARM_REG_S1],floats):u.reg_write(reg,value)
 for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],ints):u.reg_write(reg,value)
 symbol,original=ENTRIES[name];u.emu_start((symbols[symbol] if source else original)|1,STOP+2,count=500000);assert done,(source,name,floats,ints,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return {'return':u.reg_read(a.UC_ARM_REG_S0 if name in ['floor','round','ceil','mod','gcd'] else a.UC_ARM_REG_R0),'destination':bytes(u.mem_read(DEST,32)).hex(),'domain':int.from_bytes(u.mem_read(0x20027194,4),'little'),'fp_exceptions':u.reg_read(a.UC_ARM_REG_FPSCR)&0x9f}
rows=[]
def check(name,floats,ints=[]):
 original=run(False,name,floats,ints);source=run(True,name,floats,ints)
 if original!=source:
  args.output.with_suffix('.failure.json').write_text(json.dumps({'name':name,'float_bits':floats,'ints':ints,'stock':original,'source':source},indent=2)+'\n');raise AssertionError((name,floats,ints,original,source))
 rows.append({'name':name,'float_bits':floats,'ints':ints,'result':original})
rng=random.Random(427160);values={0,1,0x7fffff,0x800000,0x3effffff,0x3f000000,0x3f000001,0x3f7fffff,0x3f800000,0x3f800001,0x4affffff,0x4b000000,0x4b7fffff,0x4b800000,0x7f7fffff,0x7f800000,0x7fc12345,0x7f812345}
values|={bits(x) for x in [0.1,0.49,0.5,0.51,1.5,2.5,10,63,96,240,960]};values|={rng.getrandbits(31) for _ in range(100)};values|={v|0x80000000 for v in list(values)}
for name in ['floor','round','ceil']:
 for value in sorted(values):check(name,[value])
for x in sorted(values):
 for y in [0,1,0x7fffff,0x800000,0x3f800000,0x40000000,0x7f800000,0x7fc12345,0x80000000,0xbf800000]:check('mod',[x,y])
for reference in [0,0.1,1,10,12,12.000001,24,32.768,48,63,960]:
 for target in [0,0.1,1,4,10,59.999996,60,60.000004,96,239.99998,240,240.00002,960,960.00006,1000]:
  fs=[bits(reference),bits(target)];check('gcd',fs);check('integer',fs,[DEST,DEST+2]);check('fraction',fs,[DEST,DEST+2,DEST+4]);check('vco',fs,[DEST])
for reference,target in [(0x7f800000,bits(240)),(bits(12),0x7f800000),(0x7fc12345,bits(240)),(bits(12),0x7fc12345),(0x7f812345,bits(240)),(bits(12),0x7f812345),(bits(-12),bits(240)),(bits(12),bits(-240))]:
 for name in ['gcd','integer','fraction','vco']:
  ptrs=[] if name=='gcd' else [DEST] if name=='vco' else [DEST,DEST+2] if name=='integer' else [DEST,DEST+2,DEST+4]
  check(name,[reference,target],ptrs)
for target in [60,240,960]:check('vco',[bits(12),bits(target)],[0])
for reference in [0,32768,10000000,12000000,12000001,24000000,48000000,0xffffffff]:
 for target in [0,1,1000000,12000000,48000000,60000000,96000000,196608000,240000000,250000000,960000000,0xffffffff]:
  check('pll',[],[DEST,reference,target])
  for minimum in [60000000,240000000]:check('min',[],[DEST,reference,target,minimum])
files=['clock_generators.c','clock_generators.h','clock_pll_math.c','clock_pll_mod.c','clock_pll_rounding.c'];out={'status':'PASS','cases':len(rows),'case_counts':dict(collections.Counter(r['name'] for r in rows)),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_hashes':{name:hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks'/name).read_bytes()).hexdigest() for name in files},'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(k):v for k,v in sorted(trace.items())},'limits':['Original bytes execute for all descendants; source executes ELF only, no child models or stock code fallback.','Unicorn A15 synthetic SRAM, FPSCR starts0. Floating status compare exception bits0x9f; final comparison NZCV flags are not API results.','No hardware clock/PLL lock/timing or byte equality certified. No SRAM-write recorder.']};args.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),out['case_counts'])
