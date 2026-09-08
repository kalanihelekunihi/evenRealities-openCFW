#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Resolve authenticated host-model PC-relative dispatch entries; inspection only."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def analyze():
    inventory=json.loads((ROOT/'docs/research/gx8002-gxdnn-cmodel-inventory.json').read_text())
    member=next(m for m in inventory['members'] if m['name']=='calc.o')
    obj=ROOT/'build/gxdnn-analysis/calc.o'
    if hashlib.sha256(obj.read_bytes()).hexdigest()!=member['sha256']:raise ValueError('calc object authentication')
    rel=subprocess.check_output(['xcrun','llvm-objdump','--reloc',str(obj)],text=True)
    table=rel.split('RELOCATION RECORDS FOR [.rodata.choose_calc_func]:')[1].split('RELOCATION RECORDS FOR')[0]
    code=rel.split('RELOCATION RECORDS FOR [.text.choose_calc_func]:')[1].split('RELOCATION RECORDS FOR')[0]
    functions={int(off,16)-3:name for off,name in re.findall(r'([0-9a-f]{16}) R_X86_64_PC32\s+\.text\.calc_(\w+)-0x4',code)}
    rows=[]
    for off,addend in re.findall(r'([0-9a-f]{16}) R_X86_64_PC32\s+\.text\.choose_calc_func\+0x([0-9a-f]+)',table):
        entry=int(off,16);target=int(addend,16)-entry
        if target not in functions:raise ValueError('unknown arithmetic target')
        rows.append({'selector':entry//4,'table_offset':entry,'relocation_addend':int(addend,16),'target_offset':target,'operation':functions[target]})
    if [r['selector'] for r in rows]!=list(range(7)):raise ValueError('incomplete dispatch')
    return {'upstream_commit':inventory['commit'],'object_sha256':member['sha256'],'dispatch':rows,'source_admitted':False,'limits':['Host reference dispatch only. Numerical precision and hardware behavior remain unqualified. No object bytes used in firmware.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-gxdnn-arithmetic-dispatch.json').write_text(json.dumps(r,indent=2)+'\n');print(r['dispatch'])
