# SPDX-License-Identifier: MIT
"""Compile and qualify SDK-layout buffer accessors without binary pull-through."""
import json,re,subprocess,shutil
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_logging import check_paths
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32

# suffix, package location, envelope, header field offset (or constant return)
ROWS=(('mic_buffer_addr',0x103f8,12,80),('mic_buffer_size',0x10404,12,84),
      ('logfbank_buffer_addr',0x10410,12,112),('logfbank_buffer_size',0x1041c,12,116),
      ('context_header',0x10428,8,None),('feats_buffer',0x10430,8,None))


def execute(code,entry,memory,seed):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)};initial=r.copy();reads=[];pc=entry
    for _ in range(8):
        op,args,w=code[pc]
        if op=='lrw':
            reg,value=args.split(', ');r[reg]=int(value,0)
        elif op=='movih':
            reg,value=args.split(', ');r[reg]=int(value,0)<<16
        elif op=='ld.w':
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            address=r[base]+int(offset,0)
            if address%4 or any(address+i not in memory for i in range(4)):raise ValueError('Read bounds')
            r[reg]=int.from_bytes(bytes(memory[address+i] for i in range(4)),'little');reads.append(address)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],reads
        else:raise ValueError('Unexpected accessor opcode '+op)
        pc+=w
    raise ValueError('Execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('include/lvp_context.h','include/lvp_attr.h','lvp/common/lvp_buffer.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    source=ROOT/'components/shared/gx8002/runtime_gx8002_buffer_accessors.c'
    out=ROOT/'build/gx8002-buffer-accessors';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I',str(sdk/'include'),'-c',str(source),'-o',str(out/'accessors.o')],check=True)
    sections=['SECTIONS {']
    for suffix,offset,size,field in ROWS:
        sections.append('.text.'+suffix+' '+hex(offset+0x101f6a74)+' : { *(.text.open_cfw_gx8002_'+suffix+') }')
    sections.append('}')
    (out/'accessors.ld').write_text('\n'.join(sections)+'\n')
    subprocess.run([pre+'ld','-T',str(out/'accessors.ld'),str(out/'accessors.o'),'-o',str(out/'accessors.elf')],check=True)
    elf=Elf32((out/'accessors.elf').read_bytes(),'accessors')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    wanted_sections={'.text.'+row[0] for row in ROWS}
    if any(s['size'] and s['flags']&2 and s['name'] not in wanted_sections for s in elf.sections):raise ValueError('Unowned allocation')
    disassembly=subprocess.check_output([pre+'objdump','-d',str(out/'accessors.elf')],text=True)
    (out/'accessors.disassembly.txt').write_text(disassembly);code=decode(disassembly)
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock_elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(stock_elf.contents(next(s for s in stock_elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper identity')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x103f8','--stop-address=0x10438',str(wrapper)],text=True))
    functions=[];cases=0
    for suffix,offset,size,field in ROWS:
        section=next(s for s in elf.sections if s['name']=='.text.'+suffix);payload=elf.contents(section)
        if len(payload)>size:raise ValueError('Accessor envelope '+suffix)
        if suffix!='feats_buffer' and payload!=stock[offset:offset+size]:raise ValueError('Accessor exact match '+suffix)
        for seed in (0,1,0x7fffffff,0x80000000,0xffffffff,0xa5a5a5a5):
            values=(*range(256),0x7fffffff,0x80000000,0xffffffff,0x20030410,0x20032210)
            for value in values:
                memory={} if field is None else {0x20027b60+field+i:b for i,b in enumerate(value.to_bytes(4,'little'))}
                expected=(0x20030000 if suffix=='feats_buffer' else 0x20027b60,[]) if field is None else (value,[0x20027b60+field])
                for instructions,entry in ((code,offset+0x101f6a74),(old,offset)):
                    if execute(instructions,entry,memory,seed)!=expected:raise ValueError('Accessor result/read trace')
                cases+=1
        symbol='open_cfw_gx8002_'+suffix
        functions.append({'symbol':symbol,'section_name':'.text.'+suffix,'compiled_bytes':len(payload),
          'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,
          'sha256':sha(stock[offset:offset+size]),'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'accessors.elf',output/'accessors.elf')
    return {'functions':functions,'decoded_cases':cases,'source_sha256':sha(source.read_bytes()),'flags':flags,
      'sdk_commit':SDK_COMMIT,'upstream':upstream,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_buffer_accessors.py','verify_gx8002_memcpy_source.py')},
      'limits':['Fixed firmware RAM layout; five exact linked stock matches; all six decoded stock/source return values, read addresses and saved ABI checked. No physical memory or concurrent mutation qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-buffer-accessors-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
