#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile backup OTP-read candidate; behavior qualification is still pending."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_otp_read',0x40328,492)]


def build():
    out=ROOT/'build/gx8002-backup-flash-otp-read';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_flash_otp_read.c'
    flags=['-Os','-fira-algorithm=priority',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'otp-read.o')],check=True)
    script=out/'otp-read.ld'
    script.write_text('open_cfw_gx8002_flash_state = 0x20016d60;\nopen_cfw_gx8002_flash_wait_ready = 0x10007350;\nSECTIONS {\n'+''.join(f'.text.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'otp-read.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'otp-read.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved otp-read symbol')
    allocated=[s for s in e.sections if s['flags']&2 and s['size']]
    if len(allocated)!=1 or allocated[0]['name']!='.text.flash_otp_read':raise ValueError('unexpected OTP allocation')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved otp-read relocation')
        payload=e.contents(sec)
        if len(payload)>size or sec['address']!=offset-0x38940+0x10000000:raise ValueError('backup OTP placement overflow')
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'otp-read-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'state_header_sha256':sha((source.parent/'runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,'analysis_only_overlapping_sections_allowed':False,
            'limits':['Candidate only: backup width snapshots, register-shift semantics, controller effects and shared ready-wait substitution require decoded qualification. Not linked into startup or any full image.',
                      'No physical flash qualification.']}
    (ROOT/'docs/research/gx8002-backup-otp-read-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
