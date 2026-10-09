from pathlib import Path
import re,json,hashlib
O=Path(__file__).resolve().parent
names=['uint32_t','MSCLP_MODE_Type','MSCLP_Type','cy_en_msclp_status_t','cy_en_msclp_key_t','cy_stc_msclp_mode_config_t','cy_stc_msclp_base_config_t','cy_stc_msclp_context_t']
records=[];definitions={}
for version in ['10.3-2021.10','11.3.Rel1','12.2.Rel1','13.3-reference']:
    raw=(O/'outputs'/version/'public.i').read_text()
    text='\n'.join(x for x in raw.splitlines() if not x.startswith('#'))
    defs={}
    for name in names:
        m=re.search(r'\b'+name+r'\s*;',text)
        if m:
            start=text.rfind('typedef',0,m.start())
            defs[name]=re.sub(r'\s+',' ',text[start:m.end()]).strip()
    definitions[version]=defs
    pragmas=[x.strip() for x in raw.splitlines() if x.startswith('#pragma')]
    records.append({'version':version,'definition_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in defs.items()},'packing_or_alignment_pragmas':[x for x in pragmas if re.search(r'\b(pack|align)\b',x)],'non_diagnostic_pragmas':[x for x in pragmas if 'diagnostic' not in x],'type_attributes':{n:re.findall(r'__attribute__[^;]*',s) for n,s in defs.items()},'volatile_counts':{n:s.count('volatile') for n,s in defs.items()}})
assert all(definitions[v]==definitions['13.3-reference'] for v in definitions)
assert all(not x['packing_or_alignment_pragmas'] and not x['non_diagnostic_pragmas'] for x in records)
(O/'Configure-used-types.json').write_text(json.dumps(definitions['13.3-reference'],indent=2)+'\n')
(O/'type-comparison.json').write_text(json.dumps({'all_recovered_used_types_identical':True,'records':records,'limits':'declaration comparison, not a compiler layout probe or producing-header authentication'},indent=2)+'\n')
print('PASS focused declarations identical across four preprocess outputs; no active packing/alignment/non-diagnostic pragma')
