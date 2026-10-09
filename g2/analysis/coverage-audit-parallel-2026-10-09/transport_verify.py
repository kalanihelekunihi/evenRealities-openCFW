from pathlib import Path
import json,hashlib,re,struct
R=Path.cwd();D=R/'g2/analysis/source-discovery-parallel-2026-10-09';O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';a=json.loads((D/'TRANSPORT-CROSS-VERSION-RECEIPT.json').read_text());h=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def check(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
b=(R/a['image']).read_bytes();check('locked input',h(b)==a['sha256']);base=0x437fe0
for x in a['ranges']:check(x['start']+' full interval',h(b[int(x['start'],16)-base:int(x['end_exclusive'],16)-base])==x['sha256'])
for p,v in a['literal_values'].items():check(p+' literal',struct.unpack_from('<I',b,int(p,16)-base)[0]==int(v,16))
tsv=(R/'g2/symbols/apollo_main.tsv').read_text();line=next(l for l in tsv.splitlines() if '\tHciDrvRadioBoot\t' in l);check('symbol extent and hash',line.split('\t')[:3]==['0x004B48A6','0x004B49CE','296'] and line.split('\t')[-1]==a['ranges'][0]['sha256'])
for k in ['emulator_audit','comparison_image']:check(k+' separate input',h((Path(a[k]['path']) if Path(a[k]['path']).is_absolute() else R/a[k]['path']).read_bytes())==a[k]['sha256'])
listing={};total=0
for p in sorted(D.glob('transport-2.2.6.10-*-disassembly.txt')):
 count=0
 for z in p.read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\t([0-9a-f]{4}(?: [0-9a-f]{4})?)\s+\t(.+)$',z)
  if not m:continue
  addr=int(m[1],16);raw=b''.join(int(t,16).to_bytes(2,'little') for t in m[2].split());check('byte '+hex(addr),b[addr-base:addr-base+len(raw)]==raw);listing[addr]=(raw,m[3]);count+=1
 total+=count
# independently decode Thumb BL immediate from bytes
for pc,target in [(0x4b48ca,0x52dd94),(0x52ddf8,0x55c2bc),(0x52df6e,0x480fd6),(0x52e4e4,0x480fd6),(0x52e4f2,0x480fd6),(0x52e8fa,0x52e854)]:
 p,q=struct.unpack_from('<HH',b,pc-base);s=(p>>10)&1;i1=1^((q>>13)&1)^s;i2=1^((q>>11)&1)^s;imm=(s<<24)|(i1<<23)|(i2<<22)|((p&1023)<<12)|((q&2047)<<1);imm=imm-(1<<25) if s else imm
 check('decoded BL '+hex(pc),(p&0xf800)==0xf000 and (q&0xd000)==0xd000 and pc+4+imm==target)
for pc,hw in [(0x4b48c8,0x2006),(0x4b49a8,0x2175),(0x4b49ba,0x2104),(0x4b49bc,0x203b),(0x52df6a,0x2100),(0x52df6c,0x2095),(0x52e4e0,0x2100),(0x52e4e2,0x205d),(0x52e4ee,0x2101),(0x52e4f0,0x205d),(0x52e872,0x200f),(0x52e880,0x200f)]:check('decoded MOVS '+hex(pc),struct.unpack_from('<H',b,pc-base)[0]==hw)
check('IOM init stores module at handle+4','str\tr0, [r2, #4]' in listing[0x55c320][1]);check('configure loads handle module','ldr\tr6, [r5, #4]' in listing[0x55cad4][1]);check('base calculation register encoding',listing[0x55cae2][0]==bytes.fromhex('17eb0631'))
check('IOM6 MMIO arithmetic',0x40050000+(6<<12)==0x40056000);check('ready bit GPIO number',3*32+21==117)
(O/'TRANSPORT-INDEPENDENT-VERIFICATION.json').write_text(json.dumps({'status':'PASS','checks_count':len(checks),'disassembly_records':total,'checks':checks,'symbol_table_sha256':h((R/'g2/symbols/apollo_main.tsv').read_bytes()),'physical_wiring_proven':False,'execution':False},indent=2)+'\n');print(total,'records;',len(checks),'checks PASS')
