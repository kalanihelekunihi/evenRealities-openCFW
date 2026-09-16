# SPDX-License-Identifier: MIT
"""Compile and compare complete source divider setup with stock inline calls."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT, FLAGS, IMAGE, IMAGE_SHA, sha, Elf32
from analyze_gx8002_upstream_objects import SDK_COMMIT, authenticated_blob
from verify_gx8002_memcpy_source import decode


def calls(code,start,stop,targets):
    r={};trace=[];pc=start
    for _ in range(100):
        if pc==stop:return trace
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bsr':
            name=targets[int(args,0)];trace.append([name,*[r[f'r{i}'] for i in range(3 if name=='dto' else 2)]]);r.clear()
        elif op=='push':assert args=='r15'
        elif op=='pop':assert args=='r15';return trace
        else:raise ValueError((hex(pc),op,args))
        pc+=width
    raise ValueError('divider call bound')


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-clock-dividers';out.mkdir(exist_ok=True)
    headers=[]
    for rel in ('include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        authenticated_blob(sdk/rel,blob);headers.append({'path':rel,'blob':blob})
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    src=ROOT/'components/shared/gx8002/runtime_gx8002_backup_clock_dividers.c';obj=out/'dividers.o';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-I'+str(out),'-isystem',str(sdk/'include'),'-c',str(src),'-o',str(obj)],check=True)
    ld=out/'dividers.ld';ld.write_text('SECTIONS { .text 0x10018000 : { *(.text*) } }\ngx_clock_set_div = 0x10003788;\ngx_clock_set_dto = 0x100038e8;\n')
    path=out/'dividers.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'dividers');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'dividers.disassembly.txt').write_text(asm)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';original=Elf32(wrapper.read_bytes(),'stock');assert original.contents(next(s for s in original.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3bc8c','--stop-address=0x3bd1a',str(wrapper)],text=True))
    a=calls(old,0x3bc8c,0x3bd1a,{0x3c0c8:'div',0x3c228:'dto'})
    b=calls(decode(asm),0x10018000,None,{0x10003788:'div',0x100038e8:'dto'})
    assert len(a)==16 and a==b
    return {'source_sha256':sha(src.read_bytes()),'sdk_commit':SDK_COMMIT,'headers':headers,'elf_sha256':sha(path.read_bytes()),'code_bytes':next(s['size'] for s in elf.sections if s['name']=='.text'),'ordered_calls':b,'source_admitted':False,'limits':['Complete source helper matches 16 ordered divider/DTO argument sets. Setter bodies and resulting clock frequencies not executed here. Analysis address only; not integrated.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-clock-dividers.json').write_text(json.dumps(r,indent=2)+'\n');print(r['code_bytes'],'source bytes;',len(r['ordered_calls']),'ordered calls matched')
