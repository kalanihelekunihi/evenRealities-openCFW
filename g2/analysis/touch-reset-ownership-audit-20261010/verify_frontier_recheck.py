#!/usr/bin/env python3
"""Read-only Touch reset source/relocation frontier audit."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
L=R/'g2/analysis/touch-reset-layout-candidate-20261010'
firmware=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
image=firmware[32:]
payload=image[0xb58c-0x3300:0xb950-0x3300]
i=json.loads((L/'init_word_inventory.json').read_text());scan=json.loads((L/'archive_init_section_scan.json').read_text())
assert len(payload)==964 and hashlib.sha256(payload).hexdigest()==i['receipt']['copy_payload_sha256']
assert i['receipt']['source_owned_bytes']==25 and len(i['words'])==241
assert scan['receipt']['data_rodata_sections']==10 and scan['receipt']['sections_with_relocations']==2
archive=R/'g2/components/touch/source_candidate_20261010/build/touch-source-candidate.a'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==scan['receipt']['archive_sha256']
files=subprocess.check_output(['rg','--files','-uu','g2','third-party'],cwd=R,text=True).splitlines()
product=[x for x in files if Path(x).name.lower().startswith('cycfg_capsense')]
designs=[x for x in files if x.endswith('.cycapsense')]
touch_maps=[x for x in files if Path(x).name.startswith('touch') and x.endswith('.map')]
assert not product
assert all('infineon-' in x for x in designs)
receipt=dict(status='PASS_FINITE_TOUCH_SOURCE_FRONTIER',firmware_sha256=hashlib.sha256(firmware).hexdigest(),payload_sha256=hashlib.sha256(payload).hexdigest(),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),reset_copy_bytes=964,source_owned_bytes=25,unowned_bytes=939,source_owned_islands=i['receipt']['source_owned_islands'],archive_initialized_sections=10,archive_sections_with_relocations=2,informative_full_nonzero_matches=scan['receipt']['full_nonzero_matches'],product_cycfg_files=product,available_example_designs=designs,local_touch_maps=touch_maps,source_admission_delta=0,required_next_evidence=['G2 product .cycapsense or generated cycfg_capsense.c/.h with exact data declarations','Final Touch linker map or equivalent absolute section and relocation proof','Field-level source values plus original-byte/relocation proof if product files are unavailable'],limits=['Example designs and local touch_scb maps do not place the product reset payload.','Pointer-shaped stock words and zero padding are not source ownership.','No absolute executable Touch image or hardware claim.'])
(D/'touch-frontier-recheck.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',receipt['source_owned_bytes'],'owned',receipt['unowned_bytes'],'unowned')
