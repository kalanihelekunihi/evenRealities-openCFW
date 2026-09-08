#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the recovered MAX/standby TWS initialization control flow."""
import json,shutil
from compare_gx8002_tws import verify as compare,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();row=evidence['build']
    if not row['fits'] or not row['interface_compatibility_checked']:raise ValueError('TWS admission')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-TWS-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/tws-candidate.elf',output/'tws.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'open_cfw_gx8002_tws_init','section_name':'.text','compiled_bytes':row['compiled_bytes'],
      'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_tws_init','package_offset':0x11bfc,
      'bytes':108,'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]}],
      'evidence':evidence,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
      'limits':['Initialization control flow only. MAX decoder and audio/KWS services, TWS callbacks, message and state are separately retained dependencies. No complete TWS or whole-device claim.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-tws-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
