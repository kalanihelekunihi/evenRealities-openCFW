# SPDX-License-Identifier: MIT
"""Execute console wrappers with explicitly modeled external UART calls."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,args,port,result,targets):
    r={f'r{i}':0xa0000000+i for i in range(32)};r['r14']=0x8000
    for i,a in enumerate(args):r[f'r{i}']=a
    initial=r.copy();events=[];pc=entry;saved=None
    for _ in range(20):
        op,text,width=code[pc];p=[v.strip() for v in text.split(',')]
        if op=='push':assert text=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert text=='r15';r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            return port,r['r0'],events
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('st.w','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',text);assert m
            reg,base,off=m.groups();assert r[base]+int(off,0)==0x2001739c
            if op=='st.w':port=r[reg];events.append(['store_port',port])
            else:r[reg]=port;events.append(['load_port',port])
        elif op=='bsr':
            name=targets[int(text,0)];events.append([name,r['r0'],r['r1'],port])
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xbad00000+i
            r['r0']=result
        else:raise AssertionError((hex(pc),op,text))
        pc+=width
    raise AssertionError('console bound')


def verify():
    report=json.loads((ROOT/'docs/research/gx8002-backup-console.json').read_text())
    path=ROOT/'build/gx8002-backup-console/console.elf';assert sha(path.read_bytes())==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d148','--stop-address=0x3d16c',str(wrapper)],text=True))
    delta=0x10003000-0x3b940;targets={0x3ce5c:'uart_init',0x3cee0:'uart_putc'}
    count=0
    for port in (0,1,2,0x7fffffff,0x80000000,0xffffffff):
        for value in (0,10,13,255,256,115200,0xffffffff):
            for result in (0,1,0xffffffff):
                for entry,args,expected_events in [(0x3d148,[port,value],[['store_port',port],['uart_init',port,value,port]]),(0x3d158,[value],[['load_port',port],['uart_putc',port,value,port]])]:
                    a=execute(old,entry,args,port,result,targets)
                    b=execute(code,entry+delta,args,port,result,{k+delta:v for k,v in targets.items()})
                    assert a==b==(port,result,expected_events)
                    count+=1
    result={'elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'cases':count,'source_admitted':False,'limits':['Decoded wrapper argument forwarding, state order, modeled return propagation and preserved ABI registers. UART calls modeled, not UART hardware execution.','Invalid port values test wrapper behavior only; underlying UART valid-port contract remains separate.']}
    (ROOT/'docs/research/gx8002-backup-console-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
