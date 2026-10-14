from pathlib import Path
import json,struct,hashlib,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';raw=F.read_bytes()[32:];cat=list(map(json.loads,(R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()));E=H/'switch-fixture.elf';cmd=json.loads((B/'case-wave065-dma-cancel-call-types/final/receipt.json').read_text())['link_command'].copy();cmd.insert(1,'-ucase_boot_jump_table_dispatch_9190');cmd[-1]=str(E);subprocess.run(cmd,check=True)
with E.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def bl(p):
 a,b=struct.unpack_from('<HH',raw,p-0x8000000)
 if a&0xf800!=0xf000 or b&0xd000!=0xd000:return None
 s=(a>>10)&1;v=(s<<24)|((1^((b>>13)&1)^s)<<23)|((1^((b>>11)&1)^s)<<22)|((a&1023)<<12)|((b&2047)<<1);return p+4+v-(1<<25 if s else 0)
tables=[];pairs=[]
for fn in cat:
 lo=int(fn['body_start'],16);hi=int(fn['body_end_inclusive'],16)+1
 for pc in range(lo,hi-3,2):
  if bl(pc)!=0x8009190:continue
  start=pc+4;count=raw[start-0x8000000];size=count+2;data=raw[start-0x8000000:start+size-0x8000000];targets=sorted(set((start+1+2*v)&~1 for v in data[1:]));assert all(lo<=a<hi for a in targets)
  table=dict(function_entry=fn['entry'],BL_PC=hex(pc),data_span=[hex(start),hex(start+size)],data_hex=data.hex(),default_max_index=count,case_targets=list(map(hex,targets)));tables.append(table)
  # Original compact-table bytes copied only as RAM fixture input data.
  for selector in list(range(count+1))+[255,256,0xffffffff]:
   results=[]
   for source in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000)
    if source:
     for a,d in segs:u.mem_write(a,d)
    else:u.mem_write(0x8000000,raw)
    table_base=0x20008000;u.mem_write(table_base,data);lr=table_base+1;target=(lr+2*data[1+min(selector,count)])&~1
    regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R4,UC_ARM_REG_R5];values=[0xa5a50000+i for i in range(len(regs))]
    for reg,v in zip(regs,values):u.reg_write(reg,v)
    u.reg_write(UC_ARM_REG_R3,selector);u.reg_write(UC_ARM_REG_LR,lr);u.reg_write(UC_ARM_REG_SP,0x20002c88)
    def hook(uc,address,size,user):
     if address==target:uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(syms['case_boot_jump_table_dispatch_9190'] if source else 0x8009191,0,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==target;assert [u.reg_read(r) for r in regs]==values;assert u.reg_read(UC_ARM_REG_R3)==target|1;assert u.reg_read(UC_ARM_REG_SP)==0x20002c88
    results.append(dict(PC=hex(target),R3=hex(u.reg_read(UC_ARM_REG_R3)),argument_and_saved_registers_unchanged=True,SP_restored=True))
   assert results[0]==results[1];pairs.append(dict(BL_PC=hex(pc),selector=selector,result=results[0]))
r=dict(status='PASS_REAL_NATIVE_SOURCE_SWITCH_HELPER_TABLE_PAIRS',tables=tables,cases=len(pairs),comparisons=pairs,fixture_ELF_sha256=hashlib.sha256(E.read_bytes()).hexdigest(),link_command=cmd,limits=['Recognized ARM compact inline tables only, rawBL matches within catalogue extents; actual helper bodies verify unsignedcapping/target/registers','Copied table bytes are input data inRAM fixture; computed target cut occurs before case body, no provider stubs','Source fixture retains real naked helper absent fromproduction reachablegraph; not a new production loader or executableblob','No claim fullCASECFG/branchfeasibility or hardwarestate'])
(H/'switch-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(tables),len(pairs))
