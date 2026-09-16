# SPDX-License-Identifier: MIT
"""Authenticate image-specific vector-to-IRQ-table routing."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def code(a,b):return decode(subprocess.check_output([tool,'-D',f'--start-address={a:#x}',f'--stop-address={b:#x}',str(wrapper)],text=True))
    startup=code(0x3bae4,0x3bb1e)
    assert startup[0x3bae4][:2]==('lrw','r3, 0x10003000')
    assert startup[0x3bae6][:2]==('mtcr','r3, cr<1, 0>')
    assert startup[0x3bb18][:2]==('psrset','ee, ie')
    routes=[]
    for name,vector,handler,entry,table in [('boot',0x2850,0x10003124,0x3174,0x2000984c),('backup',0x3b940,0x10004880,0x3d1c0,0x200173a8)]:
        words=[int.from_bytes(stock[vector+4*i:vector+4*i+4],'little') for i in range(32,64)]
        assert words==[handler]*32
        body=code(entry,entry+80)
        loads=[pc for pc,(op,args,width) in body.items() if op=='lrw' and int(args.split(',')[-1],0)==table]
        assert len(loads)==1
        routes.append({'image':name,'vector_package_offset':vector,'external_vector_count':32,'handler_runtime':handler,'handler_package_offset':entry,'table_literal_reader':loads[0],'table_base':table})
    assert routes[0]['table_base']+256<=routes[1]['table_base']
    return {'stock_sha256':IMAGE_SHA,'routes':routes,'backup_vector_base_write':0x3bae6,'backup_interrupt_enable':0x3bb18,'source_admitted':False,'limits':['Authenticates both vector tables and dispatcher table literals plus backup startup ordering. Establishes routing after the observed backup initialization path. Does not execute complete boot-to-backup handoff, qualify pending-interrupt timing, or prove that all transitions follow this path.']}


if __name__=='__main__':
    result=analyze();(ROOT/'docs/research/gx8002-irq-image-dispatch.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Two image-specific vector/table routes authenticated')
