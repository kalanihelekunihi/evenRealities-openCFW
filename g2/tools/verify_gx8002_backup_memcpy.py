# SPDX-License-Identifier: MIT
"""Rebuild backup RAM copy and compare complete memory access sequences."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import COPY_FLAGS,decode,execute

def verify():
    out=ROOT/'build/gx8002-backup-memcpy';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_memcpy.c';obj=out/'copy.o';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*COPY_FLAGS,'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    address=0x49c84-0x3b940+0x10003000
    ld=out/'copy.ld';ld.write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text.open_cfw_gx8002_memcpy) }} }}\nASSERT(SIZEOF(.text) <= 128,"copy overflow")\n')
    path=out/'copy.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'copy');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    section=next(s for s in elf.sections if s['name']=='.text')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([pre+'objdump','-d',str(path)],text=True));old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x49c84','--stop-address=0x49d04',str(wrapper)],text=True));cases=0
    for sa in range(4):
        for da in range(4):
            for size in range(258):
                src,dst=0x1000+sa,0x3000+da
                initial={src+i:(i*73+19)%256 for i in range(size)}
                initial.update({dst+i:0xa5 for i in range(-4,size+4)})
                memory=initial.copy();original=initial.copy();accesses=[];old_accesses=[]
                ret,_=execute(code,memory,dst,src,size,address,accesses=accesses)
                old_ret,_=execute(old,original,dst,src,size,0x49c84,accesses=old_accesses)
                expected=initial.copy();expected.update({dst+i:initial[src+i] for i in range(size)})
                assert ret==old_ret==dst and memory==original==expected and accesses==old_accesses,(sa,da,size)
                cases+=1
    result={'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'command':command,'bytes':section['size'],'package_offset':0x49c84,'cases':cases,'source_admitted':False,'limits':['Nonoverlapping RAM; exact source/stock access widths and order, byte results and guards. Caller coverage, integration and hardware/timing pending.']}
    (ROOT/'docs/research/gx8002-backup-memcpy-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
