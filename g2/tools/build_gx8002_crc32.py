# SPDX-License-Identifier: MIT
"""Compile pinned Nationalchip/zlib CRC source on macOS without binary extraction."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'; commit='8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5'
    assert subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()==commit
    path=sdk/'base/src/crc32.c';source=path.read_bytes()
    assert source==subprocess.check_output(['git','-C',str(sdk),'show',commit+':base/src/crc32.c'])
    out=ROOT/'build/gx8002-crc32';out.mkdir(exist_ok=True)
    # Supply only the platform types and little-endian identity conversions.
    (out/'common.h').write_text('#include <stdint.h>\n#include <stddef.h>\n#define cpu_to_le32(x) (x)\n#define le32_to_cpu(x) (x)\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text.no_comp 0x102097f4 : { *(.text.crc32_no_comp) } .text.crc32 0x102098a8 : { *(.text.crc32) } .rodata.crc_table 0x1020b908 : { *(.rodata.crc_table) } }\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,offset,size in (('.text.no_comp',0x12d80,180),('.text.crc32',0x12e34,12),('.rodata.crc_table',0x14e94,1024)):
        section=next(s for s in elf.sections if s['name']==name);data=elf.contents(section)
        rows.append({'section':name,'compiled_bytes':len(data),'envelope_bytes':size,'fits':len(data)<=size,'byte_exact':data==stock[offset:offset+size],'compiled_sha256':sha(data)})
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'upstream_commit':commit,'upstream_path':'base/src/crc32.c','upstream_sha256':sha(source),'flags':flags,'sections':rows,'source_admitted':False,'limits':['Pinned source candidate; decoded behavioral and ownership qualification outstanding.']}
    (ROOT/'docs/research/gx8002-crc32-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
