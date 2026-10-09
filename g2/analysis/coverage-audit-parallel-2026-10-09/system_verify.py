from pathlib import Path
import json,hashlib,struct,collections
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';P=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09';prior=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((P/'selection.json').read_text());r=json.loads((P/'results.json').read_text());a=json.loads((P/'acquisition.json').read_text());old=json.loads((prior/'results.json').read_text());fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
# Reuse only the independent parser definition; do not execute prior verification.
src=(O/'finite_verify.py').read_text();exec(src[src.index('def elf('):src.index('checks=[]')])
units=[]
for u in r['units']:
 argv=u['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};q={'unit':u['source_unit'],'success':u['exit_code']==0,'device_retained':'-DCY8C4046FNI_T412' in argv,'interface_precedes_shim':argv.index('-I/interface')<argv.index('-I/headers'),'input_hashes_verified':all(sha((mounts['/'+n.split('/')[1]]/'/'.join(n.split('/')[2:])).read_bytes())==v for n,v in u['consumed_input_hashes'].items()),'output_hashes_verified':all(sha((P/'outputs'/u['source_unit']/n).read_bytes())==v for n,v in u['output_hashes'].items()),'official_header_consumed':u['consumed_input_hashes'].get('/interface/system_cat2.h')==a['sha256'],'old_shim_not_consumed':'/headers/system_cat2.h' not in u['consumed_input_hashes']};b,ss,ns,syms=elf(P/'outputs'/u['source_unit']/'public.o');rows=[]
 for f in u['functions']:
  name='.text.'+f['function'];z={'function':f['function'],'status':f['comparison_status']}
  if name not in ns:z['absent_verified']=f['comparison_status']=='expected_section_absent'
  else:
   idx=ns.index(name);x=ss[idx];data=b[x[4]:x[4]+x[5]];rel=[]
   for t in ss:
    if t[1]==9 and t[7]==idx:
     for off in range(t[4],t[4]+t[5],8):
      pos,info=struct.unpack_from('<II',b,off);rel.append({'offset':pos,'type':info&255,'symbol':syms[info>>8][0]})
   target=fw[f['absolute_payload_offset']:f['absolute_payload_offset']+f['historical_code_bytes']];diff=[i for i in range(min(len(data),len(target))) if data[i]!=target[i]];z.update({'section_hash_verified':sha(data)==f['compiled_sha256'],'length_verified':len(data)==f['compiled_bytes'],'relocations_verified':rel==f['relocations'],'differences_verified':diff==f['overlap_mismatched_positions'],'relocations':rel})
  rows.append(z)
 q['functions']=rows;units.append(q)
oldfailed=[f for u in old['units'] if u['exit_code'] for f in u['functions']];counts=collections.Counter(f['comparison_status'] for u in r['units'] for f in u['functions']);out={'acquired_header_hash_verified':sha((P/a['path']).read_bytes())==a['sha256'],'independent_bsp_header_identical':(P/a['path']).read_bytes()==(R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/infineon-cy8cproto-040t/system_cat2.h').read_bytes(),'selection_hash_verified':sha((P/'selection.json').read_bytes())==r['selection_sha256'],'prior_selection_hash_verified':sha((prior/'selection.json').read_bytes())==s['prior_selection_sha256'],'exact_same_twelve_target_rows':sorted(({k:v for k,v in f.items() if k!='comparison_status'} for f in oldfailed),key=lambda x:x['function'])==sorted(s['functions'],key=lambda x:x['function']),'new_result_counts':dict(counts),'units':units,'remaining_counts_after_nine_review':{'relocation_extent':16+counts['relocation_or_extent_boundary'],'absent':2+counts['expected_section_absent'],'inline':1},'original_failure_receipt_sha256':sha((prior/'results.json').read_bytes())};(O/'SYSTEM-INTERFACE-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
