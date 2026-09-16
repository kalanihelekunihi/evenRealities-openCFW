# SPDX-License-Identifier: MIT
"""Native macOS build of the backup IMCRA initialization wrapper."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-imcra-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_imcra_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'index.o')],check=True)
    (out/'index.ld').write_text('SECTIONS { .imcra_initialize 0x1000b91c : { *(.text*) } .imcra_error 0x1001378c : { *(.rodata.imcra_error) } }\nbackup_denoise_state = 0x2002d2bc; backup_allocate = 0x10009f2c; backup_pcm_sample_rate = 0x10009f80; backup_imcra_state_initialize = 0x1000e384; printf = 0x10009934;\n')
    path=out/'index.elf';subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'index');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==2
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=elf.contents(next(s for s in allocated if s['name']=='.imcra_initialize'));assert len(body)<=60
    message=elf.contents(next(s for s in allocated if s['name']=='.imcra_error'));assert message==stock[0x4c0cc:0x4c0cc+len(message)]
    (out/'index.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'diagnostic_bytes':len(message),'bytes':len(body),'envelope_bytes':60,'fits':len(body)<=60,'exact_stock':body==stock[0x4425c:0x44298],'source_admitted':False,'limits':['DSP initializer and state storage remain absolute bindings. The diagnostic is source-owned; the algorithm is not implemented here.']}
    (ROOT/'docs/research/gx8002-backup-imcra-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
