#!/usr/bin/env python3
"""Bounded, data-only IAR Arm archive extraction and stock fingerprint probe.

No compiler invocation, login, source import, or license-sensitive source access.
Requires GNU arm-none-eabi-ar and arm-none-eabi-objdump (override with flags).
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path

MEMBERS = ["printf.o", "printf_s.o", "sprintf.o", "sprintf_s.o", "snprintf.o", "snprintf_s.o",
           "vsnprintf_s.o", "vsprintf.o", "vsprintf_s.o", "memcpy_s.o", "memset_s.o",
           "memcpy.o", "memset.o", "memmove.o", "xxmemxmemcpy.o", "xxmemxmemmove.o",
           "xxmemxmemzero.o", "builtins_float.o", "xfprout.o", "xprintfdefault.o",
           "xprintffull.o", "xprintflarge.o", "xprintfsmall.o", "xprintftiny.o"]
# Authenticated binary load base and extents from SHORTCUT-ASSESSMENT.md.
STOCK = [
    {"name":"snprintf", "address":0x41b218, "size":62, "source":"assessment"},
    {"name":"vsnprintf", "address":0x41b25c, "size":None, "source":"assessment; size not stated"},
    {"name":"_Printf backend", "address":0x41e47a, "size":3256, "source":"assessment"},
]
INSN = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4,8}\s+)+)([a-z][a-z0-9.]*)\s*(.*)$', re.I)

def run(argv):
    return subprocess.run(argv, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def disasm_range(path, objdump, start, size):
    out=run([objdump,'-d',str(path)])
    instructions=[]
    for line in out.splitlines():
        m=INSN.match(line)
        if m and start <= int(m.group(1),16) < start+size:
            mnemonic=m.group(3).lower(); operands=m.group(4).strip()
            instructions.append({'address':int(m.group(1),16),'width':len(m.group(2).split())*2,'mnemonic':mnemonic,'raw_operands':operands})
    return instructions

def function_symbols(path, objdump):
    """Return only .text STT_FUNC entries with declared nonzero ELF st_size."""
    result=[]
    for line in run([objdump,'-t',str(path)]).splitlines():
        parts=line.split()
        # GNU objdump: value binding type section size [visibility] name.
        if len(parts)<6 or parts[2]!='F' or parts[3]!='.text': continue
        try: size=int(parts[4],16); address=int(parts[0],16)
        except ValueError: continue
        if size==0: continue
        result.append({'address':address,'size':size,'binding':parts[1],'name':parts[-1]})
    return result

def shape(f):
    seq=[x['mnemonic'] for x in f['insns']]
    is_branch=lambda m: ((m.startswith('b') and m not in ('bl','blx','bic','bfc','bfi','bkpt')) or m.startswith(('cb','tb')))
    branches=sum(is_branch(m) for m in seq)
    calls=sum(m in ('bl','blx') for m in seq)
    ret=sum(m in ('bx','pop') for m in seq)
    addrs=[i['address'] for i in f['insns']]; leaders={addrs[0]} if addrs else set(); edges=0
    for ix,i in enumerate(f['insns']):
        m=i['mnemonic']
        if not is_branch(m): continue
        target_match=re.search(r'(?:0x)?([0-9a-f]+)',i['raw_operands'],re.I)
        target=int(target_match.group(1),16) if target_match else None
        if target in addrs: leaders.add(target); edges+=1
        conditional=(m not in ('b','b.w','b.n','bx','bxj'))
        if conditional and ix+1<len(addrs): leaders.add(addrs[ix+1]); edges+=1
        elif target is not None and target not in addrs: edges+=1
    return {'instruction_count':len(seq),'branch_count':branches,'basic_block_count':len(leaders),'cfg_edge_count':edges,'call_count':calls,'return_like_count':ret,
            'coarse_mnemonic_sequence_sha256':hashlib.sha256(' '.join(seq).encode()).hexdigest()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',type=Path,help='optional installed IAR .a; only named members are extracted')
    ap.add_argument('--objects',type=Path,default=Path('/tmp/opencfw-iar-runtime-objects'),help='directory for extracted named members')
    ap.add_argument('--stock',type=Path,default=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'))
    ap.add_argument('--out',type=Path,default=Path('report.json'))
    ap.add_argument('--ar',default='arm-none-eabi-ar'); ap.add_argument('--objdump',default='arm-none-eabi-objdump')
    ap.add_argument('--limit',type=int,default=50)
    ap.add_argument('--min-function-size',type=int,default=16,help='minimum declared ELF function extent')
    ap.add_argument('--expected-stock-sha256',default='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5')
    a=ap.parse_args()
    if not 20 <= a.limit <= 50: ap.error('--limit must be 20..50')
    a.objects.mkdir(parents=True,exist_ok=True)
    extracted=[]
    if a.archive:
        names=set(run([a.ar,'t',str(a.archive)]).splitlines())
        for member in MEMBERS:
            if member not in names: continue
            data=subprocess.run([a.ar,'p',str(a.archive),member],check=True,stdout=subprocess.PIPE).stdout
            dest=a.objects/member; dest.write_bytes(data); extracted.append(str(dest))
    candidates=[]; obj_files=[]
    for member in MEMBERS:
        p=a.objects/member
        if not p.exists(): continue
        headers=run([a.objdump,'-h','-r',str(p)])
        section_headers=[line.strip() for line in headers.splitlines() if re.match(r'^\s*\d+\s+\.',line)]
        tm=re.search(r'^\s*\d+\s+\.text\s+([0-9a-f]+)',headers,re.M)
        text_size=int(tm.group(1),16) if tm else None
        metadata={}
        section_names=[x.split()[1] for x in section_headers if len(x.split())>1]
        metadata_sections={'.iar.rtmodel','.iar.stackusage','.debug_frame'}
        for sec in sorted(metadata_sections):
            try:
                metadata[sec]=run([a.objdump,'-s','-j',sec,str(p)])
            except subprocess.CalledProcessError:
                metadata[sec]=None
        obj_files.append({'path':str(p),'sha256':sha(p),'sections':section_headers,
                          'relocation_records':headers.split('RELOCATION RECORDS FOR'),
                          'iar_rtmodel_dump':metadata['.iar.rtmodel'],
                          'iar_stackusage_dump':metadata['.iar.stackusage'],
                          'debug_frame_dump':metadata['.debug_frame']})
        for sym in function_symbols(p,a.objdump):
            if sym['size']<a.min_function_size: continue
            insns=disasm_range(p,a.objdump,sym['address'],sym['size'])
            if not insns: continue
            f={'insns':insns}
            candidates.append({'object':member,'name':sym['name'],'binding':sym['binding'],'offset':sym['address'],'size':sym['size'],
                               'extent_basis':'declared ELF STT_FUNC st_size','all_instructions_in_declared_extent':True,**shape(f)})
    # Stable bounded subset: prioritize named formatter, memory, and floating helpers.
    candidates.sort(key=lambda x:(not bool(re.search(r'printf|litob|fp|float|mem|str|div|mod',x['name'],re.I)),x['object'],x['offset']))
    # Round-robin objects so the bounded sample is not consumed by one formatter variant.
    grouped={}
    for c in candidates: grouped.setdefault(c['object'],[]).append(c)
    selected=[]
    while len(selected)<a.limit and any(grouped.values()):
        for member in MEMBERS:
            if grouped.get(member) and len(selected)<a.limit: selected.append(grouped[member].pop(0))
    candidates=selected
    stock_sha=sha(a.stock)
    if stock_sha.lower()!=a.expected_stock_sha256.lower():
        ap.error(f'locked stock hash mismatch: expected {a.expected_stock_sha256}, got {stock_sha}')
    stock_evidence=[]
    for s in STOCK:
        item=dict(s)
        if s['size'] is None:
            item['status']='negative: unresolved extent; no exact comparison performed'
            stock_evidence.append(item); continue
        off=s['address']-0x410000
        data=a.stock.read_bytes()[off:off+s['size']]
        item['observed_file_offset']=off; item['observed_size']=len(data)
        # objdump a bounded region as a temporary raw Thumb binary.
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(data); tf.flush()
            txt=run([a.objdump,'-D','-b','binary','-m','arm','-M','force-thumb',f'--adjust-vma={s["address"]}',tf.name])
        seq=[]
        for line in txt.splitlines():
            m=INSN.match(line)
            if m: seq.append(m.group(3).lower())
        # Retain a minimal raw disassembly parse for branch leaders and CFG edges.
        parsed=[]
        for line in txt.splitlines():
            m=INSN.match(line)
            if m: parsed.append({'address':int(m.group(1),16),'mnemonic':m.group(3).lower(),'raw_operands':m.group(4)})
        leaders={parsed[0]['address']} if parsed else set(); edges=0
        for ix,i in enumerate(parsed):
            mn=i['mnemonic']; br=(mn.startswith('b') and mn not in ('bl','blx','bic','bfc','bfi','bkpt')) or mn.startswith(('cb','tb'))
            if not br: continue
            mt=re.search(r'(?:0x)?([0-9a-f]+)',i['raw_operands'],re.I); target=int(mt.group(1),16) if mt else None
            addrs=[q['address'] for q in parsed]
            if target in addrs: leaders.add(target); edges+=1
            conditional=mn not in ('b','b.w','b.n','bx','bxj')
            if conditional and ix+1<len(parsed): leaders.add(parsed[ix+1]['address']); edges+=1
            elif target is not None and target not in addrs: edges+=1
        is_branch=lambda m: ((m.startswith('b') and m not in ('bl','blx','bic','bfc','bfi','bkpt')) or m.startswith(('cb','tb')))
        item.update({'instruction_count':len(seq),'branch_count':sum(is_branch(m) for m in seq),'basic_block_count':len(leaders),'cfg_edge_count':edges,
                     'call_count':sum(m in ('bl','blx') for m in seq),
                     'coarse_mnemonic_sequence_sha256':hashlib.sha256(' '.join(seq).encode()).hexdigest(),
                     'status':'extent comparison available'})
        stock_evidence.append(item)
    # Direct candidates: exact size is only a prefilter; this coarse sequence hash does
    # not normalize relocation operands or compiler-version code generation.
    comparisons=[]
    for c in candidates:
        for s in stock_evidence:
            if s.get('size') is None: continue
            same_size=c['size']==s['size']
            same_shape=(c['coarse_mnemonic_sequence_sha256']==s['coarse_mnemonic_sequence_sha256'])
            comparisons.append({'candidate':f"{c['object']}:{c['name']}",'candidate_size':c['size'],'stock':s['name'],
                                'stock_size':s['size'],'size_equal':same_size,'coarse_mnemonic_sequence_equal':same_shape,
                                'result':'possible fingerprint lead only' if same_size and same_shape else 'negative'})
    out={'scope':'bounded IAR archive object metadata vs locked G2 stock image; no source or compiler used',
         'stock':{'path':str(a.stock),'sha256':stock_sha,'load_address':'0x00410000'},
         'archive':{'path':str(a.archive) if a.archive else 'not supplied',
                    'sha256':sha(a.archive) if a.archive else None,
                    'input_role':'original installed IAR archive' if a.archive else 'local object directory',
                    'members_extracted':extracted,'objects':obj_files,
                    'tool_version':run([a.ar,'--version']).splitlines()[0]},
         'limits':{'candidate_limit':a.limit,'minimum_declared_function_size_bytes':a.min_function_size,'candidates_considered':len(candidates),
                   'stock_candidate_version':'EWARM 9.60.2 candidate; not confirmed','installed_object_version':'IAR Base 10.10.2.27058',
                   'normalized_fingerprint':'coarse mnemonic-sequence fingerprint; operands, literals, relocation sites and compiler differences are not normalized',
                   'source_identity_claim':False},'stock_functions':stock_evidence,'candidates':candidates,
         'comparisons':comparisons,
         'interpretation':'An exact size and instruction-shape pair is a lead only. Different IAR versions prevent treating mismatch as proof of source-family absence. No source-implementation credit or byte-equality claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'out':str(a.out),'stock_sha256':stock_sha,'objects':len(obj_files),'candidates':len(candidates),'comparisons':len(comparisons),'extracted':len(extracted)},indent=2))
if __name__=='__main__': main()
