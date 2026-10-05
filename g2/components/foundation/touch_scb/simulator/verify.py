#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute linked source ELF and original ARM instructions with a synthetic FIFO.

The read hook supplies deterministic MMIO words. It is a test stimulus, not a
hardware FIFO model or evidence of bus/IRQ/concurrent consumption behavior.
"""
import argparse, hashlib, json, struct
from pathlib import Path
if not __debug__:
    raise RuntimeError('Simulator evidence verification requires assertions; optimized Python is rejected')
ROOT=Path(__file__).resolve().parents[5]
SCB=0x40250000; DST=0x20001000; PACKET=0x20002000; STOP=0x08000000
SHA='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
def digest(b): return hashlib.sha256(b).hexdigest()
def require(ok,message):
    if not ok: raise ValueError(message)
def elf_info(path):
    data=Path(path).read_bytes()
    require(52<=len(data)<=2*1024*1024,'ELF file size out of bounds')
    require(data[:6]==b'\x7fELF\x01\x01','requires ELF32 little endian')
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    require(h[1]==2 and h[2]==40,'requires linked ARM executable')
    require(h[9]==32 and 1<=h[10]<=16 and h[5]+h[9]*h[10]<=len(data),'invalid program table')
    require(h[11]==40 and 1<=h[12]<=1024 and h[6]+h[11]*h[12]<=len(data) and h[13]<h[12],'invalid section table')
    segments=[]
    for i in range(h[10]):
        p=struct.unpack_from('<IIIIIIII',data,h[5]+i*h[9])
        if p[0]==1:
            require(p[4]<=p[5]<=65536 and p[1]+p[4]<=len(data),'invalid load segment size')
            require(any(lo<=p[2]<=p[2]+p[5]<=hi for lo,hi in [(0x10000,0x20000),(0x20000000,0x20010000)]),'load segment outside simulator memory')
            segments.append(dict(address=p[2],data=data[p[1]:p[1]+p[4]],memory_size=p[5],flags=p[6]))
    sections=[struct.unpack_from('<IIIIIIIIII',data,h[6]+i*h[11]) for i in range(h[12])]
    symbols={}
    for s in sections:
        if s[1]!=2: continue
        require(s[6]<len(sections) and s[9]==16 and s[5]%16==0 and s[4]+s[5]<=len(data),'invalid symbol table')
        st=sections[s[6]];strings=data[st[4]:st[4]+st[5]]
        require(st[1]==3 and st[4]+st[5]<=len(data),'invalid symbol string table')
        for off in range(s[4],s[4]+s[5],s[9]):
            name,val,size,info,other,index=struct.unpack_from('<IIIBBH',data,off)
            require(name<len(strings),'invalid symbol name offset')
            text=strings[name:].split(b'\0',1)[0].decode()
            if text and index: symbols[text]=val
    return data,segments,symbols
def execute(segments,entry,ctrl,status,requested,values,checked=False,capacity=1024,base=SCB,destination=DST,tx=False,config=0,fifo_level=False):
    import unicorn,capstone
    from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
    u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
    pages=set()
    for seg in segments:
        for a in range(seg['address']&~4095,(seg['address']+seg['memory_size']+4095)&~4095,4096):
            if a not in pages:u.mem_map(a,4096);pages.add(a)
        u.mem_write(seg['address'],seg['data'])
    if 0x20000000 not in pages:u.mem_map(0x20000000,65536)
    else:
        for a in range(0x20000000,0x20010000,4096):
            if a not in pages:u.mem_map(a,4096)
    u.mem_map(SCB,4096);u.mem_map(STOP,4096)
    u.mem_write(SCB+(0x200 if tx else 0x300),struct.pack('<I',ctrl));u.mem_write(SCB+(0x208 if tx else 0x308),struct.pack('<I',status))
    u.mem_write(SCB,struct.pack('<I',config))
    u.mem_write(SCB+0x304,struct.pack('<I',ctrl))
    guard=b'\xa5'*1040;u.mem_write(DST-8,guard)
    if tx: u.mem_write(DST,bytes(values))
    initial=bytes(u.mem_read(DST-8,len(guard))).hex()
    reads=[];trace=[];popped=[];written=[]
    md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
    def read(uc,access,a,n,value,user):
        if SCB<=a<SCB+4096:
            assert n==4 and a in ([SCB,SCB+0x304] if fifo_level else ([SCB,SCB+0x200,SCB+0x208] if tx else [SCB+0x300,SCB+0x308,SCB+0x340])),hex(a)
            reads.append(a-SCB)
            if a==SCB+0x340:
                assert len(popped)<len(values),'unexpected FIFO read'
                v=values[len(popped)];popped.append(v);uc.mem_write(a,struct.pack('<I',v))
    def code(uc,a,n,user):
        matches=[s for s in segments if s['flags']&1 and s['address']<=a<a+n<=s['address']+len(s['data'])]
        assert len(matches)==1,hex(a)
        s=matches[0];raw=bytes(uc.mem_read(a,n));assert raw==s['data'][a-s['address']:a-s['address']+n]
        ins=list(md.disasm(raw,a));assert len(ins)==1 and ins[0].size==n
        trace.append(dict(pc=a,bytes=raw.hex()))
    def write(uc,access,a,n,value,user):
        if SCB<=a<SCB+4096:
            assert n==4 and ((tx and a==SCB+0x240) or (fifo_level and a==SCB+0x304)),'unexpected MMIO write'
            written.append(value)
    u.hook_add(unicorn.UC_HOOK_MEM_READ,read);u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write);u.hook_add(unicorn.UC_HOOK_CODE,code)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if checked:
        u.mem_write(PACKET,struct.pack('<6I',base,destination,requested,capacity,0xdeadbeef,0xffffffff));u.reg_write(UC_ARM_REG_R0,PACKET)
    else:
        for reg,v in [(UC_ARM_REG_R0,base),(UC_ARM_REG_R1,destination),(UC_ARM_REG_R2,requested)]:u.reg_write(reg,v)
        if fifo_level: u.reg_write(UC_ARM_REG_R1,requested)
    u.emu_start(entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    packet=list(struct.unpack('<6I',bytes(u.mem_read(PACKET,24)))) if checked else None
    return dict(return_value=u.reg_read(UC_ARM_REG_R0),memory=bytes(u.mem_read(DST-8,len(guard))).hex(),reads=reads,popped=popped,written=written,initial_memory=initial,trace=trace,packet=packet)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert digest(blob)==SHA
    image=blob[32:];assert digest(image)=='371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87'
    original=image[0x5f18:0x5f6e]
    assert digest(original[:56])=='07627776d2bc275029e974a40d0944d6b87502cfea118880b8d60d6c3fa97cc7'
    assert digest(original[56:])=='c7729e5dfb38b7391112b5eeeb9e0a8b0fc0d2ad0bc2e1e9b53b353b401e5e49'
    stock=[dict(address=0x9218,data=original,memory_size=len(original),flags=5)]
    elf,segments,symbols=elf_info(args.elf);assert 'touch_scb_sim_read' in symbols and 'touch_scb_sim_checked' in symbols
    cases=[];original_pc={}
    vectors=[(0,0,0),(0,3,2),(8,3,9),(16,2,2),(24,0x12340003,0xffffffff),(0,0xffffffff,512),(8,4,0),(0xffffffe7,5,5)]
    for i,(ctrl,status,request) in enumerate(vectors):
        actual=min(status&511,request);width=2 if ctrl&24 else 1;values=[(0xabcd0000+k*0x10201+0x80)&0xffffffff for k in range(actual)]
        a=execute(stock,0x9250,ctrl,status,request,values);b=execute(segments,symbols['touch_scb_sim_read'],ctrl,status,request,values)
        assert a['return_value']==b['return_value']==actual
        assert a['memory']==b['memory'] and a['reads']==b['reads']==[0x308,0x300]+[0x340]*actual and a['popped']==b['popped']==values
        expected=b'\xa5'*8+b''.join(v.to_bytes(4,'little')[:width] for v in values)+b'\xa5'*(1032-actual*width)
        assert bytes.fromhex(a['memory'])==expected
        for t in a['trace']:original_pc[t['pc']]=bytes.fromhex(t['bytes'])
        cases.append(dict(index=i,control=ctrl,status=status,requested=request,width=width,actual=actual,original=a,source_linked=b))
    checked=[]
    # Added adapter behavior; no stock equivalent is asserted.
    for name,ctrl,status,request,cap,base,dst in [('success',8,3,9,6,SCB,DST),('capacity',8,3,9,5,SCB,DST),('null_base',0,3,9,9,0,DST),('unaligned_base',0,3,9,9,SCB+1,DST),('unaligned_halfword',8,3,9,6,SCB,DST+1),('overflow_base',0,3,9,9,0xfffffffc,DST)]:
        r=execute(segments,symbols['touch_scb_sim_checked'],ctrl,status,request,[0x1234,0x5678,0x9abc],True,cap,base,dst)
        if name=='success':assert r['packet'][4]==3 and r['packet'][5]==0 and len(r['popped'])==3
        else:assert r['packet'][5]!=0 and not r['popped'] and r['packet'][4]==0xdeadbeef and r['memory']=='a5'*1040
        checked.append(dict(name=name,result=r))
    tx_bytes=image[0x5f6e:0x5fd6]
    assert digest(tx_bytes[:56])=='ba8eabab79e5f3cf46e4b9b7bd76456a262ed1ff7d3780885a747f9eb6e1b434'
    assert digest(tx_bytes[56:])=='e3bd934582667c74ed28fa5a43ce49d2a70802d22b01b6f01ff19994fa474ce9'
    tx_stock=[dict(address=0x926e,data=tx_bytes,memory_size=len(tx_bytes),flags=5)]
    tx_cases=[];tx_checked=[]
    vectors_tx=[(0,0,0,0),(0,0,0,20),(0,8,15,20),(0x4000,16,0,9),(0x8000,24,7,3),(0xc000,0,8,9),(0,8,4,0),(0,0xffffffe7,0x1234000f,0xffffffff),(0,0,17,2),(0x4000,8,9,2),(0,0,511,2),(0,8,17,17)]
    source=bytes((i*37+0x80)&255 for i in range(64))
    for i,(config,ctrl,status,request) in enumerate(vectors_tx):
        depth=8 if config&0xc000 else 16;actual=min(request,(depth-(status&511))&0xffffffff);width=2 if ctrl&24 else 1
        a=execute(tx_stock,0x92a6,ctrl,status,request,source,tx=True,config=config)
        b=execute(segments,symbols['touch_scb_sim_write'],ctrl,status,request,source,tx=True,config=config)
        expected=[int.from_bytes(source[k*width:(k+1)*width],'little') for k in range(actual)]
        assert a['return_value']==b['return_value']==actual
        assert a['reads']==b['reads']==[0,0x208,0x200]
        assert a['written']==b['written']==expected
        assert a['memory']==a['initial_memory']==b['memory']==b['initial_memory']
        for t in a['trace']:original_pc[t['pc']]=bytes.fromhex(t['bytes'])
        tx_cases.append(dict(index=i,config=config,control=ctrl,status=status,requested=request,actual=actual,width=width,original=a,source_linked=b))
    for name,config,ctrl,status,request,cap,base,dst in [('success',0,8,13,9,6,SCB,DST),('full',0x4000,0,8,9,0,SCB,DST),('capacity',0,8,13,9,5,SCB,DST),('bad_status',0,0,17,2,64,SCB,DST),('null_base',0,0,0,2,64,0,DST),('unaligned_base',0,0,0,2,64,SCB+1,DST),('overflow_base',0,0,0,2,64,0xfffffffc,DST),('unaligned_halfword',0,8,0,2,64,SCB,DST+1),('null_source',0,0,0,2,64,SCB,0)]:
        r=execute(segments,symbols['touch_scb_sim_write_checked'],ctrl,status,request,source,True,cap,base,dst,tx=True,config=config)
        assert r['memory']==r['initial_memory']
        if name in ['success','full']:
            count=3 if name=='success' else 0
            assert r['packet'][4]==count and r['packet'][5]==0
            assert r['written']==[int.from_bytes(source[k*2:k*2+2],'little') for k in range(count)]
        else:assert r['packet'][5]!=0 and r['packet'][4]==0xdeadbeef and not r['written']
        tx_checked.append(dict(name=name,result=r))
    fifo_body=image[0x6016:0x6042]
    assert digest(fifo_body)=='1fdc6e20657ebf1efbbf7423c354904526f55af9f31d09ad5cd700d69ecdb993'
    fifo_stock=[dict(address=0x9316,data=fifo_body,memory_size=len(fifo_body),flags=5)]
    fifo_cases=[];fifo_errors=[]
    for config,level in [(0,0),(0,15),(0x4000,0),(0x8000,7),(0xc000,7)]:
        initial=0xa5c312e7
        a=execute(fifo_stock,0x9316,initial,0,level,[],config=config,fifo_level=True)
        b=execute(segments,symbols['touch_scb_sim_set_rx_level'],initial,0,level,[],config=config,fifo_level=True)
        assert b['return_value']==0 and a['reads']==b['reads']==[0,0x304]
        assert a['written']==b['written']==[(initial&~255)|level]
        assert a['memory']==a['initial_memory']==b['memory']==b['initial_memory']
        for t in a['trace']:original_pc[t['pc']]=bytes.fromhex(t['bytes'])
        fifo_cases.append(dict(config=config,level=level,original=a,source_linked=b))
    for config,level in [(0,16),(0x4000,8),(0xc000,0x101),(0,0xffffffff)]:
        b=execute(segments,symbols['touch_scb_sim_set_rx_level'],0xa5c312e7,0,level,[],config=config,fifo_level=True)
        assert b['return_value']==2 and b['reads']==[0] and not b['written']
        fifo_errors.append(dict(config=config,level=level,result=b))
    report=dict(status='PASS'  ,payload_sha256=SHA,script_sha256=digest(Path(__file__).read_bytes()),linked_elf_sha256=digest(elf),elf=str(args.elf),entry_symbols={k:hex(symbols[k]) for k in ['touch_scb_sim_read','touch_scb_sim_checked','touch_scb_sim_write','touch_scb_sim_write_checked','touch_scb_sim_set_rx_level']},original_function_ranges=[dict(runtime=[0x9218,0x9250],payload=[0x5f38,0x5f70],sha256=digest(original[:56])),dict(runtime=[0x9250,0x926e],payload=[0x5f70,0x5f8e],sha256=digest(original[56:]))],original_unique_executed_instruction_bytes=sum(map(len,original_pc.values())),new_original_execution_bytes_relative_to_prior_wrapper=sum(map(len,original_pc.values()))-30,comparison_cases=cases,checked_adapter_cases=checked,fifo_comparison_cases=fifo_cases,fifo_checked_error_cases=fifo_errors,fifo_original_range=dict(runtime=[0x9316,0x9342],sha256=digest(fifo_body)),tx_comparison_cases=tx_cases,tx_checked_adapter_cases=tx_checked,tx_original_ranges=[dict(runtime=[0x926e,0x92a6],sha256=digest(tx_bytes[:56])),dict(runtime=[0x92a6,0x92d6],sha256=digest(tx_bytes[56:]))],source_manifest={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted((ROOT/"g2/components/foundation/touch_scb").rglob("*")) if p.suffix in [".c",".h",".ld"]},limits='Linked callable source-defined Cortex-M0+ simulator module, no reset vectors or hardware startup. Both implementations read the same synthetic FIFO sequence; no original callee stubs. No hardware ISR/clock/IRQ/concurrent consumer/FIFO register side-effect proof. Not stock-byte-equivalent or complete firmware.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream: stream.write(json.dumps(report,indent=2)+'\n')
    print('PASS TX',len(tx_cases),'comparisons;',len(tx_checked),'checked cases; RX',len(cases),'original+linked comparisons;',len(checked),'adapter cases;',report['original_unique_executed_instruction_bytes'],'original instruction bytes')
if __name__=='__main__':main()
