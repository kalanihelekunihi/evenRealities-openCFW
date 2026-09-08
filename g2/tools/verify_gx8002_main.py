#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit pinned-upstream main control flow with separately qualified services."""
import contextlib,io,json,shutil
from compare_gx8002_main import verify as compare,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=compare()
    row=evidence['build']
    if not row['fits']:raise ValueError('main envelope')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-MAIN-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/main-candidate.elf',output/'main.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'open_cfw_gx8002_main','section_name':'.text','compiled_bytes':row['compiled_bytes'],
        'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_main',
        'package_offset':row['package_offset'],'bytes':44,'sha256':row['stock_sha256'],'region':'image_a_sram_text'}]}],
        'evidence':evidence,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
        'limits':['Main loop adapted from pinned MIT upstream with TWS mode. App-event initialization/tick already have source; LvpSystemInit, LvpInitMode, LvpModeTick and LvpSystemDone remain separate retained dependencies. No complete startup or hardware claim.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-main-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
