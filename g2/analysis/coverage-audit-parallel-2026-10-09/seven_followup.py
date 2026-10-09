from pathlib import Path
import json,struct,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';src=(O/'seven_verify.py').read_text();exec(src[:src.index("names=['")]);d=json.loads((O/'SEVEN-LINKAGE-VERIFICATION.json').read_text());poolchecks=[];extraobjects=[];helpers=[]
for q in d['reviews']:
 P=R/'g2/analysis'/('touch-'+q['task']+'-2026-10-09');r=json.loads((P/'results.json').read_text());b,ss,ns,sy=elf(P/'outputs/linked.elf')
 for key,file in [('assembly_object_sha256','assembly.o'),('common_object_sha256','common.o')]:
  if key in r:extraobjects.append({'task':q['task'],'file':file,'hash_verified':sha((P/'outputs'/file).read_bytes())==r[key]})
 for f in r['sections']:
  if not f['exact']:continue
  a=int(f['address'],16);idx=ns.index('.'+f['section']);x=ss[idx];v=b[x[4]:x[4]+x[5]];maps=sorted((sv-a,sn) for sn,sv,_,k in sy if k==idx and sn.startswith(('$t','$d')));pool=next((off for off,n in maps if n.startswith('$d')),len(v));refs=set();off=0
  while off<pool:
   h=struct.unpack_from('<H',v,off)[0]
   if h&0xf800==0x4800:refs.add(((a+off+4)&~3)+(h&255)*4)
   off+=4 if h>>11 in (29,30,31) else 2
  poolchecks.append({'task':q['task'],'section':f['section'],'all_pool_words_referenced':set(range(a+pool,a+len(v),4))<=refs,'pool_offset':pool})
  if f.get('new_helper_outside_denominator'):helpers.append([a,a+len(v),f['section']])
# Pump source attribution, no linking or relocations needed.
P=R/'g2/analysis/touch-clkpump14-attribution-2026-10-09';r=json.loads((P/'results.json').read_text());obj=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs/cy_sysclk.c/public.o';b,ss,ns,sy=elf(obj);idx=ns.index('.text.'+r['correct_source_name']);x=ss[idx];v=b[x[4]:x[4]+x[5]];a,end=[int(t,16) for t in r['runtime_extent']];refs=[];off=0
while off<44:
 h=struct.unpack_from('<H',v,off)[0]
 if h&0xf800==0x4800:refs.append(((a+off+4)&~3)+(h&255)*4)
 off+=4 if h>>11 in (29,30,31) else 2
pump={'object_hash_verified':sha(b)==r['object_sha256'],'exact':v==stock(a,len(v)),'section_hash_verified':sha(v)==r['section_sha256'],'full_length_verified':len(v)==56==end-a,'relocation_free':not relocs(b,ss,ns,sy,idx),'mapping_symbols':[(sv,sn) for sn,sv,_,k in sy if k==idx and sn.startswith(('$t','$d'))],'all_pool_words_referenced':set(range(a+44,end,4))<=set(refs)};d['new_ranges'].append([a,end,'clkpump14-attribution','Cy_SysClk_ClkHfSetSource'])
# Independently reproduce diagnostic residual differences, without excluding any new byte.
P=R/'g2/analysis/touch-pdl14-residual-boundary-2026-10-09';r=json.loads((P/'results.json').read_text());res=[]
for f in r['entries']:
 unit=next(x['source_unit'] for x in json.loads((R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/selection.json').read_text())['functions'] if x['function']==f['function']);obj=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs'/unit/'public.o';b,ss,ns,sy=elf(obj);idx=ns.index('.text.'+f['function']);x=ss[idx];v=b[x[4]:x[4]+x[5]];a=int(f['runtime_address'],16);t=stock(a,len(v));rs=relocs(b,ss,ns,sy,idx);mask={j for off,typ,sym in rs for j in range(off,off+4)};diff=[{'offset':j,'object_byte':v[j],'stock_byte':t[j]} for j in range(len(v)) if j not in mask and v[j]!=t[j]];res.append({'function':f['function'],'hash_verified':sha(b)==f['object_sha256'],'raw_bytes_verified':v.hex()==f['object_bytes'] and t.hex()==f['stock_window_bytes'],'differences_verified':diff==f['non_relocated_differences'],'nonrelocated_mismatches':len(diff)})
ranges=sorted([list(x[:2]) for x in d['new_ranges']]+[x[:2] for x in helpers]);d.update({'pump':pump,'extra_object_hashes':extraobjects,'pool_checks':poolchecks,'residual_checks':res,'helper_ranges':helpers,'helper_bytes':sum(e-a for a,e,_ in helpers),'new_selected_extents':len(d['new_ranges']),'new_selected_bytes':sum(e-a for a,e,_,_ in d['new_ranges']),'new_spans_nonoverlapping':all(x[1]<=y[0] for x,y in zip(ranges,ranges[1:])),'aggregate_selected_bytes':2912+1036,'aggregate_selected_functions':39+7,'denominator':54,'remaining_selected':8});(O/'SEVEN-LINKAGE-VERIFICATION.json').write_text(json.dumps(d,indent=2)+'\n')
def scan(v,path=''):
 if isinstance(v,dict):
  for k,x in v.items():
   if x is False:print(path+'.'+k)
   else:scan(x,path+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):scan(x,path+f'[{i}]')
scan(d);print('new',d['new_selected_extents'],d['new_selected_bytes'],'helpers',len(helpers),d['helper_bytes'])
