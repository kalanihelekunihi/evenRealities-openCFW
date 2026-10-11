#!/usr/bin/env python3
"""Triage direct BL targets in CASE stock image, beyond fixed pseudocode leads."""
from pathlib import Path
import hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3]
blob=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
image=Path('/tmp/case-native-target-audit.bin');image.write_bytes(blob)
cmd=['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-b','binary','-m','arm','-M','force-thumb','--adjust-vma=0x08000000',str(image)]
lines=subprocess.run(cmd,capture_output=True,text=True,check=True).stdout.splitlines()
rx=re.compile(r'^\s*([0-9a-f]+):\s+.*\bbl\s+0x([0-9a-f]+)\b')
targets={}
for line in lines:
 m=rx.search(line)
 if not m:continue
 caller=int(m[1],16);target=int(m[2],16)
 if caller>=0x0800d26c or target>=0x0800d26c or target<0x08000000:continue
 targets.setdefault(target,[]).append(caller)
fixed={int(x['entry'],16) for x in json.loads((H/'case-body-crosswalk.json').read_text())['rows']}
sources=list((R/'g2/components/case/startup_candidate_20261011').glob('*.c'))+list((R/'g2/components/case/legacy_default_candidate_20261010').glob('*.c'))+list((R/'g2/components/case/source_candidate_20261010').glob('*.c'))
contents={str(p.relative_to(R)):p.read_text().lower() for p in sources}
rows=[]
for target,callers in sorted(targets.items()):
 offset=target-0x08000000;short=f'0x{offset:04x}';full=f'0x{target:08x}'
 mentions=[path for path,text in contents.items() if short in text or full in text]
 rows.append({'target':full,'caller_count':len(callers),'callers':[f'0x{x:08x}' for x in sorted(set(callers))],
  'fixed_catalogue':target in fixed,'source_address_mentions':mentions,
  'entry_halfword':f'0x{int.from_bytes(blob[offset:offset+2],"little"):04x}'})
report={'status':'TRIAGE_ONLY','firmware_payload_sha256':hashlib.sha256(blob).hexdigest(),
 'source':'Direct Thumb BL disassembly below 0x0800d26c, excluding apparent initialized tables.',
 'limitations':['Disassembly can traverse inline data; BL targets are candidates, not verified function envelopes.',
  'Address mention is neither proof of implemented body nor link inclusion.',
  'Indirect calls, vector entries and uncalled routines are not counted.'],
 'distinct_direct_bl_targets':len(rows),'targets_without_fixed_catalogue':sum(not x['fixed_catalogue'] for x in rows),
 'targets_without_source_address_mention':sum(not x['source_address_mentions'] for x in rows),'rows':rows}
(H/'case-native-call-target-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('distinct_direct_bl_targets','targets_without_fixed_catalogue','targets_without_source_address_mention')},indent=2))
print('High-caller unmentioned targets:')
for row in sorted((x for x in rows if not x['source_address_mentions']),key=lambda x:-x['caller_count'])[:20]:print(row['target'],row['caller_count'],'fixed' if row['fixed_catalogue'] else 'outside-fixed')
