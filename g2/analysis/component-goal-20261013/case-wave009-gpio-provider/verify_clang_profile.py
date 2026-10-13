#!/usr/bin/env python3
"""Bounded CASE layout, CRT and stock/source formatter qualification."""
from pathlib import Path
import hashlib,json,re,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_CPU_ARM_CORTEX_M0
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
elf=HERE/'selective/case.elf';fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';payload=fw.read_bytes()[32:]
with elf.open('rb') as f:
 e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data(),s['p_memsz']) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=e.header['e_entry'];v=e.get_section_by_name('.isr_vector').data()
undefined=subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True);assert not undefined.strip(),undefined
roots=json.loads((ROOT/'g2/analysis/c-source-completion-20261011/m0/case_semantic_corrected_optimized.indirect-roots.json').read_text());assert all(x['source_symbol'] in symbols for x in roots['rows'])
assert len(v)==184 and struct.unpack_from('<II',v)==(0x20002c88,0x08000145) and entry==0x08000145
expected={2:'case_vector_nmi_6d70',3:'case_vector_hardfault_6778',11:'case_vector_svc_6e18',14:'case_vector_pendsv_0102',15:'case_vector_systick_8420',18:'case_vector_irq_6e08',21:'case_vector_irq_3bc8',22:'case_vector_irq_3c2c',23:'case_vector_irq_3d24',28:'case_vector_irq_06c4',38:'case_vector_irq_84b0',43:'case_vector_irq_8f98'}
for i,name in expected.items():assert struct.unpack_from('<I',v,i*4)[0]==symbols[name]|1
# Execute the final-profile CRT initializer against the independently decoded
# authenticated compressed initial-state stream; no patched product values.
compressed=payload[0xd95c:0xd95c+104];decoded=bytearray();p=0
while len(decoded)<420:
 h=compressed[p];p+=1;copy=h&15;clear=h>>4
 if copy==0:copy=compressed[p];p+=1
 if clear==0:clear=compressed[p];p+=1
 decoded+=compressed[p:p+copy-1];p+=copy-1;decoded+=bytes(clear-1)
assert p==104 and len(decoded)==420 and hashlib.sha256(decoded).hexdigest()=='d91efcf9f5409364aa0e3791d1084418682e76414c5a7b588c3c484daa0dd89a'
span=max(a+max(len(b),m) for a,b,m in segments)-0x08000000;mapped=(span+4095)&~4095;crt=[]
for fill in [0,0xa5,255]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,mapped)
 for a,b,m in segments:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes([fill])*420);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.emu_start(symbols['case_crt_init_known_defaults']|1,0x20008000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x20008000 and bytes(u.mem_read(0x20000000,420))==bytes(decoded);crt.append(fill)
# Reuse the full stock/source grammar corpus, replacing only standalone build
# setup and source memory loading so native instructions cannot be overwritten.
harness=ROOT/'g2/analysis/c-source-completion-20261011/m0/verify_vformat_basic.py';s=harness.read_text();start=s.index("obj = HERE / 'vformat_candidate.o'");end=s.index("with elf.open('rb') as stream:",start);s=s[:start]+"elf = CANDIDATE_ELF\n"+s[end:]
s=s.replace("u.mem_map(0x08000000, (len(firmware[32:])+4095)&~4095)","u.mem_map(0x08000000, SOURCE_MAPPING)")
s=s.replace('for address, data in segments: u.mem_write(address, data)','for address, data in segments:\n            if not original: u.mem_write(address, data)')
ns={'__file__':str(harness),'CANDIDATE_ELF':elf,'SOURCE_MAPPING':max(mapped,(len(payload)+4095)&~4095)};exec(compile(s,str(harness),'exec'),ns)
result={'status':'PASS_BOUNDED_CASE_SOURCE_PROFILE','elf_sha256':sha(elf),'firmware_sha256':sha(fw),'stock_payload_bytes':len(payload),'source_load_span_bytes':span,'difference_from_stock':span-len(payload),'known_native_pointer_roots_present':39,'vector_words':46,'typed_vector_entries':14,'reset_entry':hex(entry),'CRT_bytes':420,'CRT_initial_fill_cases':crt,'formatter_native_C_cases':len(ns['cases']),'source_format_count':len(ns['actual_formats']),'native_caller_format_count':len(ns['native_caller_formats']),'harness_sha256':sha(harness),'undefined_symbols':[],'limits':['Known39 roots and14 vector entries, not full computed-pointer or native-body coverage.','Different compiler/optimized layout requires full ambient stack, ABI and peripheral qualification; bounded tests are not firmware-ready.','No stock package equality, hardware execution or workflow G2-G6 promotion.']}
(HERE/'selective/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','source_load_span_bytes','difference_from_stock','formatter_native_C_cases']}))
