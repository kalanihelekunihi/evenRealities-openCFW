# SPDX-License-Identifier: MIT
"""Build upstream-derived KWS runner against authenticated GRUS ABI headers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('include/driver/gx_snpu.h','include/lvp_context.h','include/lvp_attr.h','include/lvp_buffer.h','include/vui/ctc_model.h','lvp/common/snpu_engine/lvp_kws.c','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);deps.append({'path':rel,'blob':blob,'sha256':sha(data)})
    config=out/'kws-run-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_run.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    path=out/'kws-run.o';subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'kws run');section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_kws_run')
    bindings={name:address+0x1000dfec for name,address in {
        'LvpGetFeatsBuffer':0x1f8eb8,'LvpGetLogfbankBuffer':0x1f8ec0,
        'LvpGetPcmFrameNumPerContext':0x1f8f64,'gx_dcache_invalid_range':0x1761c,
        'memmove':0x1f8c58,'memcpy':0x1774c,'gx_dcache_clean_range':0x17678,
        'LvpGetContext':0x1f8edc,'LvpCTCModelInitSnpuTask':0x1fac3c,
        'LvpCTCModelGetSnpuFeatsBuffer':0x1fac7c,'LvpCTCModelGetSnpuStateBuffer':0x1fac80,
        'LvpCTCModelGetSnpuFeatsDim':0x1fac88,'gx_snpu_run_task':0x1f7d74}.items()}
    bindings['open_cfw_gx8002_audio_completion_forward']=0x100260d0
    script=out/'kws-run.ld';script.write_text('SECTIONS { .text 0x100260e4 : { *(.text.open_cfw_gx8002_kws_run) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    linked=out/'kws-run.elf';subprocess.run([pre+'ld','-T',str(script),str(path),'-o',str(linked)],check=True)
    image=Elf32(linked.read_bytes(),'linked KWS runner');text=next(s for s in image.sections if s['name']=='.text')
    assert not image.relocations(text['index']) and not any(s['name'] and s['section']==0 for s in image.symbols())
    (out/'kws-run.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))
    report={'bindings':bindings,'linked_bytes':text['size'],'linked_sha256':sha(image.contents(text)),'stock_envelope_bytes':200,'fits':text['size']<=200,'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'object_sha256':sha(path.read_bytes()),'object_text_bytes':section['size'],'unresolved_helpers':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0],'source_admitted':False,'limits':['Linked at recovered entry using decoded call targets; decoded behavior and combined callback/literal placement remain unqualified.']}
    (ROOT/'docs/research/gx8002-kws-run-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
