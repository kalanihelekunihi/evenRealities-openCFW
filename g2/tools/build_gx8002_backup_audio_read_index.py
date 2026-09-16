# SPDX-License-Identifier: MIT
"""Native macOS build of the backup audio read-index update."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/lvp_audio_in.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream=authenticated_blob(sdk/rel,blob)
    out=ROOT/'build/gx8002-backup-audio-read-index';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_audio_read_index.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'index.o')],check=True)
    (out/'index.ld').write_text('SECTIONS { .audio_read_index 0x1000a3fc : { *(.text*) } }\nbackup_audio_indices = 0x2002d75c;\n')
    path=out/'index.elf';subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'index');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=elf.contents(allocated[0]);assert len(body)<=28
    (out/'index.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'upstream_sha256':sha(upstream),'bytes':len(body),'envelope_bytes':28,'fits':len(body)<=28,'exact_stock':body==stock[0x42d3c:0x42d58],'source_admitted':False,'limits':['Audio-control storage is an absolute binding; its complete layout remains unresolved. Decoded behavior is verified separately.']}
    (ROOT/'docs/research/gx8002-backup-audio-read-index.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
