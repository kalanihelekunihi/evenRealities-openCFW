# SPDX-License-Identifier: MIT
"""Recreate PLL and source-selection data from pinned upstream declarations."""
import json
import re
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, sha
from build_gx8002_backup_cfft import FLAGS, Elf32, IMAGE, IMAGE_SHA


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='boards/nationalchip/grus_gx8002_slight_1v/clock_board.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    text=authenticated_blob(sdk/rel,blob).decode();declarations=[]
    for name in ('clk_src_xtal_table','clk_src_osc_table','pll'):
        matches=re.findall(r'static\s+GX_CLOCK_(?:SOURCE_TABLE|PLL)\s+'+name+r'(?:\[\])?\s*=\s*\{.*?\};',text,re.S)
        assert len(matches)==(2 if name=='pll' else 1)
        declarations.append(matches[0].replace('static ', '',1))
    marker='int stage2_trim_done = -1;';assert marker in text
    out=ROOT/'build/gx8002-backup-clock-source-data';out.mkdir(exist_ok=True)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    src=out/'data.c';src.write_text('#include <driver/gx_clock.h>\n'+'\n'.join(declarations)+'\n'+marker+'\n')
    headers=[]
    for h in ('include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h'):
        identity=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+h],text=True).strip();authenticated_blob(sdk/h,identity);headers.append({'path':h,'blob':identity})
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'data.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-I'+str(out),'-isystem',str(sdk/'include'),'-c',str(src),'-o',str(obj)],check=True)
    specs=[('pll',0x200168c0,56),('stage2_trim_done',0x200168f8,4),('clk_src_xtal_table',0x200168fc,80),('clk_src_osc_table',0x2001694c,80)]
    ld=out/'data.ld';ld.write_text('SECTIONS {\n'+''.join(f'.{name} {address:#x} : {{ *(.data.{name}) }}\n' for name,address,size in specs)+'}\n')
    path=out/'data.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'clock data');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size in specs:
        sec=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(sec);off=address-0x20003000+0x3b940
        assert sec['address']==address and len(body)==size and not elf.relocations(sec['index'])
        assert body==stock[off:off+size],name
        rows.append({'symbol':name,'address':address,'package_offset':off,'bytes':size,'sha256':sha(body)})
    return {'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'headers':headers,'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'sections':rows,'source_data_bytes':sum(r['bytes'] for r in rows),'source_admitted':False,'limits':['Complete declarations compile to stock-identical data; firmware bytes used only as comparison oracle. Selected upstream 50 MHz PLL branch. Runtime mutation, incoming references and integration remain pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-clock-source-data.json').write_text(json.dumps(r,indent=2)+'\n');print(r['source_data_bytes'],'source-generated clock data bytes match stock')
