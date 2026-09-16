# SPDX-License-Identifier: MIT
"""Compare cached-ID flash reads, including complete multi-chunk byte transfers."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_flash_read import build,ROOT,sha
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,source,device,length,offset,busy,seed,identify=None,composed=False):
    chunks=[min(65536,length-i) for i in range(0,length,65536)]
    def statuses():
        for count in chunks:
            yield from [1]*busy;yield 0
            for _ in range(count):yield from [0]*busy;yield 8
            yield from [1]*busy;yield 0
    status=iter(statuses());fifo=iter(([1]*busy+[0])*len(chunks))
    data=bytes((i*37+offset)&255 for i in range(length));received=iter(data)
    helper_plan=[];setup=[]
    if identify is not None:
        sr1,sr2=identify
        setup=[('write',0xa0300090,1)]+[('write',0xa2000000+a,v) for a,v in ((8,0),(0x2c,0),(0xf0,1),(0x14,2),(0x1c,31),(8,1))]
        helper_plan.append(('reg_read',159,tuple(device.to_bytes(3,'big'))))
        setup.append(('write',0x20001730,device))
        if device not in (0x1c3812,0x1c3813):
            two=device in (0x854012,0x856013,0x856014)
            if two:helper_plan.append(('reg_read',5,(sr1,)))
            helper_plan.append(('reg_read',53,(sr2,)))
            if not sr2&2:
                helper_plan += [('reg_read',5,(v,)) for v in [1]*busy+[0]]
                helper_plan += [('reg_write',6,()),('reg_write',1 if two else 49,(sr1,sr2|2) if two else (sr2|2,))]
                helper_plan += [('reg_read',5,(v,)) for v in [1]*busy+[0]]
        helper_plan += [('reg_read',5,(v,)) for v in [1]*busy+[0]]
    remaining=iter(helper_plan);active=None;helper_traces=[]
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r.update(r0=offset,r1=0x20050000,r2=length,r14=0x20040000)
    initial=dict(r);mem={0x20001730:0xffffff if identify is not None else device};pc=0x10000fdc if source else 0x39930;trace=[];polls=0;condition=False;frames=[]
    for _ in range(20000+length*(10+busy*4)):
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op=='push':
            registers=[]
            for part in p:
                if '-' in part:
                    first,last=part.split('-');registers.extend(f'r{i}' for i in range(int(first[1:]),int(last[1:])+1))
                else:registers.append(part)
            frames.append({k:r[k] for k in registers});r['r14']-=4*len(registers)
        elif op=='pop':
            saved=frames.pop();r.update(saved);r['r14']+=4*len(saved)
            if frames:nxt=r['r15']
            else:
                assert all(r[k]==initial[k] for k in (*saved,'r14')) and r['r0']==0
                break
        elif op=='rts':
            assert active is not None and r['r0']==0
            assert next(active['status'],None) is None and next(active['fifo'],None) is None
            if not active['write']:assert next(active['received'],None) is None
            assert all(r[f'r{i}']==active['saved'][f'r{i}'] for i in (*range(4,12),14,15,16,17))
            payload=active['payload'];count=len(payload)
            writes=[(8,0),(0x4c,0),(0,0x407 if active['write'] else 0xc07),(4,count if active['write'] else (count-1)&0xffffffff),(0x10,1),(0x18,count<<16 if active['write'] else 0),(0xf4,0),(8,1),(0x60,active['command'])]
            if active['write']:writes += [(0x60,v) for v in payload]
            assert [e for e in active['trace'] if e[0]=='write' and e[1]>=0xa0000000]==[('write',0xa2000000+a,v) for a,v in writes]
            assert [e for e in active['trace'] if e[1]<0xa0000000]==[('read' if active['write'] else 'write',active['buffer']+i,v) for i,v in enumerate(payload)]
            helper_traces.append([e for e in active['trace'] if e[1]>=0xa0000000]);nxt=r['r15'];active=None
        elif op in ('lrw' ,'movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bseti':r[p[0]]=r[p[-2]]|1<<int(p[-1],0)
        elif op=='rotli':
            value=r[p[1]];shift=int(p[2],0);r[p[0]]=((value<<shift)|(value>>(32-shift)))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op in ('addu','subu'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]]*(1 if op=='addu' else -1))&0xffffffff
        elif op in ('min.s32','min.u32'):
            values=[r[x] for x in p[1:]]
            if op=='min.s32':values=[x if x<0x80000000 else x-0x100000000 for x in values]
            r[p[0]]=min(values)&0xffffffff
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op in ('addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0);r[p[0]]=(a-b if op=='subi' else a+b)&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmplt':
            a,b=(r[x] for x in p);condition=(a if a<0x80000000 else a-0x100000000)<(b if b<0x80000000 else b-0x100000000)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bf','bt','br','bez','bnez'):
            take=True if op=='br' else (condition if op=='bt' else not condition) if op in ('bt','bf') else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.h','ld.b','st.w','st.b','stbi.b','ldbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            reg,base,off=m.groups();address=r[base]+(int(off,0) if off else 0)
            if op.startswith('st'):
                value=r[reg] if op=='st.w' else r[reg]&255
                assert address>=0xa0000000 or 0x20050000<=address<0x20050000+length or address==0x20001730 or r['r14']<=address<initial['r14']
                mem[address]=value
                if active is not None:active['trace'].append(('write',address,value))
                elif not r['r14']<=address<initial['r14']:trace.append(('write',address,value))
                if op=='stbi.b':r[base]+=1
            else:
                if active is not None and address>=0xa0000000:
                    if address==0xa2000028:value=next(active['status'])
                    elif address==(0xa2000020 if active['write'] else 0xa2000024):value=next(active['fifo'])
                    else:assert address==0xa2000060 and not active['write'];value=next(active['received'])|0xa5a50000
                elif address==0xa2000028:value=next(status)
                elif address==0xa2000024:value=next(fifo)
                elif address==0xa2000060:value=next(received)|0xa5a50000
                elif op=='ld.h':value=mem[address]|mem[address+1]<<8
                else:value=mem[address]
                r[reg]=value
                if active is not None:active['trace'].append(('read',address,value))
                elif address>=0xa0000000:trace.append(('read',address,value))
                if op=='ldbi.b':r[base]+=1
        elif op=='bsr':
            target=int(args,0)
            helper_target=target if not source else {0x10000edc:0x39830,0x10000f5c:0x398b0}.get(target)
            if composed and helper_target in (0x39830,0x398b0):
                assert active is None
                if identify is not None:
                    kind,command,payload=next(remaining);trace.append((kind,command,payload))
                else:
                    kind,command,payload='reg_read',5,(1 if polls<busy else 0,);polls+=1;trace.append(('status',5))
                write=kind=='reg_write'
                assert helper_target==(0x398b0 if write else 0x39830) and r['r0']==command and r['r2']==len(payload)
                r['r15']=nxt
                active={'write':write,'command':command,'payload':payload,'buffer':r['r1'],'saved':r.copy(),'trace':[],
                    'status':iter([1]*busy+[0]+sum(([0]*busy+[2 if write else 8] for _ in payload),[])+[1]*busy+[0]),
                    'fifo':iter([1]*busy+[0]),'received':iter(payload)}
                pc=target;continue
            if source and target in code:
                r['r15']=nxt;pc=target;continue
            if source:target={0x100001f8:0x38b4c,0x10000edc:0x39830,0x10000f5c:0x398b0}[target]
            if target==0x38b4c:
                assert r['r0']==13;trace.append(('gate',13,r['r1']))
            elif identify is not None:
                kind,command,payload=next(remaining)
                assert target==(0x39830 if kind=='reg_read' else 0x398b0) and r['r0']==command and r['r2']==len(payload)
                if kind=='reg_read':
                    for i,v in enumerate(payload):mem[r['r1']+i]=v
                else:assert tuple(mem[r['r1']+i] for i in range(len(payload)))==payload
                trace.append((kind,command,payload))
            else:
                assert target==0x39830 and r['r0']==5 and r['r2']==1
                mem[r['r1']]=1 if polls<busy else 0;polls+=1;trace.append(('status',5))
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            if identify is not None:r['r0']=0
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    else:raise AssertionError('bound')

    assert next(status,None) is None and next(fifo,None) is None and next(received,None) is None
    assert bytes(mem[0x20050000+i] for i in range(length))==data
    assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
    expected=[('gate',13,1)]+[('status',5)]*(busy+1)
    if identify is not None:
        assert next(remaining,None) is None and mem[0x20001730]==device
        expected=[('gate',13,1)]+setup[:7]+helper_plan[:1]+setup[7:]+helper_plan[1:]
    position=0
    special=device in (0x1c3812,0x1c3813)
    for count in chunks:
        expected += [('read',0xa2000028,v) for v in [1]*busy+[0]]
        writes=[(0x4c,0),(8,0),(0x10,0),(0,0x800807),(4,count-1),(0x18,0),(0x54,7),(0xf4,0x40003219 if special else 0x40004218),(8,1),(0x64,0xeb if special else 0x6b),(0x64,(offset+position)&0xffffffff),(0x10,1)]
        expected += [('write',0xa2000000+a,v) for a,v in writes]
        for i in range(count):
            value=data[position+i]
            expected += [('read',0xa2000028,v) for v in [0]*busy+[8]]
            expected += [('read',0xa2000060,value|0xa5a50000),('write',0x20050000+position+i,value)]
        expected += [('read',0xa2000024,v) for v in [1]*busy+[0]]
        expected += [('read',0xa2000028,v) for v in [1]*busy+[0]]
        position+=count
    expected += [('gate',13,0)]
    assert trace==expected,(source,device,length,offset,busy)
    return (trace,helper_traces) if composed else trace


def verify(identify=False,composed=False):
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==IMAGE.read_bytes()
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x39930','--stop-address=0x39b78',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-stage1-flash-read/flash.disassembly.txt').read_text());cases=0
    if composed:
        from build_gx8002_stage1_flash_cluster import build as cluster_build
        evidence=cluster_build()
        old=decode(subprocess.check_output([tool,'-D','--start-address=0x39830','--stop-address=0x39b78',str(wrapper)],text=True))
        new=decode((ROOT/'build/gx8002-stage1-flash-cluster/cluster.disassembly.txt').read_text())
    scenarios=list(product((0x1c3812,0x1c3813,0x854012,0xffffffff),(0,1,3,65),(0,0xfffffff0),(0,2),(0,0x87654321)))
    scenarios += list(product((0x1c3812,0x854012),(65535,65536,65537,131073),(0xfffffff0,),(0,),(0x87654321,)))
    if identify:
        scenarios=product((0,0x1c3811,0x1c3812,0x1c3813,0x1c3814,0x854011,0x854012,0x854013,0x856012,0x856013,0x856014,0x856015,0xffffff),(0,3,65),(0,2),(0,0x87654321),(0,0x54,0xff),(0,2,0x80,0xff))
        for device,length,busy,seed,sr1,sr2 in scenarios:
            assert execute(old,False,device,length,0xfffffff0,busy,seed,(sr1,sr2),composed)==execute(new,True,device,length,0xfffffff0,busy,seed,(sr1,sr2),composed)
            cases+=1
        report={'cases':cases,'build':evidence,'composed_helpers':composed,'limits':['Successful identification with fully supplied ID/status helper buffers and zero helper returns. Tests device dispatch boundaries, both quad setup methods, already-enabled quad and no-setup IDs, preserved status bits, finite waits and short transfers. Helpers modeled; physical SPI, helper failure/partial buffers and self-overwrite remain unqualified.']}
        if composed:report['limits']=['Actual stock/source register helpers execute in the caller register/stack frame; ordered MMIO traces match, each helper buffer access is independently checked relative to its passed pointer. Clock gate remains modeled; finite readiness sequences, synthetic destination, no physical-controller or self-overwrite qualification.']
        (ROOT/('docs/research/gx8002-stage1-flash-identify-composed.json' if composed else 'docs/research/gx8002-stage1-flash-identify.json')).write_text(json.dumps(report,indent=2)+'\n');return report
    for device,length,offset,busy,seed in scenarios:
        assert execute(old,False,device,length,offset,busy,seed,None,composed)==execute(new,True,device,length,offset,busy,seed,None,composed)
        cases+=1
    report={'cases':cases,'build':evidence,'composed_helpers':composed,'limits':['Cached IDs only; register status and clock helpers modeled. Complete ordered MMIO and byte-transfer oracle, finite polls, address wrap and 64-KiB chunk boundaries. Synthetic nonoverlapping destination at 0x20050000; no hardware RAM availability claim. No physical-controller, successful identification, destination/self-overwrite or lengths above INT_MAX qualification.']}
    if composed:report['limits']=['Cached-ID reads with actual register helpers executing in the caller frame; independent helper MMIO/buffer oracle and complete reader trace oracle. Clock gate modeled; synthetic destination, finite polls; hardware, self-overwrite and lengths above INT_MAX unqualified.']
    (ROOT/('docs/research/gx8002-stage1-flash-read-transfers-composed.json' if composed else 'docs/research/gx8002-stage1-flash-read-transfers.json')).write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import sys
    print(verify('--identify' in sys.argv,'--composed' in sys.argv)['cases'],'flash reader cases passed')
