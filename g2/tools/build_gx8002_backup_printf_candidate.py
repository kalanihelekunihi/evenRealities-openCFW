# SPDX-License-Identifier: MIT
"""Authenticate and compile SDK Paland printf for backup-image assessment."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-printf';out.mkdir(exist_ok=True)
    (out/'autoconf.h').write_text('/* Candidate configuration: SDK default printf features. */\n')
    records=[]
    for relative in ('utility/libc/printf.c','include/utility/libc/printf.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',f'{SDK_COMMIT}:{relative}'],text=True).strip()
        data=authenticated_blob(sdk/relative,blob);records.append({'path':relative,'git_blob':blob,'sha256':sha(data)})
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-I',str(out),'-I',str(sdk/'include/utility/libc'),'-c',str(sdk/'utility/libc/printf.c'),'-o',str(out/'printf.o')]
    subprocess.run(command,check=True);elf=Elf32((out/'printf.o').read_bytes(),'printf')
    (out/'printf.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(out/'printf.o')],text=True))
    report={'sdk_commit':SDK_COMMIT,'upstream_files':records,'command':command,'sections':[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0],'source_admitted':False,'limits':['SDK Paland printf compiled unchanged with default features. Stock entry signature/callback pattern supports this family, not exact version identity. Placement, configuration, decoded equivalence and output dependencies remain unverified.']}
    (ROOT/'docs/research/gx8002-backup-printf-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(build())
