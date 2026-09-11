# SPDX-License-Identifier: MIT
"""DMA allocation composed with the existing decoded clock gate."""
import json,subprocess
from itertools import product
import compare_gx8002_platform_gate as gate
from verify_gx8002_dma_select import verify as select_verify,execute,expected,ROOT,decode


def verify():
    selection=select_verify();placement=gate.link();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=gate.IMAGE.read_bytes();table=stock[0x186f4:0x18894]
    old=decode(subprocess.check_output([pre,'-D',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    path=ROOT/'build/gx8002-platform-gate/gate-fit.elf'
    new_gate=decode(subprocess.check_output([pre,'-d',str(path)],text=True));elf=gate.Elf32(path.read_bytes(),str(path))
    jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'))
    new=decode((ROOT/'build/gx8002-dma-select/select.disassembly.txt').read_text());cases=calls=0;samples=[]
    for source,helper,allocation,register in product((False,True),(False,True),([], [0], [1], [1,0], [255,128], [0,0]),(0,0xffffffff,0x55555555)):
        seen=[]
        def hook(module,enable):
            nonlocal calls
            if (module,enable)!=(25,1):raise ValueError('DMA gate arguments')
            trace=gate.execute(new_gate if helper else old,0x10025080 if helper else 0x17094,jumps if helper else stock[0x173e0:0x17474],table,module,enable,register,0 if helper else 0x1000dfec)
            if trace!=gate.oracle(table,module,enable,register):raise ValueError('DMA gate effects')
            seen.append(trace);calls+=1
        actual=execute(new if source else old,0x10203a4c if source else 0xcfd8,allocation,0x80000040,gate_hook=hook)
        if actual!=expected(allocation,0x80000040) or len(seen)!=int(0 in allocation):raise ValueError('DMA composed allocation')
        if seen and len(samples)<3:samples.append(seen[0])
        cases+=1
    return {'selection':selection,'gate_placement':placement,'decoded_cases':cases,'gate_calls':calls,'sample_gate_traces':samples,'source_admitted':False,'hardware_qualified':False,'limits':['Separate gate frame with modeled module lookup and stock configuration table; no physical clock or concurrent allocation qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-select-gate.json').write_text(json.dumps(result,indent=2)+'\n');print('DMA gate cases:',result['decoded_cases'],result['gate_calls'])
