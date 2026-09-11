#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build and qualify the typed pin/function boot policy without binary input."""
import json,subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def validate(data):
    if len(data)!=26: raise ValueError('Default table length')
    for pin in range(13):
        if data[2*pin]!=pin or data[2*pin+1]!=(0 if pin==2 else 1):
            raise ValueError('Default pin/function policy')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    out=output or ROOT/'build/gx8002-board';out.mkdir(parents=True,exist_ok=True)
    rel='include/driver/gx_padmux.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_board_pin_defaults.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'board-pin-defaults.o';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));symbol='open_cfw_gx8002_board_pin_defaults'
    sec=next(s for s in elf.sections if s['name']=='.rodata.'+symbol);data=elf.contents(sec)
    validate(data)
    if sec['flags']&4 or elf.relocations(sec['index']):raise ValueError('Default table section/relocations')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or stock[0x142bc:0x142d6]!=data:raise ValueError('Default stock evidence mismatch')
    row={'symbol':symbol,'section_name':sec['name'],'compiled_bytes':26,'compiled_sha256':sha(data),
         'ownership_kind':'generated_source_data','stock_occurrences':[{'symbol':symbol,
         'package_offset':0x142bc,'bytes':26,'sha256':sha(data),'region':'image_a_xip_text'}]}
    return {'functions':[row],'sdk_commit':SDK_COMMIT,'header':{'path':rel,'blob':blob,'sha256':sha(header)},
            'source_sha256':sha(source.read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
            'flags':flags,'source_admitted':True,'hardware_qualified':False,
            'policy':'Pins 0..12 in ascending order; pin 2 uses function zero, all others function one.',
            'limits':['Typed table layout and policy only; hardware meaning/effects of selected functions are not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-defaults-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Validated 13 typed board pin defaults')
