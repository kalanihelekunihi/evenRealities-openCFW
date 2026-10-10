from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).parent;r=json.loads((D/'results.json').read_text());b=json.loads((D/'boundary-results.json').read_text());g=json.loads((D/'internal-guard-results.json').read_text());sdk=Path('g2/analysis/sdk-runtime-link-20261010-implementation');assert hashlib.sha256((sdk/'am_util_stdio.c').read_bytes()).hexdigest()==r['unchanged_sdk_source_sha256'];normal=[c for c in r['cases'] if c.get('expected_normal_completion')];assert len(normal)==92 and all(c['exit']==0 for c in normal);assert b['count']==16 and all(c['exit']==0 for c in b['cases'])
for c in normal+b['cases']:
 observed=json.loads((D/c['stdout_receipt']).read_text());assert observed['full_destination_page_matches'];assert not (D/c['stderr_receipt']).read_text()
internal=[c for c in r['cases'] if c.get('internal_boundary_probe')];assert len(internal)==6
for c in internal:
 if c['variant']=='plain':assert c['exit']!=0 and c['asan_global_overflow']
 else:assert c['exit']==0 and not c['asan_global_overflow']
assert g['cases'][0]['exit']==0 and g['cases'][1]['exit']!=0 and g['cases'][1]['asan_use_after_poison'];(D/'verification.json').write_text(json.dumps({'ordinary_guarded_cases':108,'ordinary_cases_pass':True,'internal_probes':8,'plain_global_overflow_receipts':3,'aligned_explicit_guard_overflow_receipts':1,'aligned_uninstrumented_limit':'Default sanitizer did not flag2049-char case; explicit shadow guard did','SDK_source_unchanged':True,'total_child_runs':116,'limitations':'Native guarded source execution, not ARM ABI/stock/console/startup/hardware'},indent=2)+'\n');print('108 ordinary guarded cases and eight internal probes verified; four overflow diagnostics retained')
