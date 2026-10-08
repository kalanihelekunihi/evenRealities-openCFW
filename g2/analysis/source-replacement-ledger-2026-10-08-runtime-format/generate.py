from pathlib import Path
import json,hashlib,csv
from elftools.elf.elffile import ELFFile
R=Path.cwd();P=R/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize';N=P/'bounded-format-native';C=json.loads((N/'current-candidate.json').read_text());B=R/C['directory'];O=R/'g2/analysis/source-replacement-ledger-2026-10-08-runtime-format';O.mkdir(exist_ok=True);H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
M=json.loads((B/'input-hashes.json').read_text());assert H(B/'candidate.elf')==C['sha256']
with (B/'candidate.elf').open('rb') as f:
 e=ELFFile(f);symbols={s.name:dict(address=int(s['st_value'])&~1,bytes=int(s['st_size']),type=s['st_info']['type']) for s in e.get_section_by_name('.symtab').iter_symbols()}
A=R/'g2/analysis/component-audit-2026-10-07T223956Z';rows=json.loads((A/'verified-C-body-lower-bound.json').read_text());rows.append(dict(name='selector10',payload='apollo_bootloader',range=[0x18d90,0x18e6a],bytes=218,sha256='00a1d0224d3cb171a89c20dd937ebbd2a6cacdc82f63ce4472ada18801dd2ca0'))
rows.append(dict(name='selector9',payload='apollo_bootloader',range=[0x18ca4,0x18d90],bytes=236,sha256='dfc6a869da1b531d02c9134baf05cd333d5077d3611a271587c07f38a692ac5d'))
rows.append(dict(name='selector13',payload='apollo_bootloader',range=[0x191ec,0x1944a],bytes=606,sha256='70d1c64d8b91f5e1d95f0b898d33f85faf45b83b7b61529f9d700bd2682b7a92'))
rows.append(dict(name='selector4',payload='apollo_bootloader',range=[99590,99902],bytes=312,sha256='cd801faef0531043621aeddbdfc3ab7659b492bdab75fe384a6ebfd81ca71a9d'))
rows.append(dict(name='selector7',payload='apollo_bootloader',range=[100640,100984],bytes=344,sha256='852a295b0650321492f6fbb7b9b503c6d20fdb12a19186bb2b04b1d1322fb0ee'))
rows.append(dict(name='selector19',payload='apollo_bootloader',range=[105008,105292],bytes=284,sha256='fef081b848d958957b54bcdacfb435602765c472cbeef5f3fc100e940f0dce1b'))
config={'selector4':('pcm22_remaining_native','pcm22_remaining','opencfw_spot_pcm22_transition4'),'selector7':('pcm22_remaining_native','pcm22_remaining','opencfw_spot_pcm22_transition7'),'selector19':('pcm22_remaining_native','pcm22_remaining','opencfw_spot_pcm22_transition19'),'selector13':('pcm22_selector13_native','pcm22_sequence13','opencfw_spot_pcm22_transition13'),'selector9':('pcm22_selector9_native','pcm22_sequence9','opencfw_spot_pcm22_transition9'),'selector5':('pcm22_hot_native','pcm22_sequence5','opencfw_spot_pcm22_transition5'),'selector11':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition11'),'selector12':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition12'),'selector21':('pcm22_hot_native','pcm22_hot_transitions','opencfw_spot_pcm22_transition21'),'selector20':('pcm22_fp_native','pcm22_sequence20','opencfw_spot_pcm22_transition20'),'completion21b':('pcm22_deferred21_native','pcm22_deferred21','opencfw_pcm22_sequence21b'),'post':('pcm22_deferred21_native','pcm22_deferred21','opencfw_pcm22_post_lptohp'),'selector22':('pcm22_deferred21_native','pcm22_sequence22','opencfw_spot_pcm22_transition22'),'selector23':('pcm22_selector23_native','pcm22_sequence23','opencfw_spot_pcm22_transition23'),'selector10':('pcm22_selector10_native','pcm22_sequence10','opencfw_spot_pcm22_transition10')}
boot=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();mapped=[]
for r in rows:
 family,stem,symbol=config[r['name']];source=R/'g2/components/bootloader/initializer_callbacks'/family/(stem+'.c');obj=next(x for x in M['inputs'] if Path(x['original']).name==stem+'.o');assert H(B/obj['path'])==obj['sha256'];s=symbols[symbol];assert s['type']=='STT_FUNC' and s['bytes']>0;a,z=r['range'];assert hashlib.sha256(boot[a:z]).hexdigest()==r['sha256']
 mapped.append(dict(context='offline_candidate229_link',category='source_defined_linked_code',**r,original_address_start=0x410000+a,original_address_end=0x410000+z,source_path=str(source.relative_to(R)),source_sha256=H(source),object_path=str((B/obj['path']).relative_to(R)),object_sha256=obj['sha256'],linked_symbol=symbol,linked_address=s['address'],linked_symbol_bytes=s['bytes'],candidate_sha256=C['sha256']))

extra=[('pcm22_profile',0x42ab7c,0x42abb2,'pcm22_runtime_native','pcm22_runtime_hooks','opencfw_pcm22_profile_apply','hooks-comparison.json','child contracts controlled'),('pcm22_temperature_init',0x42ac54,0x42aca4,'pcm22_runtime_native','pcm22_runtime_hooks','opencfw_pcm22_temperature_init','hooks-comparison.json','child contracts controlled'),('snprintf',0x41b218,0x41b256,'bounded_format_native','bounded_format','opencfw_boot_elog_snprintf','real-core-comparison.json','model plus hybrid original-engine comparison'),('vsnprintf',0x41b25c,0x41b292,'bounded_format_native','bounded_format','opencfw_boot_elog_vsnprintf','real-core-comparison.json','model plus hybrid original-engine comparison'),('bounded_writer',0x415672,0x41568c,'bounded_format_native','bounded_format','opencfw_boot_bounded_writer','bounded-format-comparison.json','explicit engine model plus hybrid writer callback execution')]
for name,start,end,family,stem,symbol,receipt,mode in extra:
 a,z=start-0x410000,end-0x410000;source=R/'g2/components/bootloader/initializer_callbacks'/family/(stem+'.c');obj=next(x for x in M['inputs'] if Path(x['original']).name==stem+'.o');assert H(B/obj['path'])==obj['sha256'];r=symbols[symbol];assert r['type']=='STT_FUNC';j=json.loads((N/receipt).read_text());assert j['candidate_sha256']==C['sha256'] and j['status'].startswith('PASS')
 mapped.append(dict(context='offline_candidate229_link',category='source_defined_linked_code',name=name,payload='apollo_bootloader',range=[a,z],bytes=z-a,sha256=hashlib.sha256(boot[a:z]).hexdigest(),original_address_start=start,original_address_end=end,source_path=str(source.relative_to(R)),source_sha256=H(source),object_path=str((B/obj['path']).relative_to(R)),object_sha256=obj['sha256'],linked_symbol=symbol,linked_address=r['address'],linked_symbol_bytes=r['bytes'],candidate_sha256=C['sha256'],validation_receipt=str((N/receipt).relative_to(R)),validation_receipt_sha256=H(N/receipt),validation_mode=mode))
assert sum(r['bytes'] for r in mapped)==4932
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
   partition.append(dict(context='offline_candidate229_link',payload=name,category=category,range=[a,z],bytes=z-a))
for context in ['production_bundle','offline_candidate229_link']:
 for name in {r['payload'] for r in partition if r['context']==context}:
  rs=sorted((r for r in partition if r['context']==context and r['payload']==name),key=lambda r:r['range'][0]);assert rs[0]['range'][0]==0
  assert all(x['range'][1]==y['range'][0] for x,y in zip(rs,rs[1:]));assert sum(r['bytes'] for r in rs)==int(next(c['total_bytes'] for c in components if c['payload']==name))
contracts=[dict(category='official_executable_reference',selector=i,address=a,bytes=0,extent=None) for i,a in []]
contracts += [dict(category='original_executable_dependency',address=0x41e47a,bytes=0,extent=None,scope='formatter engine; hybrid oracle in dedicated tests; not embedded executable bytes')]
contracts += [dict(category='modeled_external_ROM_call',address=a,bytes=0,extent=None) for a in [0x40,0x48,0x200ff20]]
contracts += [dict(category='modeled_call',address=a,bytes=0,extent=None,scope='integration fixture; independent of native link ownership') for a in [0x4176ce,0x415fae,0x41fa50]]
for name,j in [('mapped-functions.json',mapped),('call-contracts.json',contracts),('validation.json',dict(status='PASS',source_defined_mapped_bytes=4932,pcm_mapped_bytes=4790,format_wrapper_mapped_bytes=142,previous=4656,delta=276,candidate_sha256=C['sha256'],partition_contiguous=True))]: (O/name).write_text(json.dumps(j,indent=2)+'\n')
(O/'address-ledger.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in partition))
(O/'README.md').write_text('''# Address-mapped source ownership ledger

Twenty mapped C bodies total4932 original bytes: seventeen PCM bodies4790bytes and three formatter-wrapper bodies142bytes. This adds276bytes to the preserved227 ledger, independent of the parser fragment (not counted). This is a bounded lower bound, not whole-firmware source replacement. Symbol/original/source/object/receipt identities are retained.

The two runtime hooks were compared with child-call contracts; wrappers were compared using an engine model and hybrid original-engine execution. These are linked C bodies, not proof of transitive source-only closure. Original formatter0x41e47a remains a zero-byte executable dependency contract, separate from admitted ownership and embedded-blob accounting.

Production partitions still use official payload providers; offline229 partitions map only these twenty bodies and64byte reference vector resource. Remaining ownership is unknown, not absent or necessarily opaque executable. No exhaustive code-only denominator or exact replacement percentage is established. Resident ROM, synthetic MMIO and modeled integration boundaries remain explicit.
''');print(O)
