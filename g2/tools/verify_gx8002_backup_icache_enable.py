# SPDX-License-Identifier: MIT
"""Compare backup instruction-cache controller traces, including continued polling."""
import itertools,json,subprocess
from build_gx8002_backup_icache_enable import build,ROOT,Elf32,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_icache_source import execute


def normalize(code,entry):
    return {pc-entry:(width,op,hex(int(args,0)-entry) if op=='bt' else args) for pc,(op,args,width) in code.items()}


def verify():
    build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=normalize(decode(subprocess.check_output([pre,'-D','--start-address=0x3d8ec','--stop-address=0x3d90c',str(wrapper)],text=True)),0x3d8ec)
    new=normalize(decode((ROOT/'build/gx8002-backup-icache-enable/device.disassembly.txt').read_text()),0x10004fac)
    count=0
    sequences=[[],[2],[0,1,3,2],[0,1,3],[0xffffffff]*8,[0xfffffffe],[4,5,7,6]]
    sequences += [list(x) for x in itertools.product(range(4),repeat=3)]
    for control,statuses in itertools.product((0,1,0x80000000,0xffffffff),sequences):
        trace=[('write32',0xb0000000,0),('read32',0xb0000000,control),('write32',0xb0000000,control|1)]
        state='polling'
        for status in statuses:
            trace.append(('read32',0xb0000004,status))
            if status&3==2:state='returned';break
        assert execute(old,control,statuses)==execute(new,control,statuses)==(state,trace)
        count+=1
    report={'cases':count,'differences':0,'limits':['Finite MMIO status sequences cover both return and continued polling. Hardware readiness/coherency remains unqualified; no timeout was added.']}
    (ROOT/'docs/research/gx8002-backup-icache-enable-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify())
