from pathlib import Path
import json,hashlib,struct,re,collections
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';D=R/'g2/analysis/source-discovery-parallel-2026-10-09';P=R/'g2/analysis/touch-startup-provider-successor-2026-10-09';T=R/'g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi';I=R/'g2/analysis/touch-newlib14-startup-exit-2026-10-09'
sha=lambda b:hashlib.sha256(b).hexdigest()
f=(O/'finite_verify.py').read_text();exec(f[f.index('def elf('):f.index('checks=[]')])
class Bytes:
 def __init__(self,b):self.b=b
 def read_bytes(self):return self.b
def section(p,n):
 b,ss,ns,sy=elf(p);x=ss[ns.index(n)];return b[x[4]:x[4]+x[5]],x[3]
def member(p,wanted):
 b=p.read_bytes();assert b[:8]==b'!<arch>\n';off=8;strings=b''
 while off<len(b):
  h=b[off:off+60];n=h[:16].decode().strip();size=int(h[48:58]);d=b[off+60:off+60+size];off+=60+size+(size%2)
  if n=='//':strings=d
  elif n.startswith('/') and n[1:].isdigit():n=strings[int(n[1:]):].split(b'/\n')[0].decode()
  else:n=n.rstrip('/')
  if n==wanted:return d
 raise AssertionError(wanted)
def hashes(d,mounts={}):
 rows=[]
 for p,h in d.items():
  q=R/p
  for prefix,root in mounts.items():
   if p.startswith(prefix):q=root/p[len(prefix):];break
  rows.append({'path':str(q.relative_to(R)),'matches':sha(q.read_bytes())==h})
 assert all(x['matches'] for x in rows);return rows
out={}
e=json.loads((D/'event-schema-byte-bindings.json').read_text());b=(R/e['image_path']).read_bytes();assert sha(b)==e['image_sha256'];out['event_sources']=hashes(e['source_hashes']);out['event_slices']=[]
for row in e['rows']:
 off=int(row['runtime'],16)-int(e['conditional_runtime_base'],16);raw=b[off:off+row['bytes']];assert raw.hex()==row['hex'] and sha(raw)==row['sha256'];out['event_slices'].append({'runtime':row['runtime'],'bytes':len(raw),'verified':True})
h=json.loads((D/'hybrid-source-bindings.json').read_text());out['hybrids']=[]
for row in h['hybrid_rows']:
 checks=hashes({x['path']:x['sha256'] for x in row['files']});s=(R/row['files'][0]['path']).read_text()
 for name,syms in row['getter_return_symbols'].items():
  body=re.search(r'int LvpModelGet'+name+r'Size\(void\)\s*\{(.*?)\}',s,re.S).group(1);assert re.findall(r'return sizeof\((\w+)\)',body)==syms
 for file,arrays in row['header_array_sizes'].items():
  text=(R/row['files'][0]['path']).with_name(file).read_text()
  for sym,size in arrays.items():assert re.search(r'\b'+sym+r'\s*\[\s*'+size+r'\s*\]',text)
 out['hybrids'].append({'files':checks,'getters_verified':True,'array_dimensions_verified':True})
r=json.loads((P/'results.json').read_text());z=json.loads((P/'halt-default-results.json').read_text());mounts={'/inputs/':I,'/tool/':T,'/source/':P/'configure-source','/out/':P/'halt-output-attempt2'}
out['startup_inputs']=hashes(r['inputs'],mounts);out['startup_outputs']=hashes(r['outputs']);out['halt_inputs']=hashes(z['inputs'],mounts);out['halt_outputs']=hashes(z['outputs']);out['configure_host']=hashes({r['source_configuration_basis']['path']:r['source_configuration_basis']['sha256']})
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();stock=lambda a,n:fw[32+a-0x3300:32+a-0x3300+n]
out['new_ranges']=[]
for row in r['stock_sections']:
 d,a=section(P/'outputs/linked.elf',row['section']);assert a==int(row['address'],16) and len(d)==row['bytes'] and d==stock(a,len(d)) and sha(d)==row['source_sha256'];out['new_ranges'].append({'address':hex(a),'end':hex(a+len(d)),'bytes':len(d),'exact':True})
d,_=section(P/'halt-output-attempt2/default-halt.o','.text._exit');assert d==stock(0xaa40,4)==bytes.fromhex('fee7c046');out['new_ranges'].append({'address':'0xaa40','end':'0xaa44','bytes':4,'exact':True})
for archive,name,raw,obj,sec in [('libc_nano.a','libc_a-init.o',r['provider_checks'][0]['member_sha256'],P/'outputs/init.o','.text.__libc_init_array'),('libnosys.a','_exit.o',z['member_sha256'],P/'halt-output-attempt2/default-halt.o','.text._exit')]:
 a=T/'arm-none-eabi/lib/thumb/v6-m/nofp'/archive;m=member(a,name);assert sha(m)==raw;assert section(Bytes(m),sec)[0]==section(obj,sec)[0]
for n in ['crti','crtn']:
 for sec in ['.init','.fini']:assert section(P/'outputs'/f'{n}.o',sec)[0]==section(T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp'/f'{n}.o',sec)[0]
out['archive_providers_verified']=True
# CRT concatenation and unrelocated bytes retained
for sec in ['.init','.fini']:assert section(P/'outputs/linked.elf',sec)[0]==section(P/'outputs/crti.o',sec)[0]+section(P/'outputs/crtn.o',sec)[0]
b,ss,ns,sy=elf(P/'outputs/init.o');idx=ns.index('.text.__libc_init_array');x=ss[idx];raw=b[x[4]:x[4]+x[5]];linked=section(P/'outputs/linked.elf','.text')[0];rel=[]
for v in ss:
 if v[1]==9 and v[7]==idx:
  for off in range(v[4],v[4]+v[5],8):
   a,inf=struct.unpack_from('<II',b,off);rel.append((a,inf&255,sy[inf>>8][0]))
covered={j for a,t,n in rel for j in range(a,a+4)};assert all(a==b for i,(a,b) in enumerate(zip(raw,linked)) if i not in covered);out['constructor_relocations']=rel
ranges=sorted((int(x['address'],16),int(x['end'],16)) for x in out['new_ranges']);prior=[(0xa9ac,0xa9d4),(0xa9d4,0xa9e4),(0xaa2c,0xaa3e)];assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]));assert all(max(a,c)>=min(b,d) for a,b in ranges for c,d in prior);out['new_bytes_nonoverlap']=100
v=json.loads((P/'original-results.json').read_text());out['instruction_inputs']=hashes(v['inputs']);assert v['cases']==56==len(v['comparisons']);assert all(x['matches'] for x in v['comparisons']);counts=collections.Counter(x['entry'] for x in v['comparisons']);assert dict(counts)=={'0xa9e4':8,'0xaa44':8,'0xaa50':8,'0xa9ac':32};out['saved_cases']=dict(counts)
for x in v['comparisons']:
 ev=x['observed']['events']
 if x['entry']=='0xa9e4':assert [i.get('provider','callback') for i in ev]==['_init','callback']
 if x['entry']=='0xa9ac':assert ev[-1]=={'provider':'_exit','status':x['status']&0xffffffff} and len(ev)==1+x['handler'] and x['observed']['stop']==['four-halt-branches']
neg=json.loads((P/'halt-results-attempt2.json').read_text());assert neg['bytes']==2 and not neg['exact_stock'];assert section(P/'halt-output-attempt2/halt.o','.text._exit')[0]==bytes.fromhex('fee7');out['negative_halt_preserved']=True
old=json.loads((I/'results.json').read_text())['runs'][0];assert old['compiled_bytes']==68 and len(old['non_relocated_mismatches'])==37
raw,_=section(I/'outputs/init/public.o','.text.__libc_init_array');covered={j for x in old['relocations'] for j in range(x['offset'],x['offset']+4)};mm=[i for i,(a,b) in enumerate(zip(raw,stock(0xa9e4,len(raw)))) if i not in covered and a!=b];assert len(mm)==37;out['original_constructor_37_mismatches_reverified']=True
out['boundary']='Independent hashes, ELF/archive extents and saved receipt/harness inspection; no compilation/emulation rerun; callbacks synthetic; event machine semantics based on existing disassembly, not independently rebuilt source.'
(O/'FOLLOWUP-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS event/hybrid source receipts, startup100 bytes, archive providers,56 saved pairs')
