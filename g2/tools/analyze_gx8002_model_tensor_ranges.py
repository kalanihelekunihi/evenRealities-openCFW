#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tensor indexing geometry from decoded upstream loops; no numeric simulation."""
import json
from itertools import product
from analyze_gx8002_model_command_chain import analyze,ROOT

def geometry(tensor):
    rows={};extents=tensor['extents']
    for role in ('source_a','source_b','destination'):
        base=tensor[role];strides=tensor[role+'_strides_elements']
        if not all(extents):end=base['offset']
        else:end=base['offset']+2*sum((n-1)*s for n,s in zip(extents,strides))+2
        rows[role]={'base_slot':base['base_slot'],'start':base['offset'],'end_exclusive':end,'strides_elements':strides}
    return rows

def report():
    chain=analyze();rows=[];maxima={}
    for command in chain['commands']:
        if 'tensor_operands' not in command:continue
        tensor=command['tensor_operands'];ranges=geometry(tensor)
        rows.append({'command_offset':command['offset'],'operator':command['operator'],'arithmetic':tensor['arithmetic'],'extents':tensor['extents'],'ranges':ranges})
        for span in ranges.values():maxima[span['base_slot']]=max(maxima.get(span['base_slot'],0),span['end_exclusive'])
    return {'command_sha256':chain['command_sha256'],'commands':rows,'minimum_slot_bytes_from_tensor_ops':maxima,'source_admitted':False,'limits':['Tensor-operation-only access bounds; other operators excluded. Assumes non-sentinel operands and nonnegative decoded strides. Runtime aliasing and physical allocation sizes not proved. No floating-point results generated.']}
if __name__=='__main__':
    r=report();(ROOT/'docs/research/gx8002-model-tensor-ranges.json').write_text(json.dumps(r,indent=2)+'\n');print(r['minimum_slot_bytes_from_tensor_ops'])
