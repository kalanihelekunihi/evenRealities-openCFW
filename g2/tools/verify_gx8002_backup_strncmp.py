# SPDX-License-Identifier: MIT
"""Compare reconstructed bounded byte comparison with decoded stock."""
import json,subprocess,random,shutil
from verify_gx8002_logging import check_paths
from itertools import product
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_stage2_libc import execute,base_registers,load_buffer
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    stock=IMAGE.read_bytes()
    assert sha(stock)==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_strncmp.c'
    obj=ROOT/'build/backup-strncmp.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_strncmp');payload=elf.contents(section)
    assert len(payload)<=36 and not elf.relocations(section['index'])
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    wrapped=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(wrapped.contents(next(x for x in wrapped.sections if x['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper mismatch')
    if any(x['size'] and x['flags']&2 and x['name']!=section['name'] for x in elf.sections):raise ValueError('Unaccounted section')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x422d8','--stop-address=0x422fc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode(subprocess.check_output([pre+'objdump','-d',str(obj)],text=True));cases=0
    samples=list(product((b'\0',b'a\0',b'abc\0',b'\xff\0',b'abc'),(b'\0',b'a\0',b'abd\0',b'\x80\0',b'abc'),range(4)))
    samples += [(bytes([a]),bytes([b]),1) for a,b in product(range(256),repeat=2)]
    rng=random.Random(0x422d8)
    for _ in range(500):
        a=bytes(rng.randrange(1,256) for _ in range(rng.randrange(128)))+b'\0'
        b=a if rng.randrange(2) else bytes(rng.randrange(1,256) for _ in range(rng.randrange(128)))+b'\0'
        samples.append((a,b,rng.choice((0,1,2,31,127,128,0xffffffff))))
    samples.append((b'',b'',0))
    for a,b,count in samples:
        memory={};load_buffer(memory,0x20030000,a);load_buffer(memory,0x20040001,b)
        want=0
        for i in range(count):
            want=a[i]-b[i]
            if want or a[i]==0:break
        for code,entry in ((old,0x422d8),(new,0)):
            r=base_registers();r.update(r0=0x20030000,r1=0x20040001,r2=count)
            assert execute(code,entry,r,memory,preserved=(*range(4,12),14,15,16,17))==want&0xffffffff
        cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'strncmp.o')
    row={'symbol':'open_cfw_gx8002_strncmp','section_name':section['name'],'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':'open_cfw_gx8002_strncmp','package_offset':0x422d8,'bytes':36,'sha256':sha(stock[0x422d8:0x422fc]),'region':'backup_sram'}]}
    return {'functions':[row],'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_backup_strncmp.py','verify_gx8002_stage2_libc.py','verify_gx8002_memcpy_source.py')},'cases':cases,'compiled_bytes':len(payload),'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Valid readable buffers; exact byte difference, termination, bound and saved ABI checked. Physical timing and pointer-wrap cases unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-strncmp-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
