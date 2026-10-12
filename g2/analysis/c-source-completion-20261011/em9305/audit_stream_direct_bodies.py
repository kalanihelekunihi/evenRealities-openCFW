"""Recheck current body receipts and symbol closure; no image-completion claim."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-nm'
p=P/'stream-frontier-round43-complete-direct-bodies.json'
r=json.loads(p.read_text());defs=set();undef=set()
base=ROOT/'g2/build/c-firmware/20261012/em-root-dispatch-round42/ble_em9305/candidate.o'
objects=[base]
for b in r['bodies']:
 d=ROOT/b['directory'];v=json.loads((d/'crosswalk-receipt.json').read_text())
 assert v['status']=='PASS_WHOLE_NATIVE_INSTRUCTION_CROSSWALK'
 sha=hashlib.sha256((d/'source.c').read_bytes()).hexdigest();assert sha==v['source_sha256']
 b.update(source_sha256=sha,object_sha256=hashlib.sha256((d/'source.o').read_bytes()).hexdigest(),pointer_relocations=v.get('function_pointer_relocations',0))
 objects.append(d/'source.o')
for obj in objects:
 for line in subprocess.check_output([str(T),str(obj)],text=True).splitlines():
  a=line.split()
  if len(a)==3 and a[1] in ['T','D','B','R','W']:defs.add(a[2])
  if len(a)==2 and a[0]=='U' and obj!=base:undef.add(a[1])
r['unresolved_group_symbols_against_round42']=sorted(undef-defs)
r['base_object_sha256']=hashlib.sha256(base.read_bytes()).hexdigest()
r['status']=f"PASS_{len(r['bodies'])}_CURRENT_COMPILED_PROVIDER_BODY_RECEIPTS" if not undef-defs else 'PENDING_SYMBOL_CLOSURE'
p.write_text(json.dumps(r,indent=2)+'\n')
q=P.parent/'progress-20261012.json';j=json.loads(q.read_text());j['em_callback_31ff68_pending'].update(status=r['status'],missing_direct_children=r['unresolved_group_symbols_against_round42']);q.write_text(json.dumps(j,indent=2)+'\n')
print({'status':r['status'],'bodies':len(r['bodies']),'instructions':r['instructions'],'native_bytes':r['native_bytes'],'unresolved':r['unresolved_group_symbols_against_round42']})
