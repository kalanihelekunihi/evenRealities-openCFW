from pathlib import Path
import json,hashlib,struct,zipfile,re
O=Path(__file__).resolve().parent;I=Path('g2/analysis/iom-strdis-stock-binding-20261009-implementation');C=Path('g2/analysis/cmsis-m55-iar-inclusion-2026-10-09-source-track');sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];base=0x438000;j=json.loads((I/'stock-receipts.json').read_text());field=json.loads((O/'STRDIS-CONTRACT.json').read_text())
for x in j['ranges']:
 a,z=int(x['start'],16),int(x['end_exclusive'],16);v=b[a-base:z-base];ck('IOM original range '+x['label'],sha(v)==x['sha256'] and v.hex()==x['original_bytes_hex'])
# Independently decode Thumb LDR.W aligned PC+4 and STR.W immediate.
for x,old,new in zip(j['branches'],field['before'],field['after']):
 a=int(x['literal_load'],16);h1,h2=struct.unpack_from('<HH',b,a-base);lit=((a+4)&~3)+(h2&4095);store=int(x['store'],16);s1,s2=struct.unpack_from('<HH',b,store-base);word=int.from_bytes(b[lit-base:lit-base+4],'little')
 ck('IOM PC literal '+str(x['rate_argument']),h1==0xf8df and h2>>12==1 and lit==int(x['literal_address'],16) and word==int(old['word_hex'],16)==int(x['stock_word'],16) and word^int(new['word_hex'],16)==0x1000000)
 ck('IOM STR immediate '+str(x['rate_argument']),s1==0xf8c2 and s2==0x12c0)
ck('IOM base pointer literal',int.from_bytes(b[0x55cf38-base:0x55cf3c-base],'little')==0x40050000)
# Authenticate serialized GNU halfwords; listings can contain literal rendering, not code admission.
ok=True;n=0
for ad,hs in re.findall(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+){1,2})\t',(I/'original-disassembly.txt').read_text(),re.M):
 a=int(ad,16);v=b''.join(int(h,16).to_bytes(2,'little') for h in hs.split());ok &= b[a-base:a-base+len(v)]==v;n+=1
ck('IOM serialized listing bytes',ok and n>100)
# Independently decode conditional BEQ and backward B16 selections.
for load,cmpbranch,entry,rate in [(0x55cb6e,0x55cb74,0x55cb88,100000),(0x55cb76,0x55cb7c,0x55cb9a,400000),(0x55cb7e,0x55cb84,0x55cbac,1000000)]:
 h1,h2=struct.unpack_from('<HH',b,load-base);lit=((load+4)&~3)+(h2&4095);v=int.from_bytes(b[lit-base:lit-base+4],'little');op=int.from_bytes(b[cmpbranch-base:cmpbranch-base+2],'little');d=op&255;d=d-256 if d&128 else d
 ck('rate selection '+str(rate),h1==0xf8df and h2>>12==1 and v==rate and op&0xff00==0xd000 and cmpbranch+4+2*d==entry)
for branch in [0x55cb98,0x55cbaa,0x55cbbc]:
 op=int.from_bytes(b[branch-base:branch-base+2],'little');d=op&2047;d=d-2048 if d&1024 else d;ck('common branch '+hex(branch),op&0xf800==0xe000 and branch+4+2*d==0x55cb22)
ck('all module address additions',all(b[a-base:a-base+4]==bytes.fromhex('17eb0632') for a in [0x55cb90,0x55cba2,0x55cbb4]))
ns={'__file__':str(O/'variants.py')};exec((O/'variants.py').read_text().split('with zipfile.ZipFile')[0],ns)
with zipfile.ZipFile('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip') as z:
 ar=z.read(next(n for n in z.namelist() if n.endswith('CMSIS/ARM/Lib/ARM/DSP_LIB_CM55/iar_cortexM55f_math.a')))
ck('CMSIS archive hash',sha(ar)=='034dfb178804c3885b73e15c28bd3ff72c34d5fc9800409c44c453061662c772');objs=dict(ns['members'](ar));parsed={}
for name,v in objs.items():
 if v[:4]!=b'\x7fELF':continue
 h=struct.unpack_from('<HHIIIIIHHHHHH',v,16);ss=[struct.unpack_from('<10I',v,h[5]+i*h[10]) for i in range(h[11])];parsed[name]=(v,ss)
r=json.loads((C/'RESULT.json').read_text());inventory=json.loads((C/'FUNCTION-INVENTORY.json').read_text());constants=json.loads((C/'CONSTANT-CHECK.json').read_text());ck('CMSIS inventory counts',len(parsed)==r['member_count']==15 and len(inventory)==r['inventoried_function_count']==638 and len(r['selected'])==20)
for x in r['selected']:
 v,ss=parsed[x['object']];st=ss[struct.unpack_from('<H',v,50)[0]];names=v[st[4]:st[4]+st[5]];sec=next(s for s in ss if names[s[0]:].split(b'\0',1)[0].decode()==x['section']);body=v[sec[4]+x['start']:sec[4]+x['start']+x['size']];ck('CMSIS body '+x['symbol'],len(body)==x['size'] and sha(body)==x['body_sha256'] and sha(v)==x['object_sha256'])
 for p in x['probes']:
  span=body[p['offset']:p['offset']+p['length']];ck('CMSIS exact span '+x['symbol']+str(p['offset']),sha(span)==p['sha256'] and b.find(span)==-1 and p['stock_hits']==[] and all(p['offset']+p['length']<=q['offset']-x['start'] or p['offset']>=q['offset']-x['start']+8 for q in x['relocations']))
 if x.get('eligible_size_at_least_128'):ck('CMSIS whole raw body '+x['symbol'],b.find(body)==-1 and x['raw_complete_function_hits']==[])
# Constant hashes checked via authored symbol extents from ELF, independently locate symbols.
for x in constants:
 v,ss=parsed[x['object']];found=None
 for s in ss:
  if s[1]!=2:continue
  t=ss[s[6]];names=v[t[4]:t[4]+t[5]]
  for off in range(s[4],s[4]+s[5],s[9]):
   nm,ad,n,info,other,idx=struct.unpack_from('<IIIBBH',v,off)
   if names[nm:].split(b'\0',1)[0].decode()==x['symbol']:found=v[ss[idx][4]+ad:ss[idx][4]+ad+n]
 ck('CMSIS table '+x['symbol'],found is not None and len(found)==x['size'] and sha(found)==x['sha256'] and b.find(found)==-1 and x['relocations']==[] and x['complete_data_hits']==[])
zero=[x for x in r['selected'] if x['eligible_size_at_least_128'] and not x['relocations']];ck('four qualifying nonrelocated functions',len(zero)==4);ck('twenty spans/four tables',sum(len(x['probes']) for x in r['selected'])==20 and len(constants)==4)
res={'all_pass':all(x['pass'] for x in checks),'checks':checks,'counts':{'symbol_records':len(inventory),'unique_object_section_start_size_tuples':len({(x['object'],x['section'],x['start'],x['size']) for x in inventory}),'nonrelocated_complete_qualifying_functions':len(zero)},'scope':'Static original-byte and raw-negative receipt checks; no firmware/object execution, extraction or canonical admission. Relocation parser/target semantics not independently executed.'};(O/'IOM-CMSIS-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'all_pass':res['all_pass'],'checks':len(checks),'failed':[x['check'] for x in checks if not x['pass']],'counts':res['counts']},indent=2))
