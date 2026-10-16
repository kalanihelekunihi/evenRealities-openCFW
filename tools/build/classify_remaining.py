# SPDX-License-Identifier: MIT
"""Partition unresolved stored bytes by evidence without promoting decoded data.

A byte-equal disassembly listing establishes a decoder observation, not that a
CPU executes it. This distinction matters for literal pools decoded as opcodes.
"""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
LABELS={0:'no_finer_evidence',1:'candidate_correspondence',2:'function_envelope',
        3:'byte_verified_disassembly',4:'accelerator_command_stream',5:'compressed_mixed_content'}


def decoded_spans(text, stock, base):
    spans=[];rejected=0
    for line in text.splitlines():
        match=re.match(r'^0x([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+',line)
        if not match:continue
        lo=int(match[1],16)-base
        try:data=bytes.fromhex(match[2])
        except ValueError:rejected+=1;continue
        if data and 0<=lo<len(stock) and stock[lo:lo+len(data)]==data:
            spans.append((lo,lo+len(data)))
        else:rejected+=1
    return spans,rejected


def classify(details, report, stage, baseline, component_names):
    components={component_names[c['component']]:c for c in baseline['componentsExclusive']}
    result=[];evidence=[]
    catalog_path=ROOT/'tools/build/disassembly-evidence.json'
    catalog=json.loads(catalog_path.read_text())
    evidence.append(dict(path=str(catalog_path.relative_to(ROOT)),sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest()))
    for detail in details:
        name=detail['payload'];size=detail['size'];kinds=bytearray(size)
        component=components.get(name)
        if component:
            for lo,hi,kind in component['runs']:
                if kind==2:kinds[lo:hi]=b'\1'*(hi-lo)
        if name=='r1-application':
            functions=ROOT/'r1/research/decompilation/application/functions.csv';base=0x27000
            rows=csv.DictReader(io.StringIO(functions.read_text()))
            spans=[(int(r['entry'],16)-base,int(r['entry'],16)-base+int(r['size'])) for r in rows]
        else:
            symbols={'g2-apollo-main':('apollo_main',0x437fe0),'g2-apollo-bootloader':('bootloader',0x410000),
                     'g2-case':('case',0x8000000-32),'g2-touch':('touch',0x3300-32)}
            spans=[]
            if name in symbols:
                symbol,base=symbols[name];functions=ROOT/f'g2/symbols/{symbol}.tsv'
                spans=[(int(r['address'],16)-base,int(r['address'],16)-base+int(r['size']))
                       for r in csv.DictReader(io.StringIO(functions.read_text()),delimiter='\t') if r['size']]
        if spans:
            evidence.append(dict(path=str(functions.relative_to(ROOT)),sha256=hashlib.sha256(functions.read_bytes()).hexdigest()))
            for lo,hi in spans:
                if 0<=lo<hi<=size:kinds[lo:hi]=b'\2'*(hi-lo)
        payload=next(p for p in report['payloads'] if p['payload']==name)
        stock=(stage/payload['file']).read_bytes()
        if name in catalog['payload_sha256']:
            if hashlib.sha256(stock).hexdigest()!=catalog['payload_sha256'][name]:raise ValueError('disassembly catalog payload mismatch')
            for span in catalog['spans']:
                if span['payload']!=name:continue
                lo,hi=span['start'],span['end']
                if not 0<=lo<hi<=size or hashlib.sha256(stock[lo:hi]).hexdigest()!=span['sha256']:raise ValueError('disassembly catalog span mismatch')
                kinds[lo:hi]=b'\3'*(hi-lo)
        if name=='r1-application':
            path=ROOT/'r1/research/decompilation/application/disassembly.s'
            spans,rejected=decoded_spans(path.read_text(),stock,0x27000)
            for lo,hi in spans:kinds[lo:hi]=b'\3'*(hi-lo)
            evidence.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),matched_rows=len(spans),rejected_rows=rejected))
        if name=='g2-case':
            path=ROOT/'g2/build/pseudocode-first/20260930T190500Z/analysis/case-function-index-139/002/instructions.jsonl'
            if path.exists():
                matched=rejected=0
                for line in path.read_text().splitlines():
                    row=json.loads(line);lo,hi=row['image_span'];data=bytes.fromhex(row['bytes'])
                    # The export uses raw-flash coordinates; package has a 32-byte header.
                    lo+=32;hi+=32
                    if 0<=lo<hi<=size and stock[lo:hi]==data:
                        kinds[lo:hi]=b'\3'*(hi-lo);matched+=1
                    else:rejected+=1
                evidence.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),matched_rows=matched,rejected_rows=rejected))
        if component:
            for claim in component['claims']:
                kind=claim['kind'];label=5 if 'compressed' in kind else 4 if kind=='accelerator_command_stream' else None
                if label:
                    lo,hi=claim['range']
                    if not 0<=lo<hi<=size:raise ValueError('invalid structural classification span')
                    kinds[lo:hi]=bytes([label])*(hi-lo)
        totals=Counter({v:0 for v in LABELS.values()});runs=[]
        for row in detail['regions']:
            if row['category']!='pulled_unclassified':continue
            start=row['start'];end=row['end'];last=kinds[start];cursor=start
            for offset in range(start,end):
                value=kinds[offset];totals[LABELS[value]]+=1
                if value!=last:
                    runs.append(dict(start=cursor,end=offset,evidence_class=LABELS[last]));cursor=offset;last=value
            runs.append(dict(start=cursor,end=end,evidence_class=LABELS[last]))
        if sum(totals.values())!=detail['totals']['pulled_unclassified']:raise ValueError('unresolved partition does not reconcile')
        result.append(dict(payload=name,unclassified_bytes=sum(totals.values()),evidence_classes=dict(totals),regions=runs))
    totals=Counter({v:0 for v in LABELS.values()})
    for item in result:totals.update(item['evidence_classes'])
    value=dict(schema=1,policy='Exclusive refinement of pulled_unclassified only. Priority: structural mixed/accelerator, byte-verified disassembly, function envelope, prior candidate correspondence, no finer evidence. These are evidence classes, not confirmed executable/non-executable classifications.',totals=dict(totals),evidence=evidence,payloads=result)
    (stage/'remaining-classification.json').write_text(json.dumps(value,indent=2)+'\n')
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['payload','start','end','bytes','evidence_class'])
    for item in result:
        for row in item['regions']:writer.writerow([item['payload'],row['start'],row['end'],row['end']-row['start'],row['evidence_class']])
    (stage/'remaining-classification.csv').write_text(out.getvalue())
    return {k:v for k,v in value.items() if k!='payloads'}
