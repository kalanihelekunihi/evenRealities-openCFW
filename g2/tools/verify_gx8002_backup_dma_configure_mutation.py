# SPDX-License-Identifier: MIT
"""Check backup configuration base/list reloads across modeled helpers."""
import json, subprocess
from itertools import product
from build_gx8002_backup_dma_configure import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_backup_dma_configure import execute


def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d314','--stop-address=0x3d4ac',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-configure/configure.disassembly.txt').read_text())
    cases=0;state=0x2002d3e8
    for channel,length,width,mutate in product((0,1),(1,4096,69616),(0,1,2,7),(False,True)):
        fields=[1,3,1,6,0,0,4,0,0,0,0,2]
        def run(code,entry,helpers):
            calls=[]
            def mutation(kind,put):
                calls.append(kind)
                if not mutate:return
                if kind=='bus':
                    count=calls.count('bus')
                    put(state,{1:0xa1001000,2:0xa1002000,3:0xa1004000}[count])
                    if count==1:put(0x20040000,width)
                else:
                    put(state,0xa1003000)
                    put(state+872+channel*4,0x20061000)
            result=execute(code,entry,fields,length,channel,state_address=state,
                           helper_addresses=helpers,mutation_hook=mutation)
            return result,calls
        a=run(old,0x3d314,{0x3db04:0x10203c60,0x3d210:0x10203828})
        b=run(new,0x100049d4,{0x100051c4:0x10203c60,0x100048d0:0x10203828})
        assert a==b
        (result,trace),calls=a;rejected=length==69616;offset=channel*88
        assert result==(0xffffffff if rejected else 0)
        assert calls==(['bus','bus'] if rejected else ['bus','bus','descriptors','bus'])
        control=0x18000001|(4<<11)|(3<<14)|(1<<1)|(1<<4)|(1<<10)|(2<<20)
        writes=[('write',0xa1000000+o,1<<channel) for o in (0x338,0x340,0x348,0x350,0x358)]
        second=0xa1001000 if mutate else 0xa1000000
        latest=0xa1002000 if mutate else 0xa1000000
        writes += [('write',0xa1000000+offset,0xa0000000),('write',second+offset+8,0x50000),
                   ('write',latest+offset+24,control),('write',latest+offset+64,0),('write',latest+offset+68,(6<<7)|2)]
        if not rejected:
            writes += [('write',(0xa1003000 if mutate else 0xa1000000)+offset+16,0x61000 if mutate else 0x60000)]
            descriptor=next(row for row in trace if row[0]=='descriptors')
            assert descriptor[4]==(1<<(width if mutate else 1))&255
        assert [row for row in trace if row[0]=='write']==writes
        cases+=1
    report={'candidate':candidate,'mutation_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Modeled helpers mutate base, list pointer and configuration width; ordered stock/source traces and independent MMIO expectations checked.',
                      'No physical concurrency claim; loader, references and source admission remain separate.']}
    (ROOT/'docs/research/gx8002-backup-dma-configure-mutation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(verify()['mutation_cases'],'mutation cases passed')
