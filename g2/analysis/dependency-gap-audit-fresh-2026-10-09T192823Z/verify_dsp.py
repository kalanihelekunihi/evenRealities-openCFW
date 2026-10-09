import pathlib,struct,json,hashlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path('g2/analysis/fresh-provider-evidence-audit-20261009T192906Z')
def sha(b): return hashlib.sha256(b).hexdigest()
def members(path):
 b=path.read_bytes(); assert b[:8]==b'!<arch>\n';p=8;long=b'';out={}
 while p+60<=len(b):
  h=b[p:p+60]; assert h[58:60]==b'`\n';size=int(h[48:58]);name=h[:16].decode().strip();v=b[p+60:p+60+size];p+=60+size+(size&1)
  if name=='//':long=v;continue
  if name=='/':continue
  if name.startswith('/') and name[1:].isdigit():name=long[int(name[1:]):].split(b'\n',1)[0].decode().rstrip('/')
  else:name=name.rstrip('/')
  if name in out:
   suffix=1
   while name+'#'+str(suffix) in out:suffix+=1
   name=name+'#'+str(suffix)
  out[name]=v
 return out

def sections(b):
 assert b[:6]==b'\x7fELF\x01\x01';off=struct.unpack_from('<I',b,32)[0];ents,num,ss=struct.unpack_from('<HHH',b,46);h=[struct.unpack_from('<10I',b,off+i*ents) for i in range(num)];strings=b[h[ss][4]:h[ss][4]+h[ss][5]]
 return [(strings[x[0]:].split(b'\0',1)[0].decode(),x) for x in h]
r=json.loads((SRC/'dsp-object-evidence.json').read_text());b=pathlib.Path('g2/blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes();checks=[{'label':'codec hash','pass':sha(b)==r['codec_payload_sha256']}];ars={};matched=[]
for a in r['archives']:
 q=pathlib.Path(a['archive']);ars[str(q)]=members(q);checks.append({'label':str(q),'pass':sha(q.read_bytes())==a['sha256'] and len(ars[str(q)])==a['objects']})
for m in r['matches']:
 choices=[v for k,v in ars[m['archive']].items() if k.split('#')[0]==m['object'].rstrip('/')];obj=next(v for v in choices if any(name==m['section'] and sha(v[h[4]:h[4]+h[5]])==m['sha256'] for name,h in sections(v)));s=sections(obj);idx,x=next((i,x) for i,(name,x) in enumerate(s) if name==m['section']);v=obj[x[4]:x[4]+x[5]];rel=[{'section':name,'size':h[5],'entry_size':h[9]} for name,h in s if h[1] in (4,9) and h[7]==idx and h[5]]
 offsets=[];p=0
 while True:
  p=b.find(v,p)
  if p<0:break
  offsets.append(hex(p));p+=1
 ok=sha(v)==m['sha256'] and len(v)==m['bytes'] and offsets==m['package_offsets'] and not rel and bool(x[2]&4)
 checks.append({'label':m['object']+':'+m['section'],'pass':ok,'object_sha256':sha(obj),'relocations_targeting_section':rel,'section_flags':hex(x[2]),'offsets':offsets})
 matched.append({'archive':m['archive'],'object':m['object'],'section':m['section'],'sha256':sha(v),'bytes':len(v),'offsets':offsets})
unique={(a,len_,h) for m in matched for a in m['offsets'] for len_,h in [(m['bytes'],m['sha256'])]};ranges=sorted((int(a,16),int(a,16)+n) for a,n,h in unique);union=0;end=-1
for a,z in ranges:union+=max(0,z-max(a,end));end=max(end,z)
checks.append({'label':'deduplication9/1606 nonoverlap','pass':len(unique)==9 and union==1606 and sum(n for a,n,h in unique)==union});checks.append({'label':'BINH B stage2 bounds','pass':all(244032<=a<z<=326092 for a,z in ranges)})
prov=json.loads((SRC/'source-provenance.json').read_text())
for f,v in prov['selected_files'].items():checks.append({'label':'source '+f,'pass':sha(pathlib.Path(f).read_bytes())==v['sha256']})
dw=json.loads((SRC/'dsp-dwarf-sample.json').read_text());tool=pathlib.Path(dw['tool']);checks.append({'label':'target readelf identity','pass':sha(tool.read_bytes())==dw['tool_sha256']});metadata=[]
for sample in dw['samples']:
 obj=next(v for k,v in ars[r['archives'][0]['archive']].items() if k.split('#')[0]==sample['object'].rstrip('/') and sha(v)==sample['object_sha256']);q=ROOT/('DSP-REFERENCE-'+sample['object'].rstrip('/'));q.write_bytes(obj);z=subprocess.run([str(tool),'--debug-dump=info',str(q)],capture_output=True,text=True);checks.append({'label':'DWARF '+sample['object'],'pass':sha(obj)==sample['object_sha256'] and z.returncode==0 and all(line in z.stdout.splitlines() for line in sample['selected_metadata_lines'])});(ROOT/(q.name+'.dwarf.txt')).write_text(z.stdout);metadata.append({'object':sample['object'],'return_code':z.returncode,'stderr':z.stderr})
res={'all_pass':all(x['pass'] for x in checks),'checks':checks,'archive_hits':len(matched),'unique_sections':len(unique),'unique_stock_bytes':union,'stage2_total_bytes':326092-244032,'selected_byte_ratio':union/(326092-244032),'matches':matched,'dwarf':metadata,'limits':'Object/metadata comparison, no source build, execution, runtime placement or global coverage claim'};(ROOT/'DSP-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'all_pass':res['all_pass'],'checks':len(checks),'hits':len(matched),'unique':len(unique),'union':union,'failed':[c['label'] for c in checks if not c['pass']]}))
