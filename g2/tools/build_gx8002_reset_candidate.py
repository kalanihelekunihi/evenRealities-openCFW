#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a source reset entry with authenticated upstream provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';deps=[]
    for relative in ('arch/cpu/csky/ck804/start.S','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
        deps.append({'path':relative,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/relative,blob))})
    out=ROOT/'build/gx8002-board';source=ROOT/'components/shared/gx8002/runtime_gx8002_reset_entry.S'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-mcpu=ck804ef','-mhard-float']
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'reset-entry.o')],check=True)
    script=out/'reset-entry.ld';script.write_text('SECTIONS { .text 0x10023500 : { *(.text.open_cfw_gx8002_reset_entry) } }\nopen_cfw_gx8002_initial_stack = 0x2002f7fc;\nopen_cfw_gx8002_system_initialize = 0x1002354c;\nopen_cfw_gx8002_main = 0x10026314;\n')
    elfpath=out/'reset-entry.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'reset-entry.o'),'-o',str(elfpath)],check=True)
    e=Elf32(elfpath.read_bytes(),str(elfpath));s=next(x for x in e.sections if x['name']=='.text');b=e.contents(s)
    if e.relocations(s['index']) or any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved reset')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if len(b)>40:raise ValueError('reset envelope')
    (out/'reset-entry.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sha(source.read_bytes()),'flags':flags,
      'compiled_bytes':len(b),'compiled_sha256':sha(b),'byte_exact':b==stock[0x15514:0x1553c],
      'source_admitted':False,'limits':['Main remains a separate retained dependency. Reset control/register/call sequence needs decoded checks; no full boot qualification.']}
    (ROOT/'docs/research/gx8002-reset-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes'],report['byte_exact']);return report
if __name__=='__main__':build()
