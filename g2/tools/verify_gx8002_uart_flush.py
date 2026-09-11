# SPDX-License-Identifier: MIT
"""Compare decoded drain waits, including finite prefixes of a stalled UART."""
import hashlib,json,re,subprocess
from itertools import product
from build_gx8002_uart_flush import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths


def execute(code,entry,port,statuses,descriptor_base=0x20026a94,device_base=None):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=port
    initial=r.copy();pc=entry;trace=[];reads=0;descriptor=(descriptor_base+(port<<7))&0xffffffff
    device=0xa0100000+port*0x1000 if device_base is None else device_base
    for _ in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op in ('lsli','addu','addi','andi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a&b if op=='andi' else a+b)&0xffffffff
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Flush load operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if address==descriptor+4:
                # A repeated descriptor read observes a changed device pointer.
                value=device if not trace else device+0x10000
            elif address==device+20:
                if reads==len(statuses):return False,trace
                value=statuses[reads];reads+=1
            else:raise ValueError('Unexpected flush read '+hex(address))
            r[reg]=value;trace.append(('read',address,value))
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Flush ABI')
            return True,trace
        else:raise ValueError('Flush instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Flush instruction bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build(prefix,output);wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Flush wrapper identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xcb24','--stop-address=0xcb40',str(wrapper)],text=True))
    out=output or ROOT/'build/gx8002-uart-flush'
    new=decode((out/'flush.disassembly.txt').read_text())
    cases=0;stalled=0
    for port,delay,waiting,ready in product((0,1),(0,1,3,32,128),(0,1,32,0xffffffbf),(64,65,0xffffffff,None)):
        statuses=[waiting]*delay+([] if ready is None else [ready])
        a=execute(old,0xcb24,port,statuses);b=execute(new,0x10203598,port,statuses)
        device=0xa0100000+port*0x1000
        expected=(ready is not None,[('read',0x20026a98+port*128,device)]+[('read',device+20,x) for x in statuses])
        if a!=b or a!=expected:raise ValueError('Flush trace/termination contract')
        cases+=1;stalled+=ready is None
    if not candidate['fits']:raise ValueError('Flush exceeds original envelope')
    row={'symbol':'open_cfw_gx8002_uart_flush','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],
         'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_uart_flush',
         'package_offset':candidate['package_offset'],'bytes':candidate['envelope_bytes'],'sha256':candidate['stock_sha256'],
         'region':'image_a_sram_text'}]}
    evidence={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in
        ('build_gx8002_uart_flush.py','verify_gx8002_uart_flush.py')}
    return {'functions':[row],'candidate':candidate,'decoded_cases':cases,'stalled_prefixes':stalled,
        'evidence_sha256':evidence,'source_admitted':True,'hardware_qualified':False,
        'limits':['Finite modeled MMIO traces, valid ports only. Stalled cases stop at the next unavailable stimulus; the C routine retains the stock unbounded wait. No physical UART timing proof.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-flush-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Flush cases:',r['decoded_cases'],'stalled prefixes:',r['stalled_prefixes'])
