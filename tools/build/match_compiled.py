# SPDX-License-Identifier: MIT
"""Locate unique compiled bodies and recover literal/branch linker bindings.

Stock supplies only candidate addresses and relocation scalar values. Every
instruction must be reproduced by compiling and linking the source afterward.
"""
import hashlib
import struct


def branch_displacement(data,offset):
    first,second=struct.unpack_from('<HH',data,offset)
    if first & 0xf800!=0xf000:raise ValueError('not a Thumb wide branch')
    sign=(first>>10)&1;j1=(second>>13)&1;j2=(second>>11)&1
    value=(sign<<24)|((1^(j1^sign))<<23)|((1^(j2^sign))<<22)|((first&1023)<<12)|((second&2047)<<1)
    return value-(1<<25) if sign else value


def match(function,stock,entries,runtime_base,anchored_entry=None):
    data=function['data'];size=len(data)
    anchored=anchored_entry is not None
    if size<(2 if anchored else 16) or not function['section'].startswith('.text.'):return None
    records=function['relocation_records'];masked=set()
    for relocation in records:
        if relocation['type'] not in (2,10,30) or not relocation['symbol']:return None
        if relocation['offset']<0 or relocation['offset']+4>size:return None
        masked.update(range(relocation['offset'],relocation['offset']+4))
    fixed=[];start=None
    for i in range(size+1):
        known=i<size and i not in masked
        if known and start is None:start=i
        if not known and start is not None:fixed.append((start,i));start=None
    if sum(hi-lo for lo,hi in fixed)<(2 if anchored else 12):return None
    lo,hi=max(fixed,key=lambda r:r[1]-r[0])
    if hi-lo<(2 if anchored else 4):return None
    needle=data[lo:hi];candidates=[];position=0
    if anchored:
        entry=anchored_entry
        if entry not in entries or entry<0 or entry+size>len(stock):return None
        if all(stock[entry+a:entry+b]==data[a:b] for a,b in fixed):candidates.append(entry)
    while not anchored:
        occurrence=stock.find(needle,position)
        if occurrence<0:break
        position=occurrence+1;entry=occurrence-lo
        if entry not in entries or entry<0 or entry+size>len(stock):continue
        if all(stock[entry+a:entry+b]==data[a:b] for a,b in fixed):candidates.append(entry)
        if len(candidates)>1:return None
    if len(candidates)!=1:return None
    entry=candidates[0];bindings={};receipts=[]
    for relocation in records:
        offset=relocation['offset'];symbol=relocation['symbol'];kind=relocation['type']
        if kind in (10,30):
            # Plain source calls use the ELF Thumb branch addend -4. More
            # complex branch expressions require a separate qualified recipe.
            try:
                if branch_displacement(data,offset)!=-4:return None
                displacement=branch_displacement(stock,entry+offset)
            except (ValueError,struct.error):return None
            target=runtime_base+entry+offset+4+displacement
            if target-runtime_base not in entries:return None
            address=target|1;role='native_function'
        else:
            # ABS32 applies only to compiler-marked literal data, never to a
            # sequence of instruction words or an opaque opcode array.
            if not any(p['kind']=='data' and p['start']<=offset and offset+4<=p['end'] for p in function['content_ranges']):return None
            value=struct.unpack_from('<I',stock,entry+offset)[0]
            addend=struct.unpack_from('<I',data,offset)[0]
            address=(value-addend)&0xffffffff
            if not address:return None
            role='native_literal_symbol'
        if symbol in bindings and bindings[symbol]!=address:return None
        bindings[symbol]=address
        receipts.append(dict(symbol=symbol,offset=offset,relocation_type=kind,address=address,role=role))
    return dict(start=entry,end=entry+size,address=runtime_base+entry,bindings=bindings,
                match_evidence=dict(method=('independently named native entry and all unrelocated bytes, followed by full linked equality' if anchored else 'unique unrelocated bytes at inventoried native function entry, followed by full linked equality'),
                                    fixed_bytes=sum(b-a for a,b in fixed),compiled_pattern_sha256=hashlib.sha256(data).hexdigest(),relocations=receipts))
