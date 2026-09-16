#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed DW SPI quick_transfer call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_clock_gate':0x10003be8}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-dw-spi-transfer';out.mkdir(exist_ok=True);rel='drivers_lib/spi/dw_spi/spi_master_v3.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/spi.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('include/utility/list.h','include/utility/types.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'dw-spi-quick-transfer-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_dw_spi_transfer.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-jump-tables']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'dw-spi-quick-transfer-candidate.o')],check=True)
    script=out/'dw-spi-quick-transfer-candidate.ld';script.write_text('SECTIONS { .text 0x100082a8 : { *(.text.open_cfw_gx8002_dw_spi_quick_transfer) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'dw-spi-quick-transfer-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'dw-spi-quick-transfer-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('DW SPI quick_transfer stock/link')
    (out/'dw-spi-quick-transfer-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_dw_spi_quick_transfer','section_name':'.text','package_offset':0x40be8,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':656,'stock_sha256':sha(stock[0x40be8:0x40e78]),'fits':len(payload)<=656,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    (ROOT/'docs/research/gx8002-backup-dw-spi-transfer-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
