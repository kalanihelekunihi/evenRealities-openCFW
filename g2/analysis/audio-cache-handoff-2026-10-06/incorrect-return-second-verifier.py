#!/usr/bin/env python3
"""Full stock query/getter with real cache provider; checked policy tested separately."""
import argparse, importlib.util, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('cache',ROOT/'g2/components/foundation/cache_maintenance/verify.py')
cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache)
H,P,OUT,CELL=0x20002000,0x20001000,0x20003000,0x2007450c


def handle(c):
    data=bytearray(b'\xa5'*0x60)
    for off,value in [(0x3c,c['first']),(0x40,c['second']),(0x44,c['first']+0x1000),
                      (0x48,c['tx_second']),(0x4c,c['selected']),(0x50,c['selected']+0x1000)]:
        struct.pack_into('<I',data,off,value&0xffffffff)
    return data


def selection(c):
    if c['kind']=='query' and c['selector']&255:
        return ((c['first'] if c['tx_second']==0xffffffff else c['selected'])+0x1000)&0xffffffff
    return c['first'] if c['second']==0xffffffff else c['selected']


def bounds_ok(address,length,base,capacity,op):
    return bool(base and capacity and base%32==0 and capacity%32==0 and op<=2 and
                base+capacity<=0xffffffff and 1<=length<=0x7fffffff and
                base<=address<base+capacity and address+length<=base+capacity)


def expected(c):
    if c['kind']=='query':return selection(c),None
    if c['kind']=='raw':return 3200,selection(c)
    if c['kind']=='checked_get':
        base,capacity=c['base'],c['capacity']
        if c['null_out'] or c['null_len'] or c['null_handle'] or not bounds_ok(selection(c),3200,base,capacity,0):return 6,None
        return 0,selection(c)
    if c['null_range'] or not bounds_ok(c['address'],c['length'],c['base'],c['capacity'],c['operation']):return 6,None
    return 0,c['address']


def run(segments,entry,c,primitive_entries):
    import unicorn as u
    import unicorn.arm_const as a
    cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4);pages=set()
    for s in segments:
        for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
            if p not in pages:cpu.mem_map(p,4096);pages.add(p)
        cpu.mem_write(s['address'],s['data'])
    for start,n in [(0x20000000,0x10000),(0x20074000,4096),(0xe000e000,8192),(cache.STOP,4096)]:cpu.mem_map(start,n)
    initial=handle(c);cpu.mem_write(H-8,b'\xcc'*8+initial+b'\xcc'*8)
    cpu.mem_write(P-8,b'\xcc'*8+struct.pack('<II',c['address'],c['length'])+b'\xcc'*8)
    cpu.mem_write(OUT-8,b'\xcc'*8+b'\xa5'*8+b'\xcc'*8)
    cpu.mem_write(CELL,struct.pack('<I',0 if c['null_handle'] else H))
    cpu.mem_write(cache.CCR,struct.pack('<I',c['ccr']));cpu.mem_write(cache.SIZE,struct.pack('<I',2))
    # Buffer contents are not touched by the provider, getter, or policy.
    cpu.mem_write(0x20008000,b'\x5a'*512)
    out_buffer=0 if c['null_out'] else OUT;out_length=0 if c['null_len'] else (OUT if c['alias'] else OUT+4)
    if c['kind']=='query':args=[H,c['selector'],0,0]
    elif c['kind']=='span':args=[0 if c['null_range'] else P,c['base'],c['capacity'],c['operation']]
    else:args=[out_buffer,out_length,c['base'],c['capacity']]
    for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],args):cpu.reg_write(reg,value)
    cpu.reg_write(a.UC_ARM_REG_SP,cache.SP);cpu.reg_write(a.UC_ARM_REG_LR,cache.STOP|1);cpu.reg_write(a.UC_ARM_REG_PRIMASK,c['prior'])
    saved={getattr(a,'UC_ARM_REG_R'+str(i)):0xabba0000+i for i in range(4,12)}
    for reg,value in saved.items():cpu.reg_write(reg,value)
    events,trace=[],{};range_pointer=[None];range_return=[None];changed=[False]
    def code(uc,pc,size,_):
        if pc==cache.STOP:uc.emu_stop();return
        seg=next((s for s in segments if s['flags']&1 and s['address']<=pc and pc+size<=s['address']+len(s['data'])),None);assert seg is not None,hex(pc)
        raw=bytes(uc.mem_read(pc,size));assert raw==seg['data'][pc-seg['address']:pc-seg['address']+size];trace[hex(pc)]=raw.hex()
        if pc==range_return[0]:
            range_pointer[0]=None;range_return[0]=None
        if pc in primitive_entries:
            range_pointer[0]=uc.reg_read(a.UC_ARM_REG_R0)
            range_return[0]=uc.reg_read(a.UC_ARM_REG_LR)&~1
            if c['mutate']:
                # Deliberate synthetic state change AFTER query. Not an ISR/hardware trace.
                slot=0x3c if c['second']==0xffffffff else 0x4c
                uc.mem_write(H+slot,struct.pack('<I',0x2000c000));changed[0]=True
        if raw==bytes.fromhex('bff34f8f'):events.append(['dsb'])
        if raw==bytes.fromhex('bff36f8f'):events.append(['isb'])
    def memory(uc,access,at,size,value,_):
        if 0xe000e000<=at<0xe0010000 or H<=at<H+0x60 or at==CELL or OUT<=at<OUT+8 or (range_pointer[0] is not None and range_pointer[0]<=at<range_pointer[0]+8):
            assert size==4
            value=struct.unpack('<I',uc.mem_read(at,4))[0] if access==u.UC_MEM_READ else value&0xffffffff
            if 0xe000e000<=at<0xe0010000:events.append(['read' if access==u.UC_MEM_READ else 'write',at,value])
            elif at==CELL:assert access==u.UC_MEM_READ;events.append(['handle_cell',value])
            elif H<=at<H+0x60:assert access==u.UC_MEM_READ;events.append(['handle',at-H,value])
            elif OUT<=at<OUT+8:assert access==u.UC_MEM_WRITE;events.append(['publish',at,value])
            elif range_pointer[0]<=at<range_pointer[0]+8:
                assert access==u.UC_MEM_READ;events.append(['range',at-range_pointer[0],value])
    cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,memory)
    cpu.emu_start(entry|1,cache.STOP,count=6000)
    assert cpu.reg_read(a.UC_ARM_REG_PC)==cache.STOP and cpu.reg_read(a.UC_ARM_REG_SP)==cache.SP
    assert cpu.reg_read(a.UC_ARM_REG_PRIMASK)==c['prior'];assert all(cpu.reg_read(r)==v for r,v in saved.items())
    if changed[0]:struct.pack_into('<I',initial,0x3c if c['second']==0xffffffff else 0x4c,0x2000c000)
    assert bytes(cpu.mem_read(H-8,len(initial)+16))==b'\xcc'*8+initial+b'\xcc'*8
    assert bytes(cpu.mem_read(P-8,24))==b'\xcc'*8+struct.pack('<II',c['address'],c['length'])+b'\xcc'*8
    assert bytes(cpu.mem_read(OUT-8,8))==bytes(cpu.mem_read(OUT+8,8))==b'\xcc'*8
    assert bytes(cpu.mem_read(0x20008000,512))==b'\x5a'*512
    return {'status':cpu.reg_read(a.UC_ARM_REG_R0),'events':events,'output':bytes(cpu.mem_read(OUT,8)).hex(),'trace':trace,'synthetic_state_changed':changed[0]}


def check(c,result):
    status,address=expected(c);assert result['status']==status,(c,result)
    events=result['events'];maintenance=[e for e in events if e[0] in ('read','write','dsb','isb','range')]
    publishes=[e for e in events if e[0]=='publish']
    if c['kind']=='query' or status==6:
        assert not maintenance and not publishes;assert result['output']=='a5'*8
        return
    core=cache.model(dict(ccr=c['ccr'],null=False,clean=c['kind']=='span' and c['operation']==2,
                          flag=1 if c['kind']=='span' and c['operation']==1 else 0,
                          size=2,address=address,length=c['length'] if c['kind']=='span' else 3200))
    core=[['range',e[1]-cache.H,e[2]] if e[0]=='read' and cache.H<=e[1]<cache.H+8 else e for e in core]
    assert maintenance==core,(c,maintenance,core)
    if c['kind']=='span':assert not publishes and result['output']=='a5'*8
    else:
        assert publishes==[['publish',OUT,address],['publish',OUT if c['alias'] else OUT+4,3200]]
        expected_output=struct.pack('<II',3200,0xa5a5a5a5) if c['alias'] else struct.pack('<II',address,3200)
        assert result['output']==expected_output.hex()
        # Publication occurs only after the cache provider's final barrier when cache enabled.
        assert events.index(publishes[0])>max((i for i,e in enumerate(events) if e[0] in ('write','dsb','isb')),default=-1)


def cases():
    d=dict(first=0x20008000,second=0xffffffff,tx_second=0xffffffff,selected=0x20009000,selector=0,
           ccr=0x10000,prior=0,alias=False,mutate=False,null_out=False,null_len=False,null_handle=False,
           null_range=False,address=0x20008000,length=3200,base=0x20008000,capacity=4096,operation=0)
    for selector in [0,1,255,256,257]:
        for second in [0xffffffff,0,0x20008800]:
            for tx in [0xffffffff,0,0x20009800]:
                for prior in [0,1]:yield dict(d,kind='query',selector=selector,second=second,tx_second=tx,prior=prior)
    for second in [0xffffffff,0,0x20008800]:
        for ccr in [0,0x10000]:
            for align in [0,1,15,31]:
                for alias in [False,True]:
                    for mutate in [False,True]:
                        for prior in [0,1]:yield dict(d,kind='raw',second=second,ccr=ccr,first=d['first']+align,selected=d['selected']+align,alias=alias,mutate=mutate,prior=prior)
    for operation in [0,1,2,3]:
        for capacity in [0,3200,3232,4096]:
            for offset in [0,1,31,32,4090]:
                for length in [0,1,32,3200,0x7fffffff,0x80000000,0xffffffff]:
                    for ccr in [0,0x10000]:yield dict(d,kind='span',operation=operation,capacity=capacity,address=d['base']+offset,length=length,ccr=ccr)
    for values in [dict(base=0),dict(base=0x20008001),dict(capacity=31),dict(base=0xffffffe0,capacity=64),dict(null_range=True)]:
        yield dict(d,kind='span',**values)
    for capacity in [0,3200,3232,4096]:
        for offset in [0,1,31]:
            for ccr in [0,0x10000]:yield dict(d,kind='checked_get',capacity=capacity,first=d['base']+offset,ccr=ccr)
    for values in [dict(null_out=True),dict(null_len=True),dict(null_handle=True),dict(base=0),dict(base=0x20008001),dict(capacity=31),dict(base=0xffffffe0,capacity=64)]:
        yield dict(d,kind='checked_get',**values)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert cache.sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob.read_bytes()[32:]
    assert raw[0x78d474-cache.BASE:0x78d47c-cache.BASE]==struct.pack('<II',0,3200)
    stock=[dict(address=p,memory_size=n,data=raw[p-cache.BASE:p-cache.BASE+n],flags=f) for p,n,f in [(0x475000,4096,5),(0x57a000,4096,5),(0x590000,8192,5),(0x78d000,4096,4)]]
    _,segments,symbols=cache.elf_reader.elf_info(a.elf);results=[];trace={};original_count=policy_count=0
    for c in cases():
        symbol={'query':'opencfw_i2s_selected_buffer','raw':'opencfw_audio_rx_buffer_get','span':'opencfw_cache_checked','checked_get':'opencfw_audio_rx_buffer_get_checked'}[c['kind']]
        source=run(segments,symbols[symbol]&~1,c,[symbols['opencfw_cache_clean']&~1,symbols['opencfw_cache_invalidate']&~1]);source.pop('trace');check(c,source)
        if c['kind'] in ('query','raw'):
            original=run(stock,0x590b6c if c['kind']=='query' else 0x57a7e0,c,[0x475014,0x47510e]);observed=original.pop('trace');check(c,original);assert original==source,(c,original,source)
            for pc,value in observed.items():assert pc not in trace or trace[pc]==value;trace[pc]=value
            results.append({'inputs':c,'original':original,'source':source});original_count+=1
        else:results.append({'inputs':c,'source':source,'scope':'new checked policy, no original implementation claimed'});policy_count+=1
    used={int(pc,0)+i for pc,value in trace.items() for i in range(len(bytes.fromhex(value)))}
    manifest={str(p.relative_to(ROOT)):cache.sha(p) for root in [Path(__file__).parent,ROOT/'g2/components/foundation/cache_maintenance'] for p in root.iterdir() if p.suffix in ('.c','.h','.py')}
    result={'status':'PASS','cases':original_count,'original_source_cases':original_count,'checked_policy_cases':policy_count,'results':results,'original_trace':trace,'unique_original_trace_bytes':len(used),
            'elf_sha256':cache.sha(a.elf),'firmware_sha256':cache.sha(blob),'source_manifest':manifest,
            'limits':'Complete stock selected-buffer query and audio getter plus actual cache provider, no executable callee stubs. Synthetic coherent handle/global state and raw cache registers. Synthetic post-query mutation expressly injected, not actual scheduling/hardware hazard proof. Getter borrows pointer, copies no PCM and claims no exclusive ownership. Checked adapters are new capacity policy, not firmware replacements or original equivalence; trust supplied bounds, cannot prove lifetime. Huge raw inputs retained separately as bounded prefixes, not completed-path passes.'}
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('PASS original/source',original_count,'new policy',policy_count,'original trace bytes',len(used))


if __name__=='__main__':main()
