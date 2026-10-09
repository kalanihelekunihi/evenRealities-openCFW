from pathlib import Path
import hashlib,json
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
obj=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs/cy_sysclk.c/public.o';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
with obj.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.text.Cy_SysClk_ClkPumpSetSource');d=s.data();assert len(d)==56;assert e.get_section_by_name('.rel'+s.name) is None
stock=fw.read_bytes()[32+0xa188-0x3300:32+0xa1c0-0x3300];assert stock==d
result={'status':'PASS','historical_name':'Cy_SysClk_ClkHfSetSource','correct_source_name':'Cy_SysClk_ClkPumpSetSource','runtime_extent':['0xA188','0xA1C0'],'code_bytes':44,'literal_bytes':12,'full_section_bytes':56,'object_sha256':sha(obj),'payload_sha256':sha(fw),'section_sha256':hashlib.sha256(d).hexdigest(),'independent_review':'pending','limits':'Historical source attribution corrected by unchanged exact source bytes; no original symbols modified. Clock pump runtime/physical state not tested.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
