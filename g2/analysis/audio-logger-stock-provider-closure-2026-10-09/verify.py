from pathlib import Path
import json,subprocess,itertools,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];G='/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-nm';syms={line.split()[2]:int(line.split()[0],16) for line in subprocess.check_output([G,str(elf)],text=True).splitlines() if len(line.split())==3};sections=[]
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
bind={'am_hal_delay_us_status_change':0x4807fc,'am_hal_debug_disable':0x4d3f78,'am_hal_debug_power':0x4d3fc2,'am_hal_debug_trace_disable':0x4d403e,'am_hal_itm_disable':0x539254,'am_hal_itm_tpiu_pipeline_flush':0x53928c,'am_hal_itm_not_busy':0x5392ae,'am_hal_itm_stimulus_not_busy':0x5392d4,'am_hal_itm_print_not_busy':0x5392f8,'am_hal_tpiu_disable':0x539304,'logger_top':0x4c2b30}
def run(name,fixture,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40010000,0x1000);u.mem_map(0xe0000000,0x10000)
 u.mem_write(0x20074f5c,bytes(fixture.get('debug',[0,0,0,0])));u.mem_write(0x20074f7d,bytes(fixture.get('tpiu',[1,1])));u.mem_write(0x40020250,fixture.get('dbgctrl',0xffffffff).to_bytes(4,'little'));u.mem_write(0xe000edfc,fixture.get('demcr',0x1000001).to_bytes(4,'little'));u.mem_write(0xe0000e80,fixture.get('tcr',0x11).to_bytes(4,'little'));u.mem_write(0xe0000000,fixture.get('port',1).to_bytes(4,'little'));u.mem_write(0x20040000,fixture.get('register',0).to_bytes(4,'little'))
 u.mem_write(0x20074f4e,bytes([fixture.get('flag',1)]));u.mem_write(0x200742f0,(0x12345679).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_PRIMASK,fixture.get('primask',0))
 for reg,arg in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],fixture.get('args',[])):u.reg_write(reg,arg)
 calls=[];done=[];nativepcs=set()
 def hook(uc,pc,size,user):
  if name=='logger_top' and native and pc in (0x539254,0x539304,0x480f0c):
   target={0x539254:'am_hal_itm_disable',0x539304:'am_hal_tpiu_disable',0x480f0c:'am_hal_gpio_pinconfig'}[pc];uc.reg_write(UC_ARM_REG_PC,syms[target]|1);return
  if pc in (0x4807a0,0x47f7ae,0x47f5b8,0x47f90c):
   arg=uc.reg_read(UC_ARM_REG_R0);calls.append((hex(pc),arg))
   if pc==0x47f90c:uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes([fixture.get('enabled',0)]))
   if pc==0x4807a0 and fixture.get('change_after')==sum(c[0]=='0x4807a0' for c in calls):uc.mem_write(0x20040000,fixture.get('change_value',1).to_bytes(4,'little'))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc in (0x10ff00,0x4c2b44,0x4c2b4e):done.append(hex(pc));uc.emu_stop();return
  if native and not(name=='logger_top' and (0x4c2b30<=pc<0x4c2b68 or 0x472c7c<=pc<0x472c84)):
   assert 0x100000<=pc<0x101000,hex(pc);nativepcs.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((syms[name] if native and name!='logger_top' else bind[name])|1,0,count=200000)
 assert done,(name,fixture,native)
 return {'stop':done,'callback':bytes(u.mem_read(0x200742f0,4)).hex(),'flag':u.mem_read(0x20074f4e,1)[0],'pin28':bytes(u.mem_read(0x40010070,4)).hex(),'padkey':bytes(u.mem_read(0x40010400,4)).hex(),'return':u.reg_read(UC_ARM_REG_R0),'debug':bytes(u.mem_read(0x20074f5c,4)).hex(),'tpiu':bytes(u.mem_read(0x20074f7d,2)).hex(),'dbgctrl':bytes(u.mem_read(0x40020250,4)).hex(),'demcr':bytes(u.mem_read(0xe000edfc,4)).hex(),'tcr':bytes(u.mem_read(0xe0000e80,4)).hex(),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'calls':calls},nativepcs
cases=[]
for budget,mask,reg,val in itertools.product([0,1,2,10],[0,1,3],[0,1,3],[0,1]):cases.append(('am_hal_delay_us_status_change',{'args':[budget,0x20040000,mask,val],'register':reg}))
for budget,at in itertools.product([1,2,10],[1,2,3]):cases.append(('am_hal_delay_us_status_change',{'args':[budget,0x20040000,1,1],'change_after':at}))
for name in ['am_hal_debug_disable','am_hal_debug_trace_disable','am_hal_tpiu_disable']:
 for c,power,state,mask in itertools.product([0,1,2,255],[0,1,2],[0,1,3],[0,1]):cases.append((name,{'debug':[c,power,c,state],'tpiu':[1,c],'primask':mask}))
for direction,count,state,enabled,mask in itertools.product([0,1],[0,1,2,255],[0,1,3],[0,1],[0,1]):cases.append(('am_hal_debug_power',{'args':[direction],'debug':[0,count,0,state],'enabled':enabled,'primask':mask}))
for name in ['am_hal_itm_disable','am_hal_itm_tpiu_pipeline_flush','am_hal_itm_not_busy','am_hal_itm_stimulus_not_busy','am_hal_itm_print_not_busy']:
 for port,tcr,refs in itertools.product([0,1,2,3],[0,0x11,0x800011],[0,1,2]):cases.append((name,{'port':port,'tcr':tcr,'debug':[refs,refs,refs,1],'args':[0]}))
for refs,tpiurefs,state,flag,mask in itertools.product([0,1,2],[0,1,2],[0,1,3],[0,1],[0,1]):cases.append(('logger_top',{'debug':[refs,refs,refs,state],'tpiu':[1,tpiurefs],'flag':flag,'primask':mask}))
rows=[];pcs=set()
for name,fixture in cases:
 a,_=run(name,fixture,False);b,reached=run(name,fixture,True)
 assert a==b,(name,fixture,a,b)
 rows.append({'function':name,'fixture':fixture,'observed':a});pcs|=reached
out={'status':'PASS','cases':len(rows),'direct_provider_cases':sum(r['function']!='logger_top' for r in rows),'top_composition_cases':sum(r['function']=='logger_top' for r in rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'reached_native_addresses':sorted(map(hex,pcs)),'comparisons':rows,'limits':'Actual original instructions vs unchanged selected SDK source text under fixed-layout adapter. Delay and peripheral power providers synthetic return/query stubs; synthetic MMIO and reference-count states. No exception delivery, elapsed time, hardware drain or installed sink proof.'}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),'nativePCs',len(pcs))
