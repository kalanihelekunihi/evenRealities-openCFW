"""Static syntax triage only; not behavioral validation or reachability."""
import json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent
inventory=json.loads((HERE.parent/'extended-log-caller-inventory-20261010/inventory.json').read_text())
token=re.compile(r'%(?:%|[-#0]*\d{0,2}(?:\.\*|\.\d{1,2})?(?:ll|l|z)?[duxXpsc])')
def in_subset(text):
    i=0
    while i<len(text):
        if text[i]!='%':i+=1;continue
        match=token.match(text,i)
        if i==len(text)-1:return True  # stock emits a final literal percent
        if not match:return False
        part=match.group();i=match.end()
        width=re.match(r'%[-#0]*(\d+)',part)
        if width and int(width.group(1))>24:return False
        if '.' in part and not part.endswith('s'):return False
    return True
resolved=[site for site in inventory['sites'] if site['format']]
within=[site for site in resolved if in_subset(site['format']['text'])]
outside=[site for site in resolved if not in_subset(site['format']['text'])]
result={'image_sha256':inventory['image_sha256'],
        'resolved_syntactic_sites':len(resolved),
        'static_syntax_subset_sites':len(within),
        'static_syntax_outside_sites':len(outside),
        'unresolved_literal_sites':inventory['sweep_bl_count']-len(resolved),
        'outside_unique_formats':len({site['format']['address'] for site in outside}),
        'outside':outside,
        'limit':'This regex is a syntax triage over linear-sweep BL sites. It does not prove reachability, argument counts, exact source semantics, or that every matching format was tested.'}
(HERE/'syntax_frontier.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:result[k] for k in ('resolved_syntactic_sites','static_syntax_subset_sites','static_syntax_outside_sites','unresolved_literal_sites','outside_unique_formats')},indent=2))
