"""Conservative relocation-site screening; a hit is not attribution."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'g2/analysis/shortcut-batch-2026-10-05/codec-upstream/evidence.json'
e=json.loads(E.read_text()); c=e['selected_candidate']; obj=ROOT/c['object']; fw=(ROOT/e['target']['path']).read_bytes()
assert hashlib.sha256(obj.read_bytes()).hexdigest()==c['object_sha256']
assert hashlib.sha256(fw).hexdigest()==e['target']['sha256']
with obj.open('rb') as f:
 elf=ELFFile(f); raw=elf.get_section_by_name(c['text_section']).data(); rs=elf.get_section_by_name(c['relocation_section']); rels=[dict(r.entry) for r in rs.iter_relocations()]
assert len(raw)==830 and len(rels)==11
assert hashlib.sha256(raw).hexdigest()==c['text_section_sha256']
def scan(buf, radius):
 mask=bytearray(b'\1'*len(raw))
 for r in rels:
  a=max(0,r['r_offset']-radius); b=min(len(raw),r['r_offset']+4+radius); mask[a:b]=b'\0'*(b-a)
 runs=[]; i=0
 while i<len(raw):
  if not mask[i]: i+=1; continue
  j=i+1
  while j<len(raw) and mask[j]: j+=1
  runs.append((i,raw[i:j])); i=j
 anchor=max(runs,key=lambda x:len(x[1])); hits=[]; p=buf.find(anchor[1])
 while p>=0:
  start=p-anchor[0]
  if start>=0 and start+len(raw)<=len(buf) and all(buf[start+a:start+a+len(s)]==s for a,s in runs):hits.append(start)
  p=buf.find(anchor[1],p+1)
 return hits,sum(mask),len(anchor[1])
results=[]
for radius in [0,4,8]:
 hits,n,anchor=scan(fw,radius)
 assert scan(b'prefix'+raw+b'suffix',radius)[0]==[6]
 mutant=bytearray(raw)
 for r in rels:mutant[r['r_offset']:r['r_offset']+4]=b'\xff'*4
 assert scan(bytes(mutant),radius)[0]==[0]
 mutant[0]^=1
 assert scan(bytes(mutant),radius)[0]==[]
 results.append(dict(extra_radius=radius,unmasked_bytes=n,anchor_bytes=anchor,payload_offsets=hits))
report=dict(status='PASS_SCREENING_CONTROLS',source_commit=e['upstream']['commit'],object_sha256=c['object_sha256'],firmware_sha256=e['target']['sha256'],relocations=rels,results=results,limits=['Whole relocation words and optionally surrounding bytes are discarded; this is a deliberately overmasked screen, not exact relocation resolution.','No linker relaxation, changed instruction selection, reordering or compiler variation is modeled.','No-hit excludes only the unchanged unmasked section pattern, not the API or equivalent implementation.','Object bytes are read locally; none exported. No new firmware attribution or source reconstruction is claimed.'])
Path(__file__).with_name('codec-mask-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results))
