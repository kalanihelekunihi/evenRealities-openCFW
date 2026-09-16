# SPDX-License-Identifier: MIT
"""Decode complete upstream exception entry through its existing terminal loop."""
import json,re,random,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,initial,control):
    regs=initial.copy();control=control.copy();memory={};writes=[];pc=0x100031fc;called=False
    for _ in range(64):
        op,args,width=code[pc];parts=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='psrset':assert args=='ee';control[0]|=1<<8
        elif op=='lrw':regs[parts[0]]=int(parts[1],0)
        elif op in ('addi','subi'):
            base=regs[parts[1]] if len(parts)==3 else regs[parts[0]]
            regs[parts[0]]=(base+(1 if op=='addi' else -1)*int(parts[-1],0))&0xffffffff
        elif op in ('st.w','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,offset=m.groups();address=regs[base]+int(offset,0)
            if op=='st.w':memory[address]=regs[reg];writes.append((address,regs[reg]))
            else:regs[reg]=memory[address]
        elif op=='stm':
            assert args=='r0-r12, (r14)'
            for i in range(13):
                address=regs['r14']+4*i;memory[address]=regs[f'r{i}'];writes.append((address,regs[f'r{i}']))
        elif op=='mfcr':
            m=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args);assert m
            regs[m[1]]=control[int(m[2])]
        elif op=='mov':regs[parts[0]]=regs[parts[1]]
        elif op=='lsri':regs[parts[0]]=regs[parts[1]]>>int(parts[2],0)
        elif op=='sextb':
            value=regs[parts[1]]&255;regs[parts[0]]=(value if value<128 else value-256)&0xffffffff
        elif op=='bsr':
            assert int(args,0)==0x100031f0 and regs['r0']==0x20017348
            called=True;regs['r15']=nxt;nxt=int(args,0)
        elif op=='br':
            assert called and pc==0x100031f8 and int(args,0)==pc
            return memory,writes,regs
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('exception instruction bound')


def verify():
    path=ROOT/'build/gx8002-backup-upstream-trap/trap.elf'
    report=json.loads((ROOT/'docs/research/gx8002-backup-upstream-trap.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256']
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    rng=random.Random(80472);count=0
    for vector in range(256):
        initial={f'r{i}':rng.getrandbits(32) for i in range(32)};initial['r14']=0x2002fffc
        controls={0:(rng.getrandbits(16)|(vector<<16)),2:rng.getrandbits(32),4:rng.getrandbits(32)}
        memory,writes,regs=execute(code,initial,controls)
        expected=[initial[f'r{i}'] for i in range(14)]+[initial['r14'],initial['r15'],controls[2],controls[4]]
        assert [memory[0x20017348+4*i] for i in range(18)]==expected
        assert memory[0x20017390]==initial['r14'] and memory[initial['r14']-4]==initial['r13']
        assert len(writes)==20 and set(memory)=={initial['r14']-4,0x20017390,*range(0x20017348,0x20017390,4)}
        assert regs['r3']==(vector if vector<128 else vector-256)&0xffffffff
        count+=1
    result={'elf_sha256':report['elf_sha256'],'cases':count,'frame_words':18,'writes_per_entry':20,'source_admitted':False,'limits':['All 256 vector-byte values with deterministic register/control states; decoded frame writes and existing terminal loop checked.','No physical exception delivery, nested exceptions, stack-depth or recovery claim. This is the original fatal handler, not replacement functionality for missing code.']}
    (ROOT/'docs/research/gx8002-backup-upstream-trap-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
