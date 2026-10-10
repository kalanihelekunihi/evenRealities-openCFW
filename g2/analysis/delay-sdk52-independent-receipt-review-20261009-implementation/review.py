from pathlib import Path
from fractions import Fraction
import hashlib,json,struct,zipfile
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;A=R/'g2/analysis/coverage-audit-parallel-2026-10-09/delay-sdk52-discriminator';sha=lambda b:hashlib.sha256(b).hexdigest();idx=sha((R/'.git/index').read_bytes())
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
seal=json.loads((A/'EXECUTION-DELIVERABLE-HASHES.json').read_text())
for n,h in seal.items():ck('audit execution artifact hash '+n,sha((A/n).read_bytes())==h)
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();ck('locked main hash',sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863');im=raw[32:];code=im[0x4807a0-0x438000:0x4807f0-0x438000];ck('all 80 original wrapper bytes',sha(code)=='f95193c502160b469e1579e13223f1cdf488a2d8fab9ec07f686c9101fbed753')
ck('250/96 floating literal bits and status address',struct.unpack_from('<III',im,0x4807f0-0x438000)==(0x437a0000,0x42c00000,0x40021000))
for a,h in [(0x4807a6,'b8ee400a'),(0x4807aa,'bfee ed0a'.replace(' ','')),(0x4807ce,'20ee200a'),(0x4807d6,'80ee200a'),(0x4807da,'bceec00a'),(0x4807be,'0f21'),(0x4807e2,'1821')]:ck('original arithmetic/adjustment bytes '+hex(a),im[a-0x438000:a-0x438000+len(h)//2].hex()==h)
a=0x4807ea;h1,h2=struct.unpack_from('<HH',im,a-0x438000);s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s;off=(s<<24)|(i1<<23)|(i2<<22)|((h1&1023)<<12)|((h2&2047)<<1);off-= (1<<25) if s else 0;ck('original BL targets ITCM 0x40',a+4+off==0x40)
z=zipfile.ZipFile(Path.home()/'Downloads/AmbiqSuite_5.2.0.zip');member='AmbiqSuite_5.2.0/AmbiqSuite_5.2.0/mcu/apollo510/hal/mcu/am_hal_utils.c';src=z.read(member);ck('SDK source member hash',sha(src)=='a4204e045b06d377eac4d2d1dec3adfc4c788ecf905bc002080eb5e769aad2b2');text=src.decode();ck('SDK integer formula and adjustment',all(x in text for x in ['ui32us * ITERATIONS_PER_MICROSEC_FOR_250M + (ui32us + 1) / 3','ui32CycleCntAdj = 25;','#define ITERATIONS_PER_MICROSEC_FOR_250M    (83)']))
# Exact rational nearest-even binary32 oracle, independent of owner's host-float oracle.
def f32(q):
 q=Fraction(q)
 if q==0:return q
 e=q.numerator.bit_length()-q.denominator.bit_length()
 def two(n):return Fraction(1<<n) if n>=0 else Fraction(1,1<<-n)
 if q<two(e):e-=1
 spacing=two(e-23);v=q/spacing;n=v.numerator//v.denominator;rem=v-n
 if rem>Fraction(1,2) or rem==Fraction(1,2) and n%2:n+=1
 return n*spacing
inputs=[0,1,2,3,4,5,10,100,2096,2097,2098,2099,2100,65535,65536,65537,16777215,16777216,16777217]
r=json.loads((A/'linux-execution-receipt.json').read_text());p=json.loads((A/'iteration-predictions.json').read_text());ck('exact 38 planned/attempted/passed',r['total_planned']==r['attempted']==r['passed']==38 and len(r['results'])==len(p['rows'])==38);ck('exact unique input-mode set',{(x['us'],x['hp']) for x in r['results']}=={(i,h) for i in inputs for h in [False,True]})
rows=[];diffs=0
for o in r['results']:
 us=o['us'];hp=o['hp'];base=int(f32(us)*32);rawcount=int(f32(f32(f32(base)*250)/96)) if hp else base;adj=24 if hp else 15;loop=rawcount-adj if rawcount>adj else None;sdkraw=us*83+(us+1)//3 if hp else us*32;sdkadj=25 if hp else 15;sdkloop=sdkraw-sdkadj if sdkraw>sdkadj else None
 ck('independent count '+str((us,hp)),o['predicted']==o['loop_argument']==loop and o['error'] is None and o['pass'])
 ck('FPSCR nearest-even and allowed cumulative flags '+str((us,hp)),o['fpscr_initial']==0 and o['fpscr_final'] in (0,0x10) and (o['fpscr_final']&(3<<22))==0)
 pre=[0x4807a0,0x4807a2,0x4807a6,0x4807aa,0x4807ae,0x4807b2,0x4807b4,0x4807b6,0x4807ba,0x4807bc];path=[0x4807c2,0x4807c6,0x4807ca,0x4807ce,0x4807d2,0x4807d6,0x4807da,0x4807de,0x4807e2] if hp else [0x4807be,0x4807c0];tail=[0x4807e4,0x4807e6]+([0x4807e8,0x4807ea] if loop is not None else [0x4807ee])
 ck('exact instruction path and stop before loop '+str((us,hp)),[int(a,16) for a in o['trace']]==pre+path+tail and int(o['stop_pc'],16)==(0x40 if loop is not None else 0x480))
 ck('bounded conversions/intermediates '+str((us,hp)),0<=base<=0xffffffff and 0<=rawcount<=0xffffffff and 0<=sdkraw<=0xffffffff and us+1<=0xffffffff)
 diffs+=loop!=sdkloop;rows.append({'us':us,'hp':hp,'independent_raw_stock':rawcount,'stock_argument':loop,'SDK_raw':sdkraw,'SDK_argument':sdkloop,'FPSCR_final':o['fpscr_final']})
ck('no ITCM instruction executed',r['loop_executed'] is False and all('0x40' not in x['trace'] for x in r['results']))
ck('index unchanged by review',sha((R/'.git/index').read_bytes())==idx)
out={'outcome':'PASS','checks':checks,'check_count':len(checks),'cases':rows,'different_loop_counts':diffs,'exact_arithmetic_oracle':'fractions.Fraction IEEE binary32 nearest-even at every step; conversion to uint32 truncates','no_reexecution':True,'scope':'Original bytes, complete wrapper instruction traces, seeded FPSCR/CPACR/performance register, stop at ITCM entry; no loop or physical timing','index_sha256':idx};(D/'REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'checks;',diffs,'count differences across 38 inputs/modes')
