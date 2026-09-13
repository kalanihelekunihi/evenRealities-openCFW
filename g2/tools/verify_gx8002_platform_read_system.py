# SPDX-License-Identifier: MIT
"""Decoded startup consumes actual getter writes to its local record."""
import json,struct,subprocess
from itertools import product
from compare_gx8002_platform_read import verify as qualify,execute as getter,oracle,ROOT,Elf32,decode
from execute_gx8002_system_getter import execute as system,SYMBOLS
from gx8002_lvp_system_oracle import expected
from analyze_gx8002_upstream_objects import sha

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-system-initialize/buffers.elf';elf=Elf32(path.read_bytes(),'system');report_path=ROOT/'docs/research/gx8002-lvp-system-initialize-source-verification.json';report=json.loads(report_path.read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));directory=ROOT/'build/gx8002-board'
    getcode=decode((directory/'platform-read-linked.disassembly.txt').read_text());linked=Elf32((directory/'platform-read.elf').read_bytes(),'getter');section=next(s for s in linked.sections if s['name']=='.rodata.platform_read');table=struct.unpack('<10I',linked.contents(section));cases=0;total=0
    for mode,control,trim,seed in product((0,1,2,0xffffffff),(0,2),(0,3,11,255),(0,1,91)):
        calls=[]
        def run(operation,record,memory,config):
            assert operation==8 and record==0x2006fff0
            trace=oracle(operation,{0xa0000038:config},record)
            def write(address,bits,value):
                assert address==record and bits==32
                for i in range(4):memory[address+i]=(value>>(i*8))&255
            result=getter(getcode,0x10024810,0,table,operation,trace,record,write_hook=write)
            calls.append(trace);return result
        actual=system(code,0x102078a4,mode,0x854012,control,trim,seed,getter_runner=run)
        wanted=expected(SYMBOLS,mode,0x854012,control,trim,seed)
        assert actual==wanted
        assert len(calls)==sum(event==('gx_pmu_ctrl_get',8) for event in wanted[0])
        total+=len(calls);cases+=1
    assert total>0
    return {'evidence':evidence,'system_cases':cases,'decoded_getter_calls':total,'system_elf_sha256':sha(path.read_bytes()),'system_report_sha256':sha(report_path.read_bytes()),'source_admitted':False,'limits':['Actual decoded getter stores feed caller local memory and subsequent startup choices; register read value scripted. Other startup helpers modeled; no physical startup qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-platform-read-system.json').write_text(json.dumps(r,indent=2)+'\n');print(r['system_cases'],r['decoded_getter_calls'])
