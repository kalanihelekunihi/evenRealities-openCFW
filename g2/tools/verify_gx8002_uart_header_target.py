# SPDX-License-Identifier: MIT
"""Finite decoded target checks for the upstream receive-header probe."""
import json
from itertools import product
from analyze_gx8002_upstream_objects import ROOT, sha
from build_gx8002_uart_header_upstream_probe import build
from execute_gx8002_uart_header_probe import execute


def verify():
    probe=build();cases=0
    for port,count,length,valid in product(range(2),range(4,15),range(14),(False,True)):
        payload=bytes((i*29+7)&255 for i in range(length))
        copied=min(length,14-count)
        header=bytearray([0xa5]*14)
        header[count:count+copied]=payload[:copied]
        crc=int.from_bytes(header[10:14],'little')
        supplied=crc if valid else crc^1
        complete=count+copied==14
        if complete and not valid:header[:4]=bytes(4)
        expected={'result':(1 if valid else 0xffffffff) if complete else 0,
                  'header':bytes(header),'count':4 if complete else count+copied,
                  'remaining':length-copied,
                  'consumed_pointer':copied if length-copied else 0,
                  'crc_calls':[(0,10)] if complete else []}
        actual=execute(port,count,payload,supplied)
        if actual!=expected:raise ValueError((port,count,length,valid,actual,expected))
        cases+=1
    return {'probe':probe,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'interpreter_sha256':sha((ROOT/'tools/execute_gx8002_uart_header_probe.py').read_bytes()),
            'limits':['Source target only; finite valid header counter states with modeled CRC results. Saved-register values modeled outside stack memory. Stock inlined path comparison and whole receive callback remain pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-header-target-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Header target cases:',report['decoded_cases'])
