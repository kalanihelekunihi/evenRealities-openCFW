"""Independent native extraction plus exact-byte and mutation controls."""
from pathlib import Path
import json, subprocess, hashlib, re, collections
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
TOOLS=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
rows=json.loads((OUT/'function-matches.json').read_text())
images={r['id']:r for r in json.loads((OUT/'authentication.json').read_text())['images']}
prior=json.loads((ROOT/'g2/analysis/shortcut-provider-archive-20261009-agent1/function-inventory.json').read_text())
prior_symbols={r['symbol'] for r in prior['functions'] if r.get('candidates')}
def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')
 return p.stdout
validated=[]; uniq=set(); classify=collections.Counter()
pins=[]
for line in run(['git','-C',ROOT,'ls-files','--stage','third-party']).decode().splitlines():
 if not line.startswith('160000 '): continue
 left,path=line.split('\t'); pin=left.split()[1]
 if not (ROOT/path/'.git').exists():
  pins.append({'path':path,'gitlink':pin,'actual_head':None,'status':'uninitialized; no source contents scanned'}); continue
 actual=run(['git','-C',ROOT/path,'rev-parse','HEAD']).decode().strip()
 assert actual==pin,(path,pin,actual)
 pins.append({'path':path,'gitlink':pin,'actual_head':actual})
(OUT/'submodule-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
for row in rows:
 row['stock_region_status']='historical_catalogue_overlap' if row['catalogue_overlaps'] else 'byte_occurrence_only; stock code boundary not proved by this scan'
 if row['image'] in ('binh_a_stage2_xip','binh_a_stage2_sram'):
  row['conditional_runtime']=(0x10203004 if row['image'].endswith('xip') else 0x10023400)+row['image_offset']
 row['prior_provider_symbol']=row['symbol'] in prior_symbols
 classify[('prior_' if row['prior_provider_symbol'] else 'other_')+row['class']]+=1
 if row['class']!='exact_bytes': continue
 key=(row['provider'],row['member'],row['symbol'])
 if key in uniq: continue
 uniq.add(key)
 if row['member']:
  member=run([TOOLS/'csky-elfabiv2-ar','p',ROOT/row['provider'],row['member']])
 else: member=(ROOT/row['provider']).read_bytes()
 obj=OUT/'validation-member.o'; obj.write_bytes(member)
 symbols=run([TOOLS/'csky-elfabiv2-readelf','-sW',obj]).decode()
 sections=run([TOOLS/'csky-elfabiv2-readelf','-SW',obj]).decode()
 selected=[]
 for line in symbols.splitlines():
  parts=line.split()
  if len(parts)>=8 and parts[-1]==row['symbol'] and parts[3]=='FUNC' and parts[6].isdigit(): selected.append(parts)
 if not selected and row['member']:
  extract=OUT/'native-extract'; extract.mkdir(exist_ok=True)
  names=run([TOOLS/'csky-elfabiv2-ar','t',ROOT/row['provider']]).decode().splitlines()
  for occurrence in range(2,names.count(row['member'])+1):
   proc=subprocess.run([str(TOOLS/'csky-elfabiv2-ar'),'xN',str(occurrence),str(ROOT/row['provider']),row['member']],cwd=extract,capture_output=True)
   assert proc.returncode==0,proc.stderr
   member=(extract/row['member']).read_bytes(); obj.write_bytes(member)
   symbols=run([TOOLS/'csky-elfabiv2-readelf','-sW',obj]).decode()
   sections=run([TOOLS/'csky-elfabiv2-readelf','-SW',obj]).decode()
   for line in symbols.splitlines():
    parts=line.split()
    if len(parts)>=8 and parts[-1]==row['symbol'] and parts[3]=='FUNC' and parts[6].isdigit(): selected.append(parts)
   if selected: break
 assert selected,row
 sy=next(x for x in selected if int(x[2],0)==row['bytes'])
 secidx=int(sy[6]); value=int(sy[1],16)&~1
 sm=re.search(r'^\s*\[\s*'+str(secidx)+r'\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',sections,re.M)
 assert sm,(row,sections)
 base,off=int(sm[2],16),int(sm[3],16)
 code=member[off+value-base:off+value-base+row['bytes']]
 assert hashlib.sha256(code).hexdigest()==row['function_sha256']
 image=images[row['image']]; stock=Path(image['path']).read_bytes() if Path(image['path']).is_absolute() else (ROOT/image['path']).read_bytes()
 at=row['image_offset']; actual=stock[at:at+len(code)]
 assert code==actual
 changed=bytearray(code); changed[len(changed)//2]^=1
 assert bytes(changed)!=actual
 # Deliberate +/-2 placement and single-bit controls test the selected exact extent, not absence elsewhere.
 shifted=[stock[at+d:at+d+len(code)]==code for d in (-2,2) if at+d>=0]
 validated.append({'provider':row['provider'],'member':row['member'],'symbol':row['symbol'],'bytes':len(code),'sha256':hashlib.sha256(code).hexdigest(),'native_symbol_and_section_agree':True,'single_bit_control_rejected':True,'shifted_equal_controls':shifted})
(OUT/'validation.json').write_text(json.dumps({'validated_unique_functions':len(validated),'native_validations':validated,'candidate_classification':dict(classify),'masked_matches':'not independently accepted; earlier branch-target contradiction remains authoritative'},indent=2)+'\n')
(OUT/'classified-matches.json').write_text(json.dumps(rows,indent=2)+'\n')
print('validated',len(validated),dict(classify))
