#!/usr/bin/env python3
"""Native/source battery client with real divide and genuine query API inputs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
import json,hashlib,random,struct,argparse
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;A=argparse.ArgumentParser();A.add_argument('--profile',default='qualified');args=A.parse_args();elf=H/(args.profile+'-measurement.elf');fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
assert sym['case_boot_battery_percent']!=sym['case_init_read_product_byte'];rng=random.Random(0x9ebc);raws=[0,1,2,255,256,257,25343,25344,25345,25599,25600,65534,65535]+[rng.randrange(65536) for _ in range(256)];inputs=[(v,0) for v in raws]+[(0,s) for s in [1,2,0xffffffff]];rows=[]
for name in ['case_boot_battery_percent','case_init_read_product_byte']:
 for raw,status in inputs:
  pair=[]
  for native in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
   if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
   else:
    for a,b in segs:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20004000,struct.pack('<I',0xdeadbeef));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001);seen=[]
   def hook(uc,address,size,data):
    if address!=(0x0800a074 if native else sym['case_policy_timer_query']&~1):return
    assert uc.reg_read(UC_ARM_REG_R0)==4;ptr=uc.reg_read(UC_ARM_REG_R1);assert ptr%4==0 and 0x20007000<=ptr<0x20008000;assert bytes(uc.mem_read(ptr,4))==bytes(4);seen.append({'query_register':4,'raw':raw,'status':status})
    if status==0:uc.mem_write(ptr,struct.pack('<I',raw))
    uc.reg_write(UC_ARM_REG_R0,status);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08009ebc if native else sym[name])|1,0x2000f000,count=10000);assert seen and u.reg_read(UC_ARM_REG_PC)==0x2000f000 and u.reg_read(UC_ARM_REG_SP)==0x20008000;pair.append((u.reg_read(UC_ARM_REG_R0),struct.unpack('<I',bytes(u.mem_read(0x20004000,4)))[0],seen))
  if pair[0]!=pair[1]:
   r={'status':'FAIL_QUERY_CLIENT_CONTRACT','profile':args.profile,'symbol':name,'raw':raw,'query_status':status,'native':pair[0],'source':pair[1],'note':'Nonzero query statuses are counterfactual interface fault injections, not a claim nativequery can produce them.','ELF_sha256':sha(elf)};(H/(args.profile+'-failure.json')).write_text(json.dumps(r,indent=2)+'\n');raise AssertionError(r)
  rows.append({'symbol':name,'raw':raw,'query_status':status,'return':pair[0][0],'output':pair[0][1],'counterfactual_fault_injection':status!=0})
r={'status':'PASS_NATIVE_C_BATTERY_CLIENT_ABI_AND_DIVISION','cases':len(rows),'query_success_cases':sum(x['query_status']==0 for x in rows),'counterfactual_fault_injection_cases':sum(x['query_status']!=0 for x in rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'actual_divide_executed':True,'genuine_query_entry_controlled':True,'limits':['Controlled data/status at genuine query API entry; querybody/sensor effects not executed or validated. Actual native/source unsigneddivide andclient conversion execute.','Native guardedstatus wrapperA130 alwaysreturns0, so nonzero cases are explicit counterfactual interfacefault tests, not reachablehardwarecoverage.','Full graph includes realquery/divide providers, no firmware stubs; additionalroots retain actualclient entry names for modulefixture only.']};(H/'measurement-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
