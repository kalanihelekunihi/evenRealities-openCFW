#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit mode control flow; callbacks and mode objects remain separate work."""
import json, shutil
from compare_gx8002_mode import verify as compare, ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths
def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();functions=[]
    for row in evidence['build']['functions']:
        if not row['fits']:raise ValueError('mode envelope')
        functions.append({'symbol':row['symbol'],'section_name':row['section_name'],'compiled_bytes':row['compiled_bytes'],
          'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],
          'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-MODE-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/mode-candidate.elf',output/'mode.elf')
        shutil.copyfile(notice,output/notice.name)
    return {'functions':functions,'evidence':evidence,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
            'limits':['Pinned upstream mode types and adapted init/tick control flow. Mode information objects, list, BSS state and callbacks remain separately retained; no complete mode or hardware qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-mode-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
