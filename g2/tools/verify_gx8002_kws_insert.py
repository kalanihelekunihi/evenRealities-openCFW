#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit decoded activation insertion without claiming storage/whole-decoder closure."""
import json,shutil
from compare_gx8002_kws_insert import verify as compare,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();row=evidence['build']
    if not row['fits']:raise ValueError('activation insertion envelope')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-KWS-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/kws-insert-candidate.elf',output/'kws-insert.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'KwsStragegyInsertKwsActivation','section_name':'.text','compiled_bytes':row['compiled_bytes'],
      'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':'KwsStragegyInsertKwsActivation','package_offset':0x11f0c,
      'bytes':144,'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]}], 'evidence':evidence,
      'notice_sha256':sha(notice.read_bytes()),'manual_sha256':sha((ROOT/'build/csky-isa-manual.pdf').read_bytes()),
      'source_admitted':True,'hardware_qualified':False,'limits':['Insertion/update function only. Valid list counts0..8; negative-count logging preserved. Corrupted positive counts above8 are not safe storage. Same FP instruction/operand traces and both condition outcomes checked without physical FP qualification. State/message/remaining decoder are separate retained dependencies.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-kws-insert-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
