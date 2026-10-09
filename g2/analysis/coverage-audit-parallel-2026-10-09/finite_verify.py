from pathlib import Path
import json,struct,hashlib,collections
R=Path.cwd(); P=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09'; O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest()
s=json.loads((P/'selection.json').read_text());r=json.loads((P/'results.json').read_text());ex=json.loads((P/'extent-followup.json').read_text());fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
def elf(path):
 b=path.read_bytes(); h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);ss=[struct.unpack_from('<10I',b,h[5]+i*h[10]) for i in range(h[11])]; st=ss[h[12]];names=b[st[4]:st[4]+st[5]];z=lambda d,k:d[k:d.index(b'\0',k)].decode(); ns=[z(names,x[0]) for x in ss];syms=[]
 for x in ss:
  if x[1]==2:
   t=ss[x[6]];strings=b[t[4]:t[4]+t[5]]
   for off in range(x[4],x[4]+x[5],16):
    n,v,size,info,other,idx=struct.unpack_from('<IIIBBH',b,off);syms.append((z(strings,n),v,size,idx))
 return b,ss,ns,syms
checks=[];unitchecks=[]
for u in r['units']:
 q={'unit':u['source_unit'],'exit_code':u['exit_code']}
 if u['exit_code']==0:
  q['outputs_verified']=all(sha((P/'outputs'/u['source_unit']/n).read_bytes())==v for n,v in u['output_hashes'].items())
  argv=u['argv']; mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'}
  q['inputs_verified']=all(sha((mounts['/'+n.split('/')[1]]/ '/'.join(n.split('/')[2:])).read_bytes())==v for n,v in u['consumed_input_hashes'].items())
  b,ss,ns,syms=elf(P/'outputs'/u['source_unit']/'public.o')
  for e in ex:
   if e['function'] not in [f['function'] for f in u['functions']]:continue
   idx=ns.index('.text.'+e['function']);x=ss[idx];data=b[x[4]:x[4]+x[5]];a=e['address'];stock=fw[32+a-0x3300:32+a-0x3300+len(data)];maps=sorted((v,n) for n,v,_,k in syms if k==idx and n.startswith(('$t','$d'))); dstart=min(v for v,n in maps if n.startswith('$d'));refs=[];off=0
   while off<dstart:
    hw=struct.unpack_from('<H',stock,off)[0]
    if hw&0xf800==0x4800: refs.append({'instruction':a+off,'target':((a+off+4)&~3)+(hw&255)*4})
    off+=4 if hw>>11 in (29,30,31) else 2
   targets=set(t['target'] for t in refs);pool=set(range(a+dstart,a+len(data),4)); rel=[ns[i] for i,v in enumerate(ss) if v[1] in (4,9) and v[7]==idx]
   checks.append({'function':e['function'],'address':hex(a),'section_bytes':len(data),'historical_code_bytes':e['historical_code_bytes'],'mapping_symbols':maps,'tail_before_pool_hex':stock[e['historical_code_bytes']:dstart].hex(),'exact':data==stock,'hashes_verified':sha(data)==e['compiled_sha256']==e['stock_full_span_sha256'],'relocations':rel,'literal_refs_verified':refs==e['original_literal_references'],'all_pool_words_referenced':pool<=targets,'pool_bytes':len(data)-dstart,'range_end':hex(a+len(data))})
 unitchecks.append(q)
counts=collections.Counter(f['status'] for f in s['functions']); statuses=collections.Counter(f['comparison_status'] for u in r['units'] for f in u['functions']);ranges=sorted((e['address'],e['address']+e['compiled_section_bytes']) for e in ex)
out={'selection_hash_verified':sha((P/'selection.json').read_bytes())==r['selection_sha256'],'payload_hash_verified':sha(fw)==s['payload_sha256'],'historical_rows':len(s['functions']),'selection_status_counts':dict(counts),'raw_result_counts':dict(statuses),'target_slice_hashes_verified':all(sha(fw[f['absolute_payload_offset']:f['absolute_payload_offset']+f['historical_code_bytes']])==f['target_code_sha256'] for f in s['functions']),'units':unitchecks,'extents':checks,'nine_nonoverlapping':all(x[1]<=y[0] for x,y in zip(ranges,ranges[1:])),'additional_full_section_bytes':sum(e['compiled_section_bytes'] for e in ex)}
(O/'FINITE-CENSUS-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
