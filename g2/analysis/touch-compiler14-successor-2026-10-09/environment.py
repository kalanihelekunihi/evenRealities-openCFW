from pathlib import Path
import json,re,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2]
old=json.loads((R/'g2/analysis/touch-msclp-attribution-2026-10-08/reproduction-receipt.json').read_text())
results=json.loads((O/'results.json').read_text());rows=[]
def extract(text):
    matches=list(re.finditer(r'cy_en_msclp_status_t\s+Cy_MSCLP_Configure\s*\(',text))
    for m in matches:
        pos=text.find(')',m.end());start=text.find('{',pos)
        if ';' in text[pos:start]:continue
        depth=0
        for end in range(start,len(text)):
            if text[end]=='{':depth+=1
            if text[end]=='}':
                depth-=1
                if depth==0:return re.sub(r'\s+',' ',text[m.start():end+1]).strip()
    raise AssertionError('definition not found')
for build in results:
    v=build['tool']['version'];p=O/'outputs'/v/'public.i'
    text='\n'.join(x for x in p.read_text().splitlines() if not x.startswith('#'))
    body=extract(text)
    (O/(v+'-Configure-preprocessed.txt')).write_text(body+'\n')
    checked=[];diff=[]
    for path,digest in build['consumed_input_hashes'].items():
        if path.startswith('/pdl/'):
            suffix=path[len('/pdl/'):];prior=next((h for n,h in old['consumed_source_hashes'].items() if n.endswith('/'+suffix)),None)
        elif path.startswith('/headers/'):
            suffix=path[len('/headers/'):];prior=next((h for n,h in old['consumed_source_hashes'].items() if n.endswith('/touch-source/'+suffix)),None)
        else:continue
        checked.append(path)
        if digest!=prior:diff.append({'path':path,'prior':prior,'current':digest})
    rows.append({'compiler':v,'normalized_configure_sha256':hashlib.sha256(body.encode()).hexdigest(),'noncompiler_inputs_compared':len(checked),'noncompiler_input_differences':diff,'expanded_loop_bounds':re.findall(r'index < ([^;]+)',body),'external_calls_in_configure':re.findall(r'\b(Cy_\w+)\s*\(',body)[1:]})
assert len({r['normalized_configure_sha256'] for r in rows})==1
assert all(not r['noncompiler_input_differences'] for r in rows)
(O/'environment-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
