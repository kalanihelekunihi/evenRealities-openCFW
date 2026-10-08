from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x483fcc,0x483fd0),(0x483ffc,0x484010)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==24
o=b/'analysis/review-isolated-P2-21383/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Formatter pointer and mask disjoint literals\n\nPartial/unaccepted;24 exactdata bytes in483FCC..483FD0 and483FFC..484010. Sixlittle-endianwordslots:483FCC→0078DC7C;483FFC→0078DC84;484000→006EE378;484004→000FFFFF;484008→3FF00000;48400C→00483031. 483FCCconsumedbynegative-specialstringmap21728;483FFCpositive-specialstringmap21730;484000scale-tablepointermap21732;484004highmantissamask and484008highnormalizedexponentmap21744;48400CThumbcallback483030|1 selectedwhenentrycontextzero map21756. Exactpointertargets/scale-tablecontentsnotincludedhere, stillneeddatarecovery. Intervening483FD0..483FFCexcludedascodependingrecovery; no classifycodefromworddump. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=24,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',24)
