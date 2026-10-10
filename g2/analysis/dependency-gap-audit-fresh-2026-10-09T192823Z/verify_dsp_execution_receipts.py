import pathlib,json,hashlib,struct,re
O=pathlib.Path(__file__).resolve().parent
Q=pathlib.Path('g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z')
ns={'__file__':str(O/'verify_dsp.py')}
exec((O/'verify_dsp.py').read_text().split('\nr=json.loads')[0],ns)
sha=ns['sha'];sections=ns['sections'];checks=[];inputs={}
def check(label,ok,**extra):checks.append({'label':label,'pass':bool(ok),**extra})
identity=json.loads((Q/'simulator-build-identity.json').read_text())
check('retained built QEMU binary hash',sha(pathlib.Path(identity['binary']).read_bytes())==identity['sha256'])
elfs={}
for name,v in json.loads((Q/'elf-placement.json').read_text())['elfs'].items():
 b=(Q/name).read_bytes();h=struct.unpack_from('<HHIIIIIHHHHHH',b,16)
 ph=[struct.unpack_from('<8I',b,h[4]+i*h[8]) for i in range(h[9])]
 loads=[x for x in ph if x[0]==1];actual=[{'address':hex(x[2]),'memory_bytes':x[5]} for x in loads]
 check('ELF identity/placement '+name,sha(b)==v['sha256'] and h[0]==2 and h[1]==252 and h[3]==int(v['entry'],16)==0x10000 and actual==v['segments'] and all(0x10000<=x[2]<=x[2]+x[5]<=0x1000000 for x in loads),bss_zero_fill_bytes=sum(x[5]-x[4] for x in loads))
 elfs[name]=(b,sections(b));inputs[name]=sha(b)
runs=[('corpus','corpus-execution.json'),('stages','stage-execution.json'),('pneg','pneg-execution.json'),('isa-memlog-run','isa-memlog-execution.json')]
runs=[(a,json.loads((Q/b).read_text())) for a,b in runs]+[(x['label'],x) for x in json.loads((Q/'kernel-executions.json').read_text())]
for folder,r in runs:
 f=Q/folder/'mem.log';cmd=r.get('command',r.get('run_command'))
 check('raw memlog/target command '+folder,f.read_text()==r['memlog'] and cmd[cmd.index('-cpu')+1]=='ck804ef' and cmd[cmd.index('-M')+1]=='smartl',memlog_sha256=sha(f.read_bytes()))
 inputs[str(f.relative_to(Q))]=sha(f.read_bytes())
summary=json.loads((Q/'numerical-summary.json').read_text());log=(Q/'corpus/mem.log').read_text()
m=re.search(r'DIFF rfft case=(\d+) index=(\d+) c=(\d+) asm=(\d+)',log);case,idx,c,a=map(int,m.groups())
helper=10*7*2+10*2+10*7;bitrev=3;passedFFT=case-helper-bitrev;remaining=14*2*2-passedFFT-1
check('corpus arithmetic/sign conversion',helper==summary['helper_c_assembly_passes']==230 and bitrev==summary['bitreversal_c_assembly_passes']==3 and passedFFT==summary['fft_c_assembly_passes_before_first_failure']==23 and remaining==summary['fft_cases_not_executed_after_stop']==32 and case==summary['corpus_passes']==256 and idx==summary['first_difference']['index']==1 and c-65536==summary['first_difference']['c_signed']==-20868 and a-65536==summary['first_difference']['assembly_signed']==-20866 and 256+1+32==289)
ordinal=case-helper-bitrev;check('first failing vector loop ordinal',(ordinal//4,(ordinal%4)//2,ordinal%2)==(5,1,1))
check('abs oracle actual55 cases',5*11==summary['abs_max_assembly_oracle_passes']==55 and 'ABS ORACLE PASS cases=55' in (Q/'abs-oracle/mem.log').read_text())
header=(Q/'tables.h').read_text();prov=json.loads((Q/'table-provenance.json').read_text());tables={}
for name,sym in [('bitrev','cskyBitRevIndexTable_fixed_256'),('twiddle','twiddleCoef_256_q15'),('realcoef','realCoefAQ15_512')]:
 vals=list(map(int,re.search(r'\b'+name+r'\[\].*?=\{([^}]*)\}',header,re.S)[1].split(',')))
 data=b''.join((v&65535).to_bytes(2,'little') for v in vals);expected=next(x for x in prov if x['symbol']==sym)
 check('generated exact table '+name,len(data)==expected['bytes'] and sha(data)==expected['stock_sha256']);tables[name]=data
b,s=elfs['harness.elf'];symbols={}
for n,h in s:
 if h[1]!=2:continue
 st=s[h[6]][1];strings=b[st[4]:st[4]+st[5]]
 for pos in range(h[4],h[4]+h[5],h[9]):
  name,val,size,info,other,idx=struct.unpack_from('<IIIBBH',b,pos)
  if name and idx and idx<len(s):symbols[strings[name:].split(b'\0',1)[0].decode()]=(val,size,idx)
for name,data in tables.items():
 val,size,idx=symbols[name];h=s[idx][1];actual=b[h[4]+val-h[3]:h[4]+val-h[3]+size]
 check('linked exact table '+name,actual==data and val%4==0)
original=json.loads((O/'DSP-INDEPENDENT-VERIFICATION.json').read_text());old=json.loads((O/'DSP-SOURCE-ASSEMBLY-INDEPENDENT-VERIFICATION.json').read_text())
for c in old['checks']:
 if not c['label'].startswith('.text.'):continue
 found=[]
 for obj in Q.glob('asm_*.o'):
  v=obj.read_bytes()
  for n,h in sections(v):
   if n==c['label']:found.append(v[h[4]:h[4]+h[5]])
 expected=next(x['sha256'] for x in original['matches'] if x['section']==c['label'])
 check('renamed exact assembly '+c['label'],len(found)==1 and len(found[0])==c['bytes'] and sha(found[0])==expected)
manual=pathlib.Path('g2/analysis/csky-dsp-negation-semantics-2026-10-09-source-track');prov=json.loads((manual/'PROVENANCE.json').read_text())
for name,v in prov['files'].items():
 f=pathlib.Path('third-party/tools/ghidra-csky/C-SKY_ISA_Reference_Guides')/name
 check('retained manual identity '+name,sha(f.read_bytes())==v['sha256'] and f.stat().st_size==v['bytes'])
cn={r['page']:r['text'] for r in json.loads((manual/'original-cn-extract.json').read_text())}
check('original ASCII lane/full-accumulator formulas','Rz[31:16] = Saturate(neg(Rx[31:16]))' in cn[503] and 'Rz[15:0] = Saturate(neg(Rx[15:0]))' in cn[503] and 'Saturate(Rz[31:0] + Rx[31:16] X Ry[31:16] + Rx[15:0] X Ry[15:0])' in cn[575] and 'Saturate(Rz[31:0] + Rx[31:16] X Ry[15:0] + Rx[15:0] X Ry[31:16])' in cn[576])
stage=(Q/'stage-main.c').read_text();spectrum=[32767]*1024;spectrum[1]=spectrum[513]=0
for i in range(1,256):spectrum[1024-2*i]=spectrum[2*i];spectrum[1025-2*i]=-spectrum[2*i+1]
check('valid Hermitian fixture shape',spectrum[1]==spectrum[513]==0 and all(spectrum[1024-2*i]==spectrum[2*i] and spectrum[1025-2*i]==-spectrum[2*i+1] for i in range(1,256)))
check('localized split and opcode logs','FIXTURE 1\nsplit-inverse index=1 c=0 asm=1' in (Q/'stages/mem.log').read_text() and 'packed-neg=e0014000 scalar-neg=e0004000' in (Q/'pneg/mem.log').read_text())
for name in ['harness.c','stage-main.c','startup.S','harness.ld','pneg-main.c','pneg-probe.S','rename-symbols.txt','tables.h','numerical-summary.json']:
 inputs[name]=sha((Q/name).read_bytes())
res={'all_pass':all(x['pass'] for x in checks),'checks':checks,'input_hashes':inputs,'counting':{'helper_pass':230,'bitrev_pass':3,'FFT_pass':23,'FFT_fail':1,'FFT_unrun':32,'total_planned':289,'abs_oracle_separate':55},'limits':['Receipt/static review only, no replay or hardware execution','Successful helper comparisons check outer canaries, not an independent logical-length oracle','First numerical mismatch returns before outer-canary checks; failure-path guard state not logged','Stage arrays lack outer canaries','Actual abs55 uses5 lengths x11 rotations, not proposed9 lengths x6 patterns pluszero','Ramp/LCG full-range patterns differ from proposed plan; constant32767 failing vector is unchanged']}
(O/'DSP-EXECUTION-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'all_pass':res['all_pass'],'checks':len(checks),'counting':res['counting'],'failed':[x['label'] for x in checks if not x['pass']]},indent=2))
