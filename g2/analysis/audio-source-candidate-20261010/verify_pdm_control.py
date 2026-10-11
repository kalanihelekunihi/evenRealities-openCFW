#!/usr/bin/env python3
"""Compare complete PDM type-1 publisher through original queue peers."""
import hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
PRIOR=ROOT/'g2/analysis/audio-watchdog-callback-closure-2026-10-09'
SOURCE=ROOT/'g2/components/audio/source_candidate_20261010/pdm_control_provider.c'
ELF=Path('/tmp/g2-audio-pdm-control-m4.elf')
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib',
       '-Wl,-Ttext=0x100000','-Wl,-e,audio_pdm_control','-Wl,--defsym=stock_audio_submit=0x53c639']
subprocess.run([str(GCC),*flags,str(SOURCE),'-o',str(ELF)],check=True)
fixture=(PRIOR/'verify.py').read_text().split('cases=[]')[0]
old="receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']"
new=f"receipt={{'elf_sha256':'{hashlib.sha256(ELF.read_bytes()).hexdigest()}'}};elf=Path('{ELF}')"
assert old in fixture;fixture=fixture.replace(old,new)
old="'emit_type0':0x53ca10,'type6':0x53c92e};names="
new="'emit_type0':0x53ca10,'pdm':0x53ca32,'type6':0x53c92e};names="
assert old in fixture;fixture=fixture.replace(old,new)
old="'emit_type0':'audio_watchdog_emit_type0','type6'"
new="'emit_type0':'audio_watchdog_emit_type0','pdm':'audio_pdm_control','type6'"
assert old in fixture;fixture=fixture.replace(old,new)
old="if kind=='emit_type0' else [0,1,2]"
new="if kind=='emit_type0' else [1,1,argument&255] if kind=='pdm' else [0,1,2]"
assert old in fixture;fixture=fixture.replace(old,new)
ns={'__file__':str(PRIOR/'verify.py')};exec(fixture,ns)
rows=[]
for argument in (0,1,2,255,256,258,0xffffffff):
 for queue in ('null','empty','full'):
  original=ns['run'](False,'pdm',argument,queue);compiled=ns['run'](True,'pdm',argument,queue)
  assert original==compiled,(argument,queue,original,compiled)
  rows.append({'argument':argument,'queue':queue,'observed':original})
receipt={'status':'PASS','cases':len(rows),'original_entry':'0x53ca32','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'comparison_elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'compiler_sha256':hashlib.sha256(GCC.read_bytes()).hexdigest(),
         'flags':flags,'prior_fixture_sha256':hashlib.sha256((PRIOR/'verify.py').read_bytes()).hexdigest(),'rows':rows,
         'limit':'Complete wrapper and original publisher/CMSIS queue peers; successful empty-queue path stops before thread flag dispatch. Synthetic queue state, no live audio hardware.'}
(HERE/'pdm-control-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows))
