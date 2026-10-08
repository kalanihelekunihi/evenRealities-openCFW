"""Finalize only after all exact-image and scoped source checks succeeded."""
from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
c=json.loads((HERE/'current-candidate.json').read_text());b=ROOT/c['directory'];h=c['sha256'];hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert hashfile(b/'candidate.elf')==h
integration=[]
for name,count in [('comparison.json',2),('failures.json',3),('powerloss.json',2)]:
 p=b/'validation'/name;d=json.loads(p.read_text());assert d['status']=='PASS' and d['cases']==count and d['elf_sha256']==h
 integration.append(dict(path=str(p.relative_to(b)),cases=count,sha256=hashfile(p)))
for name,count in [('broad',44),('focused',11),('extra',5),('closure',3)]:
 d=json.loads((HERE/(name+'-run-results.json')).read_text());assert len(d)==count and all(x['returncode']==0 for x in d)
for name,count in [('selector5-comparison.json',579),('hot-transition-comparison.json',796),('selector20-comparison.json',192)]:
 d=json.loads((HERE/name).read_text());assert d['status']=='PASS' and d['cases']==count and d['base_elf_sha256']==h
front=json.loads((HERE/'updater-frontier.json').read_text());assert front['cases']==151 and not front['boundaries'] and front['elf_sha256']==h
fp=json.loads((HERE/'fp-qemu/positive-comparison.json').read_text());assert fp['status']=='PASS' and fp['cases']==290 and fp['source_candidate_sha256']==h and fp['bucket_mismatches']==fp['fpscr_mismatches']==0
assert hashfile(Path('/tmp/opencfw-hot-reproduced.elf'))==h
m=json.loads((b/'input-hashes.json').read_text());assert len(m['inputs'])==220
for row in m['inputs']+m['source']:assert hashfile(b/row['path'])==row['sha256']
component=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_hot_native';assert not component.exists(), 'Refuse to overwrite an existing component delivery directory'
component.mkdir()
for name in ['initialized_data.c','startup_events_a.c','startup_events_a.h','pcm22_hot_transitions.c','interfaces.h']:shutil.copy2(HERE/name,component/name)
shutil.copy2(HERE.parent/'pcm22-selector5-integrated/pcm22_sequence5.c',component/'pcm22_sequence5.c')
flags=json.loads((HERE/'build-inputs.json').read_text())['flags'];source_rows=[]
for name in ['initialized_data','startup_events_a','pcm22_hot_transitions','pcm22_sequence5']:
 out=Path('/tmp/opencfw-hot-delivered')/(name+'.o');out.parent.mkdir(exist_ok=True)
 subprocess.run(['clang',*flags,'-I',str(component),'-I',str(ROOT/'g2/components/bootloader/initializer_callbacks'),'-c',str(component/(name+'.c')),'-o',str(out)],check=True)
 row=next(r for r in m['inputs'] if Path(r['path']).name==name+'.o');assert hashfile(out)==row['sha256'];source_rows.append(dict(path=str(component/(name+'.c')),source_sha256=hashfile(component/(name+'.c')),object_sha256=hashfile(out),frozen_object=row['path']))
(component/'README.md').write_text('''# PCM2.2 bounded native transition variants

Reconstruction of locked selectors5/11/12/21 plus updater volatile-class rereads. Read interfaces.h for the private raw-R0 ABI and profile fields. These are compiler-generated C bodies, not SDK copies or embedded original instructions. initialized_data.c and startup_events_a.c replace the corresponding parent objects in the separate220-object offline candidate; do not link these variants alongside parent variants. pcm22_sequence5.c and pcm22_hot_transitions.c add new callback bodies.

Candidate e5972f996f4ffc9a08ac54ba8e92e07cbc1745425db32b1eb78a9c9dea67b7ff: all7 original-image integration cases PASS;579 selector5 and796 hot-family direct comparisons PASS, visiting all1744 original body bytes;151 native updater frontier cases plus17 targeted cases PASS;290 QEMU bucket/fullFPSCR comparisons match. Four C copies compile identically to frozen objects. Synthetic peripherals/ROMdelay and incomplete deferred21b lifecycle limit proof. This is not a deployable, whole-source, byte-identical official firmware or hardware-safe patch.

Detailed function hashes, SDK variant differences, disassembly, bounds-default evidence and receipts: g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm22-hot-transitions-integrated/REPORT.md. No shared build recipe/campaign was changed.
''')
(HERE/'component-object-reproduction.json').write_text(json.dumps(dict(status='PASS',elf_sha256=h,flags=flags,results=source_rows),indent=2)+'\n')
report=HERE/'REPORT.md';s=report.read_text().replace('Final interrupted-update integration checks are still running; this report will be finalized from their actual receipts.','All7 exact-image integration cases PASS:2 normal/update,3 malformed-input,2 interrupted-update. Final component copies are delivered in g2/components/bootloader/initializer_callbacks/pcm22_hot_native/ and reproduce frozen objects exactly.')
s=s.replace('Readable reconstruction is pcm22_sequence5.c in the selector5 predecessor area plus pcm22_hot_transitions.c here; interfaces.h explains fields and private ABI.','Readable reconstruction is delivered in the component directory above and preserved in the two owned analysis areas; interfaces.h explains fields and private ABI.')
report.write_text(s)
# Preserve creation source snapshots. Final verifiers/source corrections have a separate hash ledger.
final=b/'validation-source-final';final.mkdir(exist_ok=True)
for p in HERE.glob('*.py'):shutil.copy2(p,final/p.name)
for p in component.glob('*'):
 if p.is_file():shutil.copy2(p,final/p.name)
for p in (HERE/'fp-qemu').glob('*'):
 if p.suffix in ['.py','.c','.S','.ld']:
  q=final/'fp-qemu'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
for name in ['selector5-comparison.json','hot-transition-comparison.json','selector20-comparison.json','updater-frontier.json','temperature-default.json','native-coverage.json','function-provenance.json','source-object-reproduction.json','component-object-reproduction.json','input-reconciliation.json','preservation-check.json','diagnostics.json','tool-versions.json']:
 shutil.copy2(HERE/name,b/'validation'/name)
for name in ['positive-comparison.json','predecessor-negative-comparison.json']:
 shutil.copy2(HERE/'fp-qemu'/name,b/'validation'/('fp-qemu-'+name))
(HERE/'validation-source-addendum.json').write_text(json.dumps(dict(candidate_sha256=h,files=[dict(path=str(p.relative_to(b)),sha256=hashfile(p)) for p in sorted(final.rglob('*')) if p.is_file()]),indent=2)+'\n');shutil.copy2(HERE/'validation-source-addendum.json',b/'validation-source-addendum.json')
receipts=[]
for p in sorted((b/'validation').rglob('*.json')):
 d=json.loads(p.read_text());receipts.append(dict(path=str(p.relative_to(b)),status=d.get('status','STRUCTURED_RECEIPT'),sha256=hashfile(p)))
summary=dict(status='PASS_BOUNDED',elf_sha256=h,objects=220,integration_cases=7,integration=integration,driver_runs={'broad':44,'focused':11,'extra':5,'closure':3},new_functions=4,new_original_body_bytes=1744,direct_selector5_cases=579,direct_hot_family_cases=796,native_frontier_cases=151,targeted_updater_cases=17,native_updater_bytes=756,updater_body_bytes=758,synthetic_mutation_prefix_cases=3,synthetic_prefix_counted_in_native_coverage=False,qemu_bucket_full_fpscr_cases=290,exact_frozen_object_relink=True,compile_identical_delivered_sources=4,receipts=receipts,limits=['Offline three-slot layout, synthetic peripherals and absent resident ROMdelay.','Deferred21b body and physical asynchronous scheduling/cache/FP context behavior remain outside this result.','No whole-source, byte-identical OTA or hardware-safe patch claim.'])
(b/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n');shutil.copy2(b/'validation-summary.json',HERE/'validation-summary.json');print('PASS220: seven integration cases, source delivery and frozen reconciliation',h)
