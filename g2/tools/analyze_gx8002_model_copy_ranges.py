#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only copy access geometry, preserving ordered tensor element semantics."""
import json
from collections import Counter
from itertools import product
from analyze_gx8002_model_command_chain import analyze,ROOT

def inspect_copy(copy):
    extents=copy['extents'];indices=list(product(*(range(n) for n in extents)))
    accesses={}
    for role in ('source','destination'):
        base=copy[role];strides=copy[role+'_strides_elements']
        offsets=[base['offset']+2*sum(i*s for i,s in zip(index,strides)) for index in indices]
        accesses[role]=offsets
    source=accesses['source'];destination=accesses['destination']
    same_slot=copy['source']['base_slot']==copy['destination']['base_slot']
    hazards=[]
    if same_slot:
        # A two-byte write can alter a later two-byte source read, including
        # odd-byte overlap. Do not collapse strided copies to memcpy/memmove.
        for i,dst in enumerate(destination):
            for j in range(i+1,len(source)):
                if max(dst,source[j])<min(dst+2,source[j]+2):hazards.append([i,j])
    ranges={}
    for role,offsets in accesses.items():
        ranges[role]={'base_slot':copy[role]['base_slot'],'start':min(offsets) if offsets else None,'end_exclusive':max(offsets)+2 if offsets else None,'unique_elements':len(set(offsets))}
    return {'elements':len(indices),'ranges':ranges,'same_slot':same_slot,'write_before_later_read':hazards}

def analyze_ranges():
    chain=analyze();rows=[];maxima={};pairs=Counter()
    for command in chain['commands']:
        if 'copy' not in command:continue
        copy=command['copy'];geometry=inspect_copy(copy)
        rows.append({'command_offset':command['offset'],**geometry})
        pairs[(copy['source']['base_slot'],copy['destination']['base_slot'])]+=1
        for span in geometry['ranges'].values():
            if span['end_exclusive'] is not None:maxima[span['base_slot']]=max(maxima.get(span['base_slot'],0),span['end_exclusive'])
    return {'command_sha256':chain['command_sha256'],'copy_commands':rows,'slot_pairs':[{'source':s,'destination':d,'count':n} for (s,d),n in pairs.items()],'minimum_slot_bytes_from_copies':maxima,'hazardous_commands':sum(bool(r['write_before_later_read']) for r in rows),'source_admitted':False,'limits':['Only copy operations included. Slot sizes are lower bounds, not actual allocation sizes. Distinct slots may alias at runtime; cross-slot overlap is not excluded. No numeric operations, weights or hardware behavior reconstructed.']}
if __name__=='__main__':
    report=analyze_ranges();(ROOT/'docs/research/gx8002-model-copy-ranges.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ('copy_commands','limits')})
