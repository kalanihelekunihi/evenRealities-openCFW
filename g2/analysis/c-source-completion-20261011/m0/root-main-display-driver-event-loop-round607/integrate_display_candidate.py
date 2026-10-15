#!/usr/bin/env python3
"""Trial-link display C bodies with the selected Apollo relocatable candidate."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-round615'
out=root/'build/c-firmware/root-main-display-integration-round650'
out.mkdir(parents=True,exist_ok=True)
selected_receipt=json.loads((base/'receipt.json').read_text())
selected_link=selected_receipt['images']['apollo_main']['relocatable_link']
selected=base/'apollo_main/candidate.o'
display_audit=json.loads((display/'link-audit.json').read_text())
display_object=display/'display-driver-combined.o'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(selected)==selected_link['output_sha256'],'selected Apollo object changed'
assert sha(display_object)==display_audit['combined_sha256'],'display object changed'
overlap=sorted(set(selected_link['defined_symbols'])&set(display_audit['defined']))
assert not overlap,('duplicate definitions',overlap)
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                '-o',str(candidate)],check=True)
unresolved=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})
prior=set(selected_link['unresolved_symbols'])
resolved=sorted(prior&set(display_audit['defined']))
assert not set(resolved)&set(unresolved)
assert len(unresolved)==len(prior)-len(resolved),(len(unresolved),len(prior),resolved)
audit={'status':'candidate relocatable link only; whole-image gates remain open',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'integrated_object_sha256':sha(candidate),
       'duplicate_definitions':overlap,
       'selected_unresolved_before':len(prior),
       'resolved_by_display':resolved,
       'integrated_unresolved_after':len(unresolved),
       'unresolved_symbols':unresolved,'source_complete':False,
       'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_DISPLAY_APOLLO_INTEGRATION_LINK',len(prior),len(unresolved),len(resolved))
