#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reauthenticate existing instruction evidence; never generate disassembly."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from source_providers import ROOT
sys.path.insert(0,str(ROOT/'tools/cutting'))
import firmware_cut as cut


def digest(data):return hashlib.sha256(data).hexdigest()


def main():
    stocks={m['payload']:cut.official_bytes(m) for m in cut.load_manifests()}
    mapping={'apollo_bootloader':'g2-apollo-bootloader','apollo_main':'g2-apollo-main','case':'g2-case'}
    arrays={name:bytearray(len(data)) for name,data in stocks.items() if name.startswith('g2-')}
    folder=ROOT/'g2/evidence/instructions-current'
    ledger=folder/'instruction-ledger.jsonl';cache={};counts=Counter()
    with ledger.open() as stream:
        for line in stream:
            row=json.loads(line);name=mapping.get(row['payload'])
            if not name:continue
            key=(row['artifact'],row['artifact_sha256'])
            if key not in cache:cache[key]=digest((ROOT/key[0]).read_bytes())==key[1]
            if not cache[key]:counts['artifact_changed']+=1;continue
            lo,hi=row['payload_range']
            if not 0<=lo<hi<=len(stocks[name]) or digest(stocks[name][lo:hi])!=row['bytes_sha256']:
                counts['byte_mismatch']+=1;continue
            arrays[name][lo:hi]=b'\1'*(hi-lo);counts['matched_instruction_rows']+=1
    arc=ROOT/'g2/research/corpus/em9305/objdump/open-2026-09-29/em9305-0x302400-0x335BC8.s'
    for line in arc.read_text().splitlines():
        match=re.match(r'^\s*([0-9a-f]+):\s*([0-9a-f ]+)\t+([^\s]+)',line)
        if not match or match[3].startswith('.') or match[3] in ('(bad)','???','invalid'):continue
        data=b''.join(bytes.fromhex(t)[::-1] for t in match[2].split());lo=int(match[1],16)-0x301fdc;hi=lo+len(data)
        if 0<=lo<hi<=len(stocks['g2-em9305']) and stocks['g2-em9305'][lo:hi]==data:
            arrays['g2-em9305'][lo:hi]=b'\1'*(hi-lo);counts['matched_arc_rows']+=1
        else:counts['arc_byte_mismatch']+=1
    spans=[]
    for name,array in arrays.items():
        start=None
        for offset,value in enumerate([*array,0]):
            if value and start is None:start=offset
            if not value and start is not None:
                spans.append(dict(payload=name,start=start,end=offset,sha256=digest(stocks[name][start:offset])));start=None
    result=dict(schema=1,qualification='Byte-verified decoder observations only; not confirmed executable classification or source completeness.',evidence=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in (ledger,folder/'instruction-artifact-manifest.jsonl',arc)],artifacts_verified=sum(cache.values()),outcomes=dict(counts),payload_sha256={k:digest(v) for k,v in stocks.items() if k.startswith('g2-')},spans=spans)
    output=ROOT/'tools/build/disassembly-evidence.json';output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(outcomes=dict(counts),artifacts_verified=sum(cache.values()),bytes=sum(r['end']-r['start'] for r in spans))))

if __name__=='__main__':main()
