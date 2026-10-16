#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Recover scalar bindings at independently named entries from compiled objects.

This is discovery only. Production always recompiles and relinks every selected
provider. Short functions need a named anchor, never a relaxed whole-image scan.
"""
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from source_providers import ROOT,functions,link_function,sha
from match_compiled import match
import sys
sys.path.insert(0,str(ROOT/'tools/cutting'))
import firmware_cut as cut


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compilation',type=Path,action='append',required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():p.error('choose a fresh output directory')
    a.out.mkdir(parents=True)
    stocks={m['payload']:cut.official_bytes(m) for m in cut.load_manifests()}
    plan=json.loads((ROOT/'tools/build/source-plan.json').read_text());assets=json.loads((ROOT/'tools/build/resources.json').read_text())
    occupied=defaultdict(list)
    for u in plan['units']:
        for r in u['regions']:occupied[r['payload']].append((r['start'],r['end']))
    for r in assets:occupied[r['payload']].append((r['start'],r['end']))
    names={};entries={};bases={'g2-apollo-main':0x437fe0,'g2-apollo-bootloader':0x410000,'g2-case':0x8000000-32,'g2-touch':0x3300-32,'r1-application':0x27000}
    for payload,base in bases.items():
        if payload=='r1-application':
            rows=list(csv.DictReader(io.StringIO((ROOT/'r1/research/source-build/function-frontier.csv').read_text())))
            names[payload]=defaultdict(set)
            for r in rows:
                if r['image']=='application' and r['candidate_symbol']:names[payload][r['candidate_symbol']].add(int(r['entry'],16)-base)
            entries[payload]={int(r['entry'],16)-base for r in csv.DictReader(io.StringIO((ROOT/'r1/research/decompilation/application/functions.csv').read_text()))}
        else:
            symbolfile={'g2-apollo-main':'apollo_main','g2-apollo-bootloader':'bootloader','g2-case':'case','g2-touch':'touch'}[payload]
            rows=list(csv.DictReader(io.StringIO((ROOT/f'g2/symbols/{symbolfile}.tsv').read_text()),delimiter='\t'));names[payload]=defaultdict(set)
            for r in rows:names[payload][r['name']].add(int(r['address'],16)-base)
            entries[payload]={int(r['address'],16)-base for r in rows}
    outcomes=Counter();input_cache={};selected=[]
    for directory in a.compilation:
        for path in sorted(directory.glob('*/unit.json')):
            unit=json.loads(path.read_text());folder=path.parent;payload=unit['payload']
            if payload not in bases:continue
            receipt=json.loads((folder/'receipt.json').read_text())
            valid=True
            for source,digest in receipt['inputs'].items():
                if source not in input_cache:input_cache[source]=sha(source)
                if input_cache[source]!=digest:valid=False;break
            if not valid or sha(folder/'unit.o')!=receipt['object_sha256']:
                outcomes['stale_discovery_inputs']+=1;continue
            regions=[]
            for f in functions(folder/'unit.o'):
                if not f['relocations']:continue
                targets=set(names[payload].get(f['symbol'],set()));suffix=re.search(r'_([0-9a-fA-F]{6,8})$',f['symbol'])
                if suffix and int(suffix[1],16)-bases[payload] in entries[payload]:targets.add(int(suffix[1],16)-bases[payload])
                if len(targets)!=1:continue
                lo=next(iter(targets));hi=lo+f['size']
                if any(lo<right and left<hi for left,right in occupied[payload]):continue
                found=match(f,stocks[payload],entries[payload],bases[payload],anchored_entry=lo)
                if not found:outcomes['fixed_instructions_or_relocations_differ']+=1;continue
                try:data,_=link_function(folder/'unit.o',f,found['address'],found['bindings'],a.out/f'{len(selected):04d}-{f["symbol"]}')
                except ValueError:outcomes['link_not_closed']+=1;continue
                if data!=stocks[payload][lo:hi]:outcomes['linked_bytes_differ']+=1;continue
                found.update(payload=payload,symbol=f['symbol'],sha256=hashlib.sha256(data).hexdigest(),evidence=unit['evidence'])
                regions.append(found);selected.append(dict(source=unit['source'],**found));occupied[payload].append((lo,hi));outcomes['exact_selected']+=1
            if regions:plan['units'].append(dict({k:unit[k] for k in ('source','argv','compiler_path','compiler_sha256') if k in unit},regions=regions))
    (a.out/'source-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (a.out/'qualification.json').write_text(json.dumps(dict(outcomes=dict(outcomes),selected=selected),indent=2)+'\n')
    print(json.dumps(dict(outcomes=dict(outcomes),new_bytes=sum(r['end']-r['start'] for r in selected))))

if __name__=='__main__':main()
