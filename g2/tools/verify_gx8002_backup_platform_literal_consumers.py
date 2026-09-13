# SPDX-License-Identifier: MIT
"""Validate preceding flash routine's literal bindings against generated data."""
import json,subprocess,struct
from build_gx8002_backup_platform_literals import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x4e01c','--stop-address=0x4e08a',str(wrapper)],text=True))
    generated=Elf32((ROOT/'build/gx8002-backup-platform-literals/literals.elf').read_bytes(),'literal source')
    sections={s['name']:s for s in generated.sections};pool=generated.contents(sections['.shared_literals'])
    uses=[]
    for pc,index,reg,target in ((0x4e026,0,'r3',0x20016d80),(0x4e052,1,'r0',0x10012aa4),
                                (0x4e05a,1,'r1',0x10012aa4),(0x4e07e,2,'r0',0x10012a8c)):
        op,args,width=code[pc];assert op=='lrw' and args==reg+', '+hex(target)
        value=struct.unpack_from('<I',pool,index*4)[0];assert value==target
        uses.append({'instruction':pc,'literal_offset':0x4e098+index*4,'value':value})
    assert struct.unpack_from('<I',pool,12)[0]==0x10012a3c
    assert generated.contents(sections['.otp_error'])==b'read flash otp error\n\0'
    assert generated.contents(sections['.otp_model'])==b'8003A\0'
    # Exact strings reproduce length/byte comparison behavior of the retained
    # consumer. This does not execute or qualify its call targets.
    report={'build':evidence,'uses':uses,'source_admitted':False,'hardware_qualified':False,
            'limits':['Four decoded literal loads and source text identity checked; the full flash routine and called helpers are not executed by this check.']}
    (ROOT/'docs/research/gx8002-backup-platform-literal-consumers.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(len(verify()['uses']),'literal consumers checked')
