#!/usr/bin/env python3
"""Conservative CASE body leads against retained fixed-image pseudocode.

Address mentions in source headers are leads only. They never establish a
function mapping, semantic equivalence, or whole-image completeness.
"""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
decomp=ROOT/'g2/tools/manifests/g2-box-ghidra-decomp.c'
stock=decomp.read_text()
addresses=sorted({int(x,16) for x in re.findall(r'/\* FUN 0x([0-9a-fA-F]+) FUN_',stock)})
selected=ROOT/'g2/components/case/source_candidate_20261010'
candidate=ROOT/'g2/components/case/legacy_default_candidate_20261010'
startup=ROOT/'g2/components/case/startup_candidate_20261011'
sources=[('selected',p) for p in selected.rglob('*.c')]+[('candidate',p) for p in candidate.glob('*.c')]+[('startup_candidate',p) for p in startup.glob('*.c')]
leads={a:[] for a in addresses}
for tier,path in sources:
    # This deliberately reads only each source's top comment/provenance area.
    # Calls further down in a C file are not attributed as implementations.
    start=path.read_text(errors='replace')[:700]
    for x in re.findall(r'0x080[0-9a-fA-F]{5}',start):
        address=int(x,16)
        if address in leads:
            leads[address].append({'tier':tier,'source':str(path.relative_to(ROOT))})
rows=[{'entry':f'0x{a:08x}','status':('header_address_lead' if leads[a] else 'no_header_lead'),
       'leads':leads[a]} for a in addresses]
summary={'fixed_pseudocode_sha256':hashlib.sha256(decomp.read_bytes()).hexdigest(),
         'recognized_entries':len(rows),'entries_with_header_leads':sum(bool(leads[a]) for a in addresses),
         'entries_without_header_leads':sum(not leads[a] for a in addresses),
         'selected_source_files_examined':sum(t=='selected' for t,_ in sources),
         'candidate_source_files_examined':sum(t=='candidate' for t,_ in sources),
         'startup_candidate_source_files_examined':sum(t=='startup_candidate' for t,_ in sources),
         'limitations':'Header mention is not a body match. A no-lead row may have a source body under another name. Startup, initialized data, layout, and physical effects are outside this pseudocode table.'}
(HERE/'case-body-crosswalk.json').write_text(json.dumps({'summary':summary,'rows':rows},indent=2)+'\n')
print(json.dumps(summary,indent=2))
