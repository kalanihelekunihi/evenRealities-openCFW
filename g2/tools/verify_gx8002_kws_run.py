# SPDX-License-Identifier: MIT
"""KWS runner decoded traces versus explicit feature-window/task oracle."""
import json,subprocess
from itertools import product
from build_gx8002_kws_run_candidate import build,ROOT,sha
from execute_gx8002_kws_run import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA
MASK=0xffffffff

def expected(context,index,stride,features,output,dimension,seed):
    if not context:return MASK,[]
    incoming=(stride*40*2)&MASK;keep=((13-stride)*40*2)&MASK
    task=[(seed+i)&MASK for i in range(8)];task[3]=features&0xfffffff;task[4]=output&0xfffffff
    return 0,[('LvpGetFeatsBuffer',),('LvpGetLogfbankBuffer',context,index),('LvpGetPcmFrameNumPerContext',),
        ('gx_dcache_invalid_range',0x20041000,incoming),('memmove',0x20040000,(0x20040000+incoming)&MASK,keep),
        ('memcpy',(0x20040000+keep)&MASK,0x20041000,incoming),('memcpy',0x20050000,0x20040000,1040),
        ('gx_dcache_clean_range',0x20050000,1040),('LvpGetContext',index),('LvpGetContext',(index+1)&MASK),
        ('LvpCTCModelInitSnpuTask',),('LvpCTCModelGetSnpuFeatsBuffer',0x20052000),('LvpCTCModelGetSnpuStateBuffer',0x20054000),
        ('LvpCTCModelGetSnpuFeatsDim',),('gx_dcache_clean_range',features,(dimension*2)&MASK),
        ('gx_snpu_run_task',tuple(task),0x100260d0,0x20053000)]

def verify():
    candidate=build();directory=ROOT/'build/gx8002-board';path=directory/'padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x180f8','--stop-address=0x181c0',str(path)],text=True));new=decode((directory/'kws-run.disassembly.txt').read_text());cases=0
    for context,index,stride,features,output,dimension,seed in product((0,0x20030000),(0,1,MASK),(0,1,12,13,14,0x80000000,MASK),(0x20058000,MASK),(0x20059000,0xf1234567),(0,520,0x80000000,MASK),(0,91)):
        args=(context,index,stride,features,output,dimension,seed);wanted=expected(*args)
        assert execute(old,0x180f8,candidate['bindings'],*args)==execute(new,0x100260e4,candidate['bindings'],*args)==wanted
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source argument sequence, unsigned window arithmetic, context wrap, task address masking, preserved task fields, null return and ABI checked against independent oracle. Buffer/cache/context/task helpers modeled; oversized transfer arithmetic tested without executing invalid memory transfers. Real data movement and hardware pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
