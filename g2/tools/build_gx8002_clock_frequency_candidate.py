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
    output=ROOT/'build/gx8002-clock-frequency';output.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_clock_frequency.c'
    dependencies=[]
    for name in ('arch/soc/grus/include/clk_priv.h','arch/soc/grus/include/base_addr.h',
                 'include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        dependencies.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    original=(sdk/'arch/soc/grus/include/clk_priv.h').read_text()
    call='unsigned int div = __module_get_div(info);'
    declaration='static inline unsigned int _clk_get_module_frequence(GX_CLOCK_MODULE module)'
    if original.count(call)!=1 or original.count(declaration)!=1:
        raise ValueError('Upstream frequency adaptation anchors changed')
    adapted=original.replace(call,'unsigned int div = open_cfw_gx8002_clock_divider(info.param, info.base_addr);')
    adapted=adapted.replace(declaration,'extern unsigned int open_cfw_gx8002_clock_divider(const GX_CLOCK_MODULE_PARAM *, unsigned int);\n\n'+declaration)
    (output/'clk_priv_frequency.h').write_text(adapted)
    config=output/'autoconf.h';config.write_text('#define CONFIG_ARCH_GRUS 1\n')
    compiler=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-delete-null-pointer-checks']
    obj=output/'frequency.o'
    subprocess.run([str(compiler),*flags,'-isystem',str(output),'-isystem',str(sdk/'arch/soc/grus/include'),
                    '-isystem',str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj))
    sections=[{'section':s['name'],'bytes':s['size'],'sha256':sha(elf.contents(s)),
               'relocations':len(elf.relocations(s['index']))}
              for s in elf.sections if s['size'] and s['flags']&2]
    report={'sdk_commit':SDK_COMMIT,'upstream_dependencies':dependencies,'flags':flags,
            'source_sha256':sha(source.read_bytes()),'adapted_header_sha256':sha(adapted.encode()),'adaptation':'Only frequency divider call uses stock two-register ABI; upstream arithmetic unchanged','configuration':config.read_text(),
            'sections':sections,'source_admitted':False,'firmware_bytes_emitted':0,
            'limits':['Unlinked candidate; frequency entry is package 0x17224/runtime 0x10025210; placement pending.',
                      'Module lookup, tables, jump tables and MMIO behavior require qualification.',
                      'No hardware qualification or complete source-only claim.']}
    (ROOT/'docs/research/gx8002-clock-frequency-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build(),indent=2))
