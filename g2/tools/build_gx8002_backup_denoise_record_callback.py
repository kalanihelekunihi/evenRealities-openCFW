# SPDX-License-Identifier: MIT
"""Build backup denoise record callback; upstream is provenance, not binary input."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'backup_get_context':0x10009e8c,'backup_get_mic_frame':0x10009ec0,
          'backup_dcache_invalid_range':0x10004dd8,'backup_queue_put':0x10015b64,
          'backup_denoise_state':0x2002d2bc}
def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/lvp_mode_denoise.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    upstream=subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob])
    out=ROOT/'build/gx8002-backup-denoise-record-callback';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_denoise_record_callback.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'callback.o')],check=True)
    (out/'callback.ld').write_text('SECTIONS { .callback 0x1000bd54 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in BINDINGS.items()))
    path=out/'callback.elf';subprocess.run([pre+'ld','-T',str(out/'callback.ld'),str(out/'callback.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'callback');alloc=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(alloc)==1 and alloc[0]['name']=='.callback'
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=elf.contents(alloc[0])
    (out/'callback.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oracle=Elf32(wrapper.read_bytes(),'stock')
    assert sha(oracle.contents(next(s for s in oracle.sections if s['name']=='.data')))==IMAGE_SHA
    (out/'stock.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-D','--start-address=0x44694','--stop-address=0x446f0',str(wrapper)],text=True))
    result={'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'upstream_sha256':sha(upstream),
            'package_offset':0x44694,'runtime_address':0x1000bd54,'compiled_bytes':len(body),'envelope_bytes':92,'fits':len(body)<=92,
            'compiled_sha256':sha(body),'stock_sha256':sha(stock[0x44694:0x446f0]),'bindings':BINDINGS,'source_admitted':False,
            'limits':['Candidate only: decoded equivalence and startup integration remain pending.',
                      'Partial field declarations do not establish complete context or header ownership.',
                      'Unsigned wrapping multiplication/division and live microphone-count reload follow backup instructions.']}
    (ROOT/'docs/research/gx8002-backup-denoise-record-callback-candidate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
