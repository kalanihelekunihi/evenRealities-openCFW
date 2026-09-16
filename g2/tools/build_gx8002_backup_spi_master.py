# SPDX-License-Identifier: MIT
"""Build source SPI-master storage using authenticated upstream type headers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-spi-master';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';headers={}
    for rel in ('include/driver/spi.h','include/utility/list.h','include/utility/types.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        headers[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (out/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_spi_master.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-I'+str(out),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'master.o')],check=True)
    (out/'master.ld').write_text('SECTIONS { .spi_master 0x20017680 : { *(.bss.open_cfw_gx8002_backup_spi_master) } }\n')
    path=out/'master.elf';subprocess.run([pre+'ld','-T',str(out/'master.ld'),str(out/'master.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'master');alloc=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(alloc)==1
    s=alloc[0];assert (s['address'],s['size'],s['type'])==(0x20017680,36,8)
    assert 0x20017090<=s['address'] and s['address']+s['size']<=0x2002d79c
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'sdk_commit':SDK_COMMIT,'headers':headers,'source_sha256':sha(source.read_bytes()),'address':s['address'],'bytes':36,'reset_bss':True,'source_admitted':False,'limits':['Storage/type verification; probe/list behavior and physical operation qualified separately. Driver context is not owned by this record.']}
    (ROOT/'docs/research/gx8002-backup-spi-master.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['bytes'])
