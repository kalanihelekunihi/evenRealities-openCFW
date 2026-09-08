#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit reconstructed byte-normalizing fast memset with explicit size limits."""
import json,shutil
from compare_gx8002_memset import verify as compare,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();row=evidence['build']
    if not row['fits']:raise ValueError('memset envelope')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-LIBC-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/memset-candidate.elf',output/'memset.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'open_cfw_gx8002_memset','section_name':'.text','compiled_bytes':row['compiled_bytes'],
      'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_memset','package_offset':0x12f58,
      'bytes':160,'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]}], 'evidence':evidence,'notice_sha256':sha(notice.read_bytes()),
      'manual_sha256':sha((ROOT/'build/csky-isa-manual.pdf').read_bytes()),'source_admitted':True,'hardware_qualified':False,
      'limits':['Source fill implementation only. Signed stock block tests preserved, including bounded negative-count tail. Large positive paths checked at loop prefixes; no valid-memory claim for arbitrary32-bit counts/addresses, no hardware/MMIO/timing qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-memset-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
