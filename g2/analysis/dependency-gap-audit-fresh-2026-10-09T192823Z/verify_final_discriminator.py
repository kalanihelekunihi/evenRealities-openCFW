from pathlib import Path
import json,hashlib,re,struct
O=Path(__file__).resolve().parent
D=Path('g2/analysis/csky-inverse-split-discriminator-20261009T204649Z')
P=Path('g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z')
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in json.loads((D/'DELIVERABLES.json').read_text())['files'].items():ck('sealed deliverable '+p,sha(Path(p))==h)
for p,h in json.loads((D/'reference-hashes.json').read_text()).items():ck('reference identity '+p,sha(Path(p))==h)
e=json.loads((D/'execution.json').read_text());r=json.loads((D/'results.json').read_text());log=(D/'run/mem.log').read_text()
ck('raw log receipt and binary identity',log==e['memlog'] and sha(D/'discriminator.elf')==e['elf_sha256'] and e['returncode']==0)
ck('simulator CPU and offline execution',e['command'][e['command'].index('-cpu')+1]=='ck804ef' and '--network=none' in e['command'] and '--read-only' in e['command'])
rows=[]
for line in log.splitlines():
 if line.startswith('case='):rows.append(dict(re.findall(r'(\S+?)=(\S+)',line)))
ck('twelve raw rows equal structured results',rows==r['rows'] and len(rows)==12 and log.endswith('PASS discriminator_cases=12\n'))
def s32(v):return v if v<0x80000000 else v-0x100000000
def pneg(v):
 out=0
 for k in [0,16]:
  x=(v>>k)&65535;x=x if x<32768 else x-65536
  out|=(min(32767,-x)&65535)<<k
 return out
# Mathematical formula verification only; no guest execution/replay.
ck('whole Q15 domain residue deduction',all((s32(pneg((a*16384)&0xffffffff))+a*16384)==(0 if a%4==0 else 65535 if a%4==2 else 65536) for a in range(-32768,32768)))
for row in rows:
 a=int(row['amplitude']);p=(a*16384)&0xffffffff;n=pneg(p);acc=(s32(n)+a*16384)&0xffffffff;imag=acc>>16
 ck('independent arithmetic amplitude '+str(a),row['product']==f'{p:08x}' and row['packed_neg']==f'{n:08x}' and row['accumulator']==f'{acc:08x}' and row['real_C/model/asm']=='/'.join([str(a//2)]*3) and row['imag_C/model/asm']==f'0/{imag}/{imag}' and int(row['original_differences'])==int(a%2!=0))
ck('all observed memory/prediction/diagnostic checks zero',all(all(row[k]=='0' for k in ['guard_mask','predictions_failed','diagnostic_differences']) for row in rows))
ck('five expected original differences',sum(int(x['original_differences']) for x in rows)==r['original_C_expected_differences']==5)
h=(D/'discriminator.c').read_text()
ck('checks before arithmetic and mismatch branch',h.index('if(guard){')<h.index('product=probe_mulcax')<h.index('if(predictions||'))
ck('independent input/tail and all buffer canaries',all(t in h for t in ['all[]={&src,&orig,&model,&stock}','for(k=0;k<4;k++)','for(i=0;i<1024;i++)if(src.x[i]!=((i==0||i==512)?amp:0))','for(i=512;i<1024;i++)if(p->x[i]!=0x5a5a)','guard|=verify(amps[c],&orig)|verify(amps[c],&model)|verify(amps[c],&stock)']))
ck('full output independent oracle', 'for(i=0;i<512;i++){q15_t original_want=i==0?expected_real[c]:0;' in h and 'i==1?expected_imag[c]:0' in h)
ck('unchanged table and linker fixture',all((D/n).read_bytes()==(P/n).read_bytes() for n in ['tables.h','harness.ld']))
ck('actual exchanged subtract probe','mulacsx.s16.s r2,r0,r1' in (D/'mac-difference-probe.S').read_text())
b=(D/'discriminator.elf').read_bytes();hdr=struct.unpack_from('<HHIIIIIHHHHHH',b,16);ph=[struct.unpack_from('<8I',b,hdr[4]+i*hdr[8]) for i in range(hdr[9])]
ck('ELF machine and executable RAM mapping',hdr[0]==2 and hdr[1]==252 and hdr[3]==0x10000 and all(0x10000<=x[2]<=x[2]+x[5]<=0x1000000 for x in ph if x[0]==1))
ck('all compile/link receipts successful',all(x['returncode']==0 for x in json.loads((D/'build-results.json').read_text())))
p=json.loads((D/'preservation.json').read_text());ck('owner preservation receipt clean',p['seal_mismatches']==p['audit_mismatches']==[] and p['audit_inputs']==110 and len(p['checkpoints'])==4 and all(p['checkpoints'].values()) and p['index_stable_during_seal'])
result={'all_pass':all(x['pass'] for x in checks),'checks':checks,'scope':'Independent static receipt/hash/harness/formula audit; no simulator replay or hardware execution. Full-domain formula enumeration is mathematical deduction, not 65536 executed firmware cases. Owner preservation receipt inspected, not a fresh repository-wide seal.'}
(O/'FINAL-DISCRIMINATOR-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'all_pass':result['all_pass'],'checks':len(checks),'failures':[x['check'] for x in checks if not x['pass']]},indent=2))
