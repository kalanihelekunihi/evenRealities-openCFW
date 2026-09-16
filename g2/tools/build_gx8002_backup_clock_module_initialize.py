# SPDX-License-Identifier: MIT
"""Build and compare the upstream normal module-source setup helper."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, sha
from build_gx8002_backup_cfft import FLAGS, Elf32, IMAGE, IMAGE_SHA
from verify_gx8002_memcpy_source import decode


def calls(code,start,stop,target):
    r={};result=[];pc=start
    for _ in range(100):
        if pc==stop:return result
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op=='bsr':
            assert int(args,0)==target;result.append([r['r0'],r['r1']]);r.clear()
        elif op=='push':assert args=='r15'
        elif op=='pop':assert args=='r15';return result
        else:raise ValueError((hex(pc),op,args))
        pc+=width
    raise ValueError('module call sequence bound')


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='boards/nationalchip/grus_gx8002_slight_1v/clock_board.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    source=authenticated_blob(sdk/rel,blob).decode();a=source.index('static void _clk_mod_normal_init(void)');b=source.index('static void _clk_mod_lowpower_init',a);function=source[a:b]
    adapted=function.replace('MODULE_SOURCE_ADC_32K','MODULE_SOURCE_ADC_SYS').replace('MODULE_SOURCE_PDM_OSC_1M','MODULE_SOURCE_PDM_SYS')
    out=ROOT/'build/gx8002-backup-clock-module-initialize';out.mkdir(exist_ok=True)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    path=out/'modules.c';path.write_text('#include <driver/gx_clock.h>\n'+adapted+'\nvoid open_cfw_gx8002_backup_clock_module_initialize(void) { _clk_mod_normal_init(); }\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'modules.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-I'+str(out),'-isystem',str(sdk/'include'),'-c',str(path),'-o',str(obj)],check=True)
    for header in ('include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h'):
        identity=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip();authenticated_blob(sdk/header,identity)
    ld=out/'modules.ld';ld.write_text('SECTIONS { .text 0x10018000 : { *(.text*) } }\ngx_clock_set_module_source = 0x100035c0;\n')
    elfpath=out/'modules.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),'modules');sec=next(s for s in elf.sections if s['name']=='.text')
    assembly=subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True);(out/'modules.disassembly.txt').write_text(assembly)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oldelf=Elf32(wrapper.read_bytes(),'stock');assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3bbf4','--stop-address=0x3bc8c',str(wrapper)],text=True))
    original=calls(old,0x3bbf4,0x3bc8c,0x3bf00);actual=calls(decode(assembly),0x10018000,None,0x100035c0)
    assert len(actual)==19 and original==actual, (original,actual)
    return {'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'function_sha256':sha(function.encode()),'adapted_function_sha256':sha(adapted.encode()),'adaptations':['ADC selects MODULE_SOURCE_ADC_SYS instead of ADC_32K','PDM selects MODULE_SOURCE_PDM_SYS instead of PDM_OSC_1M'],'elf_sha256':sha(elfpath.read_bytes()),'code_bytes':sec['size'],'ordered_module_sources':actual,'source_admitted':False,'limits':['Complete upstream-based module helper with explicit stock audio-source adaptations compiled and its 19 ordered call arguments matched to stock inline sequence. Module-setting helper effects are not executed here. Analysis placement only; complete clock initialization, PLL/resume branches and integration remain pending.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-backup-clock-module-initialize.json').write_text(json.dumps(result,indent=2)+'\n');print(result['code_bytes'],'source bytes;',len(result['ordered_module_sources']),'ordered calls matched')
