#!/usr/bin/env python3
"""Select the three public CASE C providers into a relocatable source candidate."""
from pathlib import Path
import hashlib, json, subprocess, tempfile

D=Path(__file__).resolve().parent
ROOT=D.parents[3]
SELECTED=ROOT/'g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a'
CANDIDATE=ROOT/'g2/analysis/c-source-completion-20261011/m0/case-build/libcase_command_candidate.a'
RECEIPT=ROOT/'g2/analysis/case-source-candidate-round2-20261010/receipt.json'
OUT=ROOT/'g2/build/c-firmware/20261011/peripherals-case-public-source/case-public-source.o'
LD='/opt/homebrew/bin/arm-none-eabi-ld'
NM='/opt/homebrew/bin/arm-none-eabi-nm'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SELECTED)==json.loads(RECEIPT.read_text())['archive_sha256']
assert SELECTED.exists() and CANDIDATE.exists()
OUT.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as t:
 paths=[Path(t)/f'pass-{i}.o' for i in range(2)]
 for p in paths:
  subprocess.run([LD,'-r','--whole-archive',str(SELECTED),'--no-whole-archive',
                  '-u','case_binary_command','-u','case_legacy_command',
                  '-u','case_vformat',str(CANDIDATE),'-o',str(p)],check=True)
 assert sha(paths[0])==sha(paths[1])
 OUT.write_bytes(paths[0].read_bytes())
names=subprocess.run([NM,'-g',str(OUT)],check=True,capture_output=True,text=True).stdout
defined=set();undefined=set()
for line in names.splitlines():
 parts=line.split()
 if len(parts)<2:continue
 kind,name=parts[-2:]
 if kind=='U':undefined.add(name)
 elif kind.upper() in {'T','D','B','R','C','W'}:defined.add(name)
assert not undefined,sorted(undefined)
assert {'case_binary_command','case_legacy_command','case_vformat'}<=defined
out={'status':'CASE_PUBLIC_SOURCE_CANDIDATE_RELOCATABLE',
     'artifact':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),
     'selected_archive_sha256':sha(SELECTED),'candidate_archive_sha256':sha(CANDIDATE),
     'defined_count':len(defined),'undefined_count':0,'rebuild_identical':True,
     'public_providers':['case_binary_command','case_legacy_command','case_vformat'],
     'source_evidence':['linked256-comparison.json','binary-whole-no-lower.json',
                        'case-flash-apply-whole-comparison.json',
                        'verify_case_vformat_extended.py'],
     'limits':['Relocatable C source candidate only; no final stock image placement.',
               'Native equivalence is bounded by cited comparison corpora.',
               'Physical flash, PMIC, sensor, transport and reset effects are not validated.']}
OUT.with_suffix('.receipt.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','defined_count','undefined_count','sha256')},indent=2))
