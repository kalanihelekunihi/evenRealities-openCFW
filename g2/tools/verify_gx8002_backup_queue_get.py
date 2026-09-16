# SPDX-License-Identifier: MIT
"""Decoded queue reads, head updates and output against an independent oracle."""
import json,re,subprocess
from build_gx8002_backup_queue_get import build,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def signed(x):return x if x<0x80000000 else x-(1<<32)

def execute(code,pc,initial):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=0x20040000,r1=0x20050000)
    before=r.copy();memory=initial.copy();condition=False;writes=[]
    for _ in range(4000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='rts':
            assert all(r[f'r{i}']==before[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],memory,writes
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','subu','mult','addi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0) if op=='addi' else r[p[-1]]
            r[p[0]]=(a-b if op=='subu' else a*b if op=='mult' else a+b)&M
        elif op=='divs':
            a,b=signed(r[p[1]]),signed(r[p[2]]);assert b
            r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&M
        elif op in ('cmpne','cmplt'):condition=r[p[0]]!=r[p[1]] if op=='cmpne' else signed(r[p[0]])<signed(r[p[1]])
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op=='blsz':
            if signed(r[p[0]])<=0:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
            if op=='ld.w':r[reg]=memory[address]
            else:memory[address]=r[reg];writes.append((address,r[reg]))
        elif op=='ldr.b':
            reg,base,index=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args).groups();r[reg]=memory[r[base]+r[index]]
        elif op=='stbi.b':
            reg,base=re.fullmatch(r'(r\d+), \((r\d+)\)',args).groups();memory[r[base]]=r[reg]&255;writes.append((r[base],r[reg]&255));r[base]+=1
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x428fc','--stop-address=0x4294a',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-queue-get/queue.disassembly.txt').read_text());cases=0
    for size in (1,2,8,16,64):
        for member in (1,2,8):
            for head in range(size):
                for tail in range(size):
                    mem={0x20040000:tail,0x20040004:head,0x20040008:0x20060000,0x2004000c:size,0x20040010:member}
                    mem.update({0x20060000+i:(i*37+19)&255 for i in range(size)});mem.update({0x20050000+i:0xcc for i in range(10)})
                    expected=mem.copy();writes=[]
                    if head!=tail:
                        for i in range(member):expected[0x20050000+i]=mem[0x20060000+(head+i)%size];writes.append((0x20050000+i,expected[0x20050000+i]))
                        expected[0x20040004]=(head+member)%size;writes.append((0x20040004,expected[0x20040004]))
                    want=(int(head!=tail),expected,writes)
                    assert execute(old,0x428fc,mem)==execute(new,0x10009fbc,mem)==want,(size,member,head,tail)
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Positive-size nonaliasing ordinary RAM, finite head/tail/member combinations; wraparound, empty, output guards and write ordering verified. Includes geometries outside normal initializer contracts.', 'No concurrent mutation, malformed signed sizes, zero division or hardware execution qualification.']}
    (ROOT/'docs/research/gx8002-backup-queue-get-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
