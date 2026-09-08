#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit reconstructed resume initializer and its source-defined zero input."""
import contextlib,io,json,shutil
from compare_gx8002_flash_full import verify as compare,ROOT
from analyze_gx8002_upstream_objects import IMAGE,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):comparison=compare()
    row=comparison['selection']['build'];constant=row['configuration_constant']
    if not row['fits'] or comparison['candidate_frame_bytes']!=comparison['stock_frame_bytes']:raise ValueError('resume envelope/frame')
    symbol='open_cfw_gx8002_flash_initialize';stock=IMAGE.read_bytes()
    functions=[{'symbol':symbol,'section_name':'.text','compiled_bytes':row['compiled_bytes'],
        'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':symbol,
        'package_offset':row['package_offset'],'bytes':208,'sha256':sha(stock[0x16604:0x166d4]),'region':'image_a_sram_text'}]},
        {'symbol':'configuration.0','section_name':constant['section'],'ownership_kind':'generated_source_data',
        'compiled_bytes':4,'compiled_sha256':constant['sha256'],'stock_occurrences':[{'symbol':'configuration.0',
        'package_offset':constant['package_offset'],'bytes':4,'sha256':constant['stock_sha256'],'region':'image_a_sram_text'}]}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/flash.elf',output/'flash.elf')
    return {'functions':functions,'evidence':comparison,
        'platform_config_source_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_platform_config.c').read_bytes()),
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Operation9 uses a source-defined read-only zero input instead of a stack local; its recovered implementation reads without modifying or retaining the pointer. Full decoded traces model returning helpers. Complete startup composition and physical hardware remain unqualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
