#!/usr/bin/env python3
"""Compare separate CASE HAL tick getter against original."""
from pathlib import Path
import argparse,hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/tick_word_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__tick_word_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'tick_word.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
elfpath=H/'tick_word.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_tick_word2',str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_tick_word2')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(original,value):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:]);u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000120,struct.pack('<I',value))
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x20000001)
    u.emu_start(0x08004ead if original else entry|1,0x20000000,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000000
    return u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK)
values=[0,1,2,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
for v in values:assert run(True,v)==run(False,v),hex(v)
rec={'status':'PASS','cases':len(values),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'values':[hex(v) for v in values],
     'limits':['Synthetic RAM word values; no HAL tick cadence or clock initialization proof.']}
(H/('tick_word_archive_results.json' if a.archive_object else 'tick_word_results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(values)}))
