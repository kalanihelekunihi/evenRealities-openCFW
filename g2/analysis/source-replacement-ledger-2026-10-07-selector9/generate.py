from pathlib import Path
import json,hashlib,csv
from elftools.elf.elffile import ELFFile
R=Path.cwd();P=R/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize';N=P/'pcm22-selector9-integrated';C=json.loads((N/'current-candidate.json').read_text());B=R/C['directory'];O=R/'g2/analysis/source-replacement-ledger-2026-10-07-selector9';O.mkdir(exist_ok=True);H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
M=json.loads((B/'input-hashes.json').read_text());assert H(B/'candidate.elf')==C['sha256']
with (B/'candidate.elf').open('rb') as f:
 e=ELFFile(f);symbols={s.name:dict(address=int(s['st_value'])&~1,bytes=int(s['st_size']),type=s['st_info']['type']) for s in e.get_section_by_name('.symtab').iter_symbols()}
A=R/'g2/analysis/component-audit-2026-10-07T223956Z';rows=json.loads((A/'verified-C-body-lower-bound.json').read_text());rows.append(dict(name='selector10',payload='apollo_bootloader',range=[0x18d90,0x18e6a],bytes=218,sha256='00a1d0224d3cb171a89c20dd937ebbd2a6cacdc82f63ce4472ada18801dd2ca0'))
rows.append(dict(name='selector9',payload='apollo_bootloader',range=[0x18ca4,0x18d90],bytes=236,sha256='dfc6a869da1b531d02c9134baf05cd333d5077d3611a271587c07f38a692ac5d'))
config={'selector9':('pcm22_selector9_native','pcm22_sequence9','opencfw_spot_pcm22_transition9'),'selector5':('pcm22_hot_native','pcm22_sequence5','opencfw_spot_pcm22_transition5'),'selector11':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition11'),'selector12':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition12'),'selector21':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition21'),'selector20':('pcm22_fp_native','pcm22_sequence20','opencfw_spot_pcm22_transition20'),'completion21b':('pcm22_deferred21_native','pcm22_deferred21','opencfw_pcm22_sequence21b'),'post':('pcm22_deferred21_native','pcm22_deferred21','opencfw_pcm22_post_lptohp'),'selector22':('pcm22_deferred21_native','pcm22_sequence22','opencfw_spot_pcm22_transition22'),'selector23':('pcm22_selector23_native','pcm22_sequence23','opencfw_spot_pcm22_transition23'),'selector10':('pcm22_selector10_native','pcm22_sequence10','opencfw_spot_pcm22_transition10')}
boot=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();mapped=[]
for r in rows:
 family,stem,symbol=config[r['name']];source=R/'g2/components/bootloader/initializer_callbacks'/family/(stem+'.c');obj=next(x for x in M['inputs'] if Path(x['original']).name==stem+'.o');assert H(B/obj['path'])==obj['sha256'];s=symbols[symbol];assert s['type']=='STT_FUNC' and s['bytes']>0;a,z=r['range'];assert hashlib.sha256(boot[a:z]).hexdigest()==r['sha256']
 mapped.append(dict(context='offline_candidate225_link',category='source_defined_linked_code',**r,original_address_start=0x410000+a,original_address_end=0x410000+z,source_path=str(source.relative_to(R)),source_sha256=H(source),object_path=str((B/obj['path']).relative_to(R)),object_sha256=obj['sha256'],linked_symbol=symbol,linked_address=s['address'],linked_symbol_bytes=s['bytes'],candidate_sha256=C['sha256']))
assert sum(r['bytes'] for r in mapped)==3110
metrics={}
for line in (R/'g2/build/audits/component-audit-2026-10-07T223956Z/audit-byte-ledger.jsonl').read_text().splitlines():
 r=json.loads(line);metrics.setdefault((r['payload'],r['metric']),[]).append(r['range'])
components=list(csv.DictReader((A/'components.csv').open()));partition=[]
for c in components:
 name=c['payload'];length=int(c['total_bytes']);cuts={0,length}
 groups=[('official_executable_passthrough',metrics.get((name,'observed_executable'),[])),('resources',metrics.get((name,'confirmed_noncode'),[])+metrics.get((name,'metadata_padding'),[]))]
 for _,rs in groups:
  for a,z in rs:cuts.update([a,z])
 cuts=sorted(cuts)
 for a,z in zip(cuts,cuts[1:]):
  category=next((cat for cat,rs in groups if any(x<=a and z<=y for x,y in rs)),'unknown')
  partition.append(dict(context='production_bundle',payload=name,category=category,range=[a,z],bytes=z-a,provider='official_blob',payload_sha256=c['sha256']))
 # Candidate ownership partition is deliberately bounded to mapped bodies; other executable ownership unknown.
 if name=='apollo_bootloader':
  rs=[r['range'] for r in mapped];cuts=sorted({0,length,64,*[v for r in rs for v in r]})
  for a,z in zip(cuts,cuts[1:]):
   category='source_defined_linked_code' if any(x<=a and z<=y for x,y in rs) else 'reference_resource' if z<=64 else 'unknown'
   partition.append(dict(context='offline_candidate225_link',payload=name,category=category,range=[a,z],bytes=z-a))
for context in ['production_bundle','offline_candidate225_link']:
 for name in {r['payload'] for r in partition if r['context']==context}:
  rs=sorted((r for r in partition if r['context']==context and r['payload']==name),key=lambda r:r['range'][0]);assert rs[0]['range'][0]==0
  assert all(x['range'][1]==y['range'][0] for x,y in zip(rs,rs[1:]));assert sum(r['bytes'] for r in rs)==int(next(c['total_bytes'] for c in components if c['payload']==name))
contracts=[dict(category='official_executable_reference',selector=i,address=a,bytes=0,extent=None) for i,a in [(4,0x428506),(7,0x428920),(13,0x4291ec),(19,0x429a30)]]
contracts += [dict(category='modeled_external_ROM_call',address=a,bytes=0,extent=None) for a in [0x40,0x48,0x200ff20]]
contracts += [dict(category='modeled_call',address=a,bytes=0,extent=None,scope='integration fixture; independent of native link ownership') for a in [0x4176ce,0x415fae,0x41fa50]]
for name,j in [('mapped-functions.json',mapped),('call-contracts.json',contracts),('validation.json',dict(status='PASS',source_defined_mapped_bytes=3110,previous=2874,delta=236,candidate_sha256=C['sha256'],partition_contiguous=True))]: (O/name).write_text(json.dumps(j,indent=2)+'\n')
(O/'address-ledger.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in partition))
(O/'README.md').write_text('''# Address-mapped source ownership ledger

Eleven explicitly mapped PCM C bodies total3110 original bytes (+236 versus the selector10 ledger; +454 versus the sealed audit). This is a lower bound, not whole-firmware source replacement. mapped-functions.json binds original byte hashes to canonical C hashes, frozen object hashes and actual linked STT_FUNC symbols in candidate7ffc7b0e. Original and linked body sizes differ and are recorded separately.

address-ledger.jsonl contains two separate views. Production uses official payload providers: known executable intervals are official executable passthrough, admitted non-code/metadata are resources, and the remainder is unknown. Each payload partition covers its stored byte denominator exactly. The offline225 candidate view accounts for the bootloader original coordinates: the eleven mapped source bodies, the64-byte reference vector prefix, and unknown ownership elsewhere. Unknown does not mean absent or opaque executable; this ledger has not mapped the other linked modules. No production replacement is inferred from offline tests.

call-contracts.json records unsupported selector entry references, external resident ROM calls and fixture-specific modeled calls as zero-byte point contracts. They neither count as executable blobs embedded in the candidate nor reduce source byte totals. Modeled execution and linked ownership are independent. Resources do not satisfy executable reconstruction. An exhaustive code-only denominator and exact source-replacement/remaining-opaque percentages remain unavailable.

To extend: add a nonoverlapping original body with authenticated range hash, canonical C and frozen object hashes, linked function symbol, dedicated original-instruction comparison receipt and integration candidate identity. Do not admit trace footprints, aliases, literal regions or ROM addresses as source-owned body bytes. Generator generate.py asserts hashes, linked function presence and contiguous full-payload partitions. Preserve the sealed audit; update a successor ledger.
''');print(O)
