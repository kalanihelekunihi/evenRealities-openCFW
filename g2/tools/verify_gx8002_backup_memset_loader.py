# SPDX-License-Identifier: MIT
"""Decoded backup loader normal path with modeled flash reads and returning entry."""
import json,re,subprocess
from build_gx8002_backup_memset import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,SEG2_OFF
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,image,mode,seed):
    assert mode!=0xaabbccdd
    regs={f'r{i}':(seed+i*0x10203)&MASK for i in range(32)};regs['r14']=0x2002fffc;initial=dict(regs)
    memory={0x20001724:0x2f3b0,0x20033ffc:mode};calls=[];saved=None;condition=False;pc=0x396a0
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r5, r15' and saved is None;saved={n:regs[n] for n in ('r4','r5','r15')};regs['r14']-=12
        elif op=='pop':
            assert args=='r4-r5, r15' and saved is not None and regs['r14']==initial['r14']-12
            regs.update(saved);regs['r14']+=12
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return regs['r0'],calls,memory
        elif op in ('lrw','movi'):regs[p[0]]=int(p[1],0)
        elif op=='mov':regs[p[0]]=regs[p[1]]
        elif op=='bseti':regs[p[0]]|=1<<int(p[1],0)
        elif op in ('addi','subi','addu','subu'):
            a=regs[p[1]] if len(p)==3 else regs[p[0]];b=regs[p[-1]] if p[-1] in regs else int(p[-1],0)
            regs[p[0]]=(a-b if op in ('subi','subu') else a+b)&MASK
        elif op=='cmpne':condition=regs[p[0]]!=regs[p[1]]
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert match
            reg,base,off=match.groups();address=regs[base]+int(off,0)
            if op=='ld.w':regs[reg]=memory[address]
            else:assert address==0x2002d3e4;memory[address]=regs[reg]
        elif op=='bsr':
            assert int(args,0)==0x39930
            offset,dest,length=regs['r0'],regs['r1'],regs['r2'];calls.append(['read',offset,dest,length])
            data=image[SEG2_OFF+offset:SEG2_OFF+offset+length];assert len(data)==length and length%4==0
            for i in range(0,length,4):memory[dest+i]=int.from_bytes(data[i:i+4],'little')
            for i in (0,1,2,3,12,13,15,*range(18,32)):regs[f'r{i}']=0xbad00000+i
        elif op=='jsr':
            assert regs[args]==0x10003100;calls.append(['entry',regs[args]])
            for i in (0,1,2,3,12,13,15,*range(18,32)):regs[f'r{i}']=0xbad10000+i
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('backup loader bound')


def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x396a0','--stop-address=0x396ee',str(p)],text=True))
    p=ROOT/'build/gx8002-backup-memset/memset-candidate.elf';elf=Elf32(p.read_bytes(),'candidate');body=elf.contents(next(s for s in elf.sections if s['name']=='.text'))
    image=bytearray(stock);offset=candidate['package_offset'];image[offset:offset+candidate['stock_envelope_bytes']]=body+bytes(candidate['stock_envelope_bytes']-len(body));cases=0
    for mode in (0,1,MASK,0xaabbccdc):
        for seed in (0,91,MASK):
            result,calls,memory=execute(code,bytes(image),mode,seed)
            assert result==0 and calls==[['read',0x323b0,0x2002ffec,4],['read',0x323b4,0x10003000,0x1408c],['entry',0x10003100]]
            loaded=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10003000,0x1001708c,4))
            assert loaded==image[0x3b940:0x4f9cc]
            relative=candidate['runtime_address']-0x10003000;assert loaded[relative:relative+len(body)]==body
            assert loaded[relative+len(body):relative+candidate['stock_envelope_bytes']]==bytes(candidate['stock_envelope_bytes']-len(body))
            assert memory[0x2002d3e4]==0x10003100;cases+=1
    return {'candidate':candidate,'loader_sha256':sha(stock[0x396a0:0x39744]),'cases':cases,'candidate_image_sha256':sha(bytes(image)),'zero_tail_bytes':candidate['stock_envelope_bytes']-len(body),'source_admitted':False,'hardware_qualified':False,'limits':['Normal backup loader instructions copy the complete initialized SRAM image containing source candidate bytes with modeled flash reads and returning entry. Saved registers and entry pointer checked.','Special 0xaabbccdd branch, physical flash behavior, backup selection, application execution and external entry into the replacement envelope remain separate. Zero-filled tail is copied and checked, but not admitted as unreachable here.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-memset-loader.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup memset loader:',r['cases'],'cases')
