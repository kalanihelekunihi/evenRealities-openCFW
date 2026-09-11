# SPDX-License-Identifier: MIT
"""Compile source-authored board pin diagnostic and compare its exact extent."""
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_logging import check_paths
from verify_gx8002_analog_source import FLAGS


def validate(data):
    if data != b'pin %d set error!\n\0':
        raise ValueError('Board pin diagnostic text/terminator')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    out = Path(output) if output else ROOT/'build/gx8002-board'
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT/'components/shared/gx8002/runtime_gx8002_board_pin_initialize_error.c'
    prefix = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out/'board-pin-initialize-error.o'
    flags = ['-Os', *FLAGS[1:]]
    subprocess.run([prefix+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    elf = Elf32(obj.read_bytes(),str(obj))
    symbol = 'open_cfw_gx8002_board_pin_initialize_error'
    section = next(s for s in elf.sections if s['name']=='.rodata.'+symbol)
    data = elf.contents(section)
    validate(data)
    if section['flags']&4 or elf.relocations(section['index']):
        raise ValueError('Board pin diagnostic section')
    stock = IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or stock[0x14323:0x14323+len(data)]!=data:
        raise ValueError('Board pin diagnostic stock extent')
    return {'functions':[{'symbol':symbol,'section_name':section['name'],
            'compiled_bytes':len(data),'compiled_sha256':sha(data),
            'ownership_kind':'generated_source_data','stock_occurrences':[{
                'symbol':symbol,'package_offset':0x14323,'bytes':len(data),
                'sha256':sha(data),'region':'image_a_xip_text'}]}],
            'source_sha256':sha(source.read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
            'flags':flags,'source_admitted':True,'hardware_qualified':False,
            'limits':['Experimental source diagnostic admission only. No board initialization or hardware proof.']}


if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-board-pin-initialize-error-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Source board pin diagnostic validated')
