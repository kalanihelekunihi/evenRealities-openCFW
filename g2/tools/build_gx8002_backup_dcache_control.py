# SPDX-License-Identifier: MIT
"""Build pinned CSI data-cache enable for backup firmware on macOS."""
import json,subprocess
from build_gx8002_backup_cache_initialize import build as authenticate
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    upstream=authenticate();out=ROOT/'build/gx8002-backup-dcache-control';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    rows=[];objects=[];script='SECTIONS {\n'
    for name,symbol,offset,size in (('enable','gx_dcache_enable',0x3d6d4,32),('disable_upstream','open_cfw_gx8002_dcache_disable_upstream',0x3d6f4,36)):
        source=ROOT/f'components/shared/gx8002/runtime_gx8002_dcache_{name}.c';obj=out/(name+'.o');objects.append(str(obj))
        command=[pre+'gcc','-O2','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections']
        for directory in ('arch/soc/grus/include','include/utility','include/utility/libc'):command+=['-isystem',str(sdk/directory)]
        subprocess.run([*command,'-c',str(source),'-o',str(obj)],check=True)
        section='.dcache_'+name;address=offset+0x10000000-0x38940
        script+=f'{section} {address:#x} : {{ {obj}(.text.{symbol}) }}\nASSERT(SIZEOF({section}) <= {size}, "cache control overflow")\n'
        rows.append({'section':section,'offset':offset,'envelope_bytes':size,'source_sha256':sha(source.read_bytes())})
    script+='}\ngx_dcache_disable = open_cfw_gx8002_dcache_disable_upstream;\n'
    (out/'control.ld').write_text(script);path=out/'control.elf'
    subprocess.run([pre+'ld','-T',str(out/'control.ld'),*objects,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'cache');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    for row in rows:
        sec=next(s for s in elf.sections if s['name']==row['section']);body=elf.contents(sec)
        if row['section']=='.dcache_enable': assert body==stock[row['offset']:row['offset']+row['envelope_bytes']]
        row.update(bytes=len(body),stock_byte_exact=body==stock[row['offset']:row['offset']+len(body)])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'control.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'upstream_dependencies':upstream['upstream_dependencies'],'sections':rows,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Pinned CSI source reproduces the enable body including synchronization instructions. Actual cache coherency and whole-firmware behavior remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dcache-control.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':print(build())
