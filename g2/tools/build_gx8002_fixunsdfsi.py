# SPDX-License-Identifier: MIT
"""Compile authenticated GCC unsigned-double conversion with runtime provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit='1e9b70447a8417f5c692370de4533e43d754e8fa';deps={}
    for name in ('libgcc/libgcc2.c','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip();deps[name]=authenticated_blob(gcc/name,blob).decode()
    original=deps['libgcc/libgcc2.c'];start=original.index('UWtype\n__fixunsdfSI (');end=original.index('\n#endif',start)
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\ntypedef uint32_t UWtype;\ntypedef int32_t Wtype;\ntypedef double DFtype;\n#define Wtype_MIN INT32_MIN\n'+original[start:end]
    out=ROOT/'build/gx8002-fixunsdfsi';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10209a6c : { *(.text.__fixunsdfSI) } }\n__gedf2 = 0x1020a420;\n__subdf3 = 0x1020a0cc;\n__fixdfsi = 0x1020a460;\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':56,'fits':len(data)<=56,'byte_exact':data==IMAGE.read_bytes()[0x12ff8:0x13030],'compiled_sha256':sha(data),'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-fixunsdfsi-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
