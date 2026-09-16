# SPDX-License-Identifier: MIT
"""First complete general-path execution; not broad power qualification."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from gx8002_binary32_rational import operation

def verify():
    path=ROOT/'build/gx8002-powf-placed/power.elf'
    report=json.loads((ROOT/'docs/research/gx8002-powf-placed.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256']
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    trace={pc:[] for pc in code}
    result=execute(code,0x100100bc,bytes(20),float_arguments=[0x3fc00000,0x40400000]+[0]*14,return_float=True,float_operation=operation,trace=trace)
    assert result==0x40580000
    ops=sorted({code[pc][0] for pc,visits in trace.items() if visits})
    result={'elf_sha256':report['elf_sha256'],'cases':1,'input_bits':['0x3fc00000','0x40400000'],'expected_bits':'0x40580000','executed_opcodes':ops,'source_admitted':False,'limits':['Single exact 1.5 cubed sample through compiled approximation. Explicit nearest-even finite arithmetic; accumulates use separate multiply/add rounding. Stock comparison, broad accuracy, nonfinite handling, hardware FP semantics and integration pending.']}
    (ROOT/'docs/research/gx8002-powf-general-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
