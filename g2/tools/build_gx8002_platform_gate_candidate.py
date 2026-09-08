#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile authenticated upstream GRUS clock logic without source admission."""
import json
import subprocess
from analyze_gx8002_upstream_objects import SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT
from verify_gx8002_analog_source import FLAGS


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    output=ROOT/'build/gx8002-platform-gate';output.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_platform_gate.c'
    dependencies=[]
    for name in ('arch/soc/grus/include/clk_priv.h','arch/soc/grus/include/base_addr.h',
                 'include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        dependencies.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    config=output/'autoconf.h';config.write_text('#define CONFIG_ARCH_GRUS 1\n')
    compiler=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-delete-null-pointer-checks']
    obj=output/'gate.o'
    subprocess.run([str(compiler),*flags,'-I',str(output),'-isystem',str(sdk/'arch/soc/grus/include'),
                    '-isystem',str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj))
    sections=[{'section':s['name'],'bytes':s['size'],'sha256':sha(elf.contents(s)),
               'relocations':len(elf.relocations(s['index']))}
              for s in elf.sections if s['size'] and s['flags']&2]
    report={'sdk_commit':SDK_COMMIT,'upstream_dependencies':dependencies,'flags':flags,
            'source_sha256':sha(source.read_bytes()),'configuration':config.read_text(),
            'sections':sections,'source_admitted':False,'firmware_bytes_emitted':0,
            'limits':['Unlinked candidate; stock gate envelope is 256 bytes at package 0x17094.',
                      'Module lookup, tables, jump tables and MMIO behavior require qualification.',
                      'No hardware qualification or complete source-only claim.']}
    (ROOT/'docs/research/gx8002-platform-gate-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build(),indent=2))
