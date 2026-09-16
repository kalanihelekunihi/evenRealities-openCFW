# SPDX-License-Identifier: MIT
"""Decoded async packet dispatch against stock and independent call traces."""
import itertools,json,re,struct,subprocess
from build_gx8002_backup_uart_async_tick import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,pc,delta,packet,entries,available,crc_result,callback_result):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;before=r.copy();mem={};trace=[];condition=False;saved=None
    def put(a,data):mem.update({a+i:b for i,b in enumerate(data)})
    def word(a):return sum(mem[a+i]<<(8*i) for i in range(4))
    for i,(port,cmd,callback,priv) in enumerate(entries):
        row=bytearray(28);row[0]=port;struct.pack_into('<I',row,4,cmd);struct.pack_into('<II',row,20,callback,priv);put(0x2002cf30+28*i,row)
    for _ in range(500):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r4, r15';saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            assert args=='r4, r15';r['r4'],r['r15']=saved;r['r14']+=8
            assert all(r[f'r{i}']==before[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&M
        elif op in ('cmpne','cmpnei'):condition=r[p[0]]!=(int(p[1],0) if op=='cmpnei' else r[p[1]])
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op in ('bez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','ld.h','ld.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0);n={'ld.w':4,'ld.h':2,'ld.b':1}[op]
            r[reg]=sum(mem[a+i]<<(8*i) for i in range(n))
        elif op in ('bsr','jsr'):
            target=int(args,0)+delta if op=='bsr' else r[args];result=0
            if target==0x10009fbc:
                assert r['r0']==0x2002d770 and r['r1']==r['r14'];trace.append(('queue',));result=available
                if available:put(r['r1'],packet)
            elif target==0x1000c5c4:
                trace.append(('crc',r['r0'],r['r1'],r['r2']));result=crc_result
            elif target==0x10009934:trace.append(('printf',r['r0'],r['r1']))
            else:
                assert target in [e[2] for e in entries] and target
                assert r['r0']==r['r14'];trace.append(('callback',target,r['r1'],bytes(mem[r['r0']+i] for i in range(32))));result=callback_result
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbad00000+i
            r['r0']=result
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    e=Elf32(wrapper.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x43e08','--stop-address=0x43e8c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-uart-async-tick/tick.disassembly.txt').read_text());cases=0
    for available,flags,match,valid,ret,port in itertools.product((0,1),(0,1,2,255),(-1,0,7,15),(False,True),(0,7,M),(0,1,255)):
        packet=bytearray(32);struct.pack_into('<H',packet,4,0x1234);packet[7]=flags;packet[20]=port;struct.pack_into('<I',packet,16,0x20050000);struct.pack_into('<II',packet,24,19,0x89abcdef);packet=bytes(packet)
        entries=[(((port+1)&255) if i%2 else port,0x1234 if i%2 else 0x4321,0x10020000+4*i,i+33) for i in range(16)]
        if match>=0:
            entries[match]=(port,0x1234,0x10020000+4*match,match+33)
            if match<15:entries[match+1]=(port,0x1234,0x10020000+4*(match+1),match+34)
        crc=0x89abcdef if valid else 0x89abcdee;wanted=[('queue',)];result=M
        if available:
            if flags==1:wanted.append(('crc',0,0x20050000,19))
            if flags==1 and not valid:wanted.append(('printf',0x10013624,19))
            elif match>=0:wanted.append(('callback',entries[match][2],entries[match][3],packet));result=ret
        args=(packet,entries,available,crc,ret)
        assert execute(old,0x43e08,0x10000000-0x38940,*args)==execute(new,0x1000b4c8,0,*args)==(result,wanted),(available,flags,match,valid,ret,port)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Queue, CRC, printf and callback bodies modeled. Stock/source dispatch compared with independent expected traces; first match, port mismatch, absent registration, CRC rejection and callback returns covered.', 'No concurrent registration mutation, null matched callback execution, nested helpers or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-uart-async-tick-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
