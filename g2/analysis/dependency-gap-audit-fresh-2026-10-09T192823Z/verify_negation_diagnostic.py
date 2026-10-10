import pathlib,json,re,struct
O=pathlib.Path(__file__).resolve().parent
Q=pathlib.Path('g2/analysis/csky-inverse-split-negation-diagnostic-20261009T203251Z')
P=pathlib.Path('g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z')
ns={'__file__':str(O/'verify_dsp.py')};exec((O/'verify_dsp.py').read_text().split('\nr=json.loads')[0],ns)
sha=ns['sha'];sections=ns['sections'];checks=[]
def check(label,ok,**extra):checks.append({'label':label,'pass':bool(ok),**extra})
intervention=json.loads((Q/'source-intervention.json').read_text());src=pathlib.Path(intervention['original_source']).read_text();diag=(Q/'inverse_split_diagnostic.c').read_text()
check('original source identity',sha(src.encode())==intervention['original_source_sha256'])
check('diagnostic source identity',sha(diag.encode())==intervention['diagnostic_source_sha256'])
start=diag.index('/* ANALYSIS DIAGNOSTIC ONLY.');end=diag.index('void diagnostic_csky_split_rfft_q15(',start)
undo=diag[:start]+diag[end:]
undo=undo.replace('void diagnostic_csky_split_rfft_q15(','void csky_split_rfft_q15(').replace('void diagnostic_csky_split_rifft_q15(','void csky_split_rifft_q15(')
change=intervention['semantic_changes'][0];undo=undo.replace(change['diagnostic'],change['original'])
check('only helper/namespace/declared one semantic intervention',undo==src and diag.count(change['diagnostic'])==1)
helper=diag[start:end]
check('fixed-width helper safe sign decode and unsigned packing',all(x in helper for x in ['lo_bits < UINT32_C(0x8000)','hi_bits < UINT32_C(0x8000)','(int32_t)lo_bits - INT32_C(65536)','(int32_t)hi_bits - INT32_C(65536)','lo == -INT32_C(32768) ? INT32_C(32767) : -lo','hi == -INT32_C(32768) ? INT32_C(32767) : -hi','((uint32_t)lo & UINT32_C(0xffff))','((uint32_t)hi & UINT32_C(0xffff)) << 16']))
# Arithmetic formula review, not compilation or an instruction interpreter.
check('all65536 lane encodings agree with documented saturating negation',all(((32767 if v==32768 else -(v if v<32768 else v-65536))&65535)==((max(-32768,min(32767,-(v if v<32768 else v-65536))))&65535) for v in range(65536)))
harness=(Q/'diagnostic-harness.c').read_text();triples=[(pat,inv,real) for pat in range(14) for inv in range(2) for real in range(2) if pat*4+inv*2+real>=23]
check('exact33 vector selection and independent counter',len(triples)==33 and triples[0]==(5,1,1) and 'cases=256;goto diagnostic_fft;' in harness and 'if(pat*4+inv*2+real<23)continue;' in harness and 'number(cases-256)' in harness)
oldFFT=(P/'harness.c').read_text().split('for(pat=0;pat<14;pat++)',1)[1].split('text("PASS cases=',1)[0]
newFFT=harness.split('for(pat=0;pat<14;pat++)',1)[1].split('text("DIAGNOSTIC PASS cases=',1)[0].replace('if(pat*4+inv*2+real<23)continue;','')
check('unchanged vector data/call/comparison bodies',oldFFT==newFFT)
old=json.loads((P/'numerical-summary.json').read_text());new=json.loads((Q/'SUMMARY.json').read_text())
check('original failure retained and no mixed56-case claim',old['corpus_passes']==256 and old['corpus_failures']==1 and old['fft_cases_not_executed_after_stop']==32 and new['diagnostic_passes']==new['diagnostic_targeted_fft_cases']==33 and new['mac_documented_model_differences']==6)
build=json.loads((Q/'build-results.json').read_text());check('diagnostic build commands succeeded',all(r['returncode']==0 for r in build))
for r in json.loads((Q/'diagnostic-executions.json').read_text()):
 f=Q/r['label']/'mem.log';elf=Q/pathlib.Path(r['command'][r['command'].index('-kernel')+1]).name;b=elf.read_bytes();h=struct.unpack_from('<HHIIIIIHHHHHH',b,16);ph=[struct.unpack_from('<8I',b,h[4]+i*h[8]) for i in range(h[9])]
 check('diagnostic run receipt '+r['label'],f.read_text()==r['memlog'] and sha(b)==r['elf_sha256'] and r['returncode']==0 and '-cpu' in r['command'] and r['command'][r['command'].index('-cpu')+1]=='ck804ef' and '--network=none' in r['command'] and '--read-only' in r['command'],memlog_sha256=sha(f.read_bytes()),elf_sha256=sha(b))
 check('diagnostic ELF valid RAM placement '+elf.name,h[0]==2 and h[1]==252 and h[3]==0x10000 and all(0x10000<=x[2]<=x[2]+x[5]<=0x1000000 for x in ph if x[0]==1))
 if r['label']=='remaining-fft-diagnostic':check('reported33passes log','DIAGNOSTIC PASS cases=33' in f.read_text() and 'DIFF' not in f.read_text() and 'GUARD' not in f.read_text())
 else:check('stage rechecks same and all prefix reductions present',f.read_text().count('SAME')==23 and all('PREFIX '+str(n)+'\n' in f.read_text() for n in [512,256,128,64,32,16,8]))
check('same unchanged stock table fixture',(Q/'tables.h').read_bytes()==(P/'tables.h').read_bytes())
ex=json.loads((Q/'mac-corner-exclusion.json').read_text());header=(Q/'tables.h').read_text();values=list(map(int,re.search(r'\brealcoef\[\].*?=\{([^}]*)\}',header,re.S)[1].split(',')));raw=b''.join((v&65535).to_bytes(2,'little') for v in values);A=[];B=[]
for i in range(0,len(values),2):
 a=(values[i]&65535)|((values[i+1]&65535)<<16);lo=(32768-(a&65535))&65535;hi=(-(a>>16))&65535;sv=lo if lo<32768 else lo-65536;lo=min(abs(sv),32767);A.append(a);B.append(lo|(hi<<16))
check('table-bound exact256 pairs and corner exclusion',sha(raw)==ex['table_sha256'] and len(A)==ex['coefficient_pairs']==256 and [i for i,a in enumerate(A) if a==0x80008000]==ex['A_all_min_pair_indices']==[] and [i for i,b in enumerate(B) if b==0x80008000]==ex['derived_B_all_min_pair_indices']==[] and max(b&65535 for b in B)==ex['B_low_lane_range_max']==32767)
assembly=pathlib.Path('third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source.asm/TransformFunctions/csky_rfft_q15.S').read_text().splitlines()
for r in ex['source_mac_bindings']:
 actual=assembly[r['source_line']-1].split('//',1)[0].strip();normalize=lambda x:re.sub(r'\s+','',x)
 check('MAC coefficient source binding '+str(r['source_line']),normalize(actual)==normalize(r['instruction']))
mac=json.loads((Q/'mac-corner-execution.json').read_text());log=(Q/'mac-corner/mem.log').read_text();triples=[]
for z,m,a,x in re.findall(r'z=([0-9a-f]{8}) manual=([0-9a-f]{8}) mulaca=([0-9a-f]{8}) mulacax=([0-9a-f]{8})',log):
 zi=int(z,16);zi=zi if zi<0x80000000 else zi-0x100000000;expected=max(-2147483648,min(2147483647,zi+2*1073741824))&0xffffffff;triples.append((z,m,a,x))
 check('documented full-expression arithmetic '+z,int(m,16)==expected and a==x=='80000000' and int(a,16)!=expected)
check('six MAC observations are documented differences not passes',len(triples)*2==6 and log==mac['memlog'] and 'EXPECTED MODEL DISCREPANCY' in log and sha((Q/'mac-corner.elf').read_bytes())==mac['elf_sha256'])
# Verify only wrapper inverse references were renamed; text is unchanged.
oldwrap=pathlib.Path('g2/analysis/nationalchip-dsp-complete-c-alternative-20261009T200634Z/csky_rfft_q15.o').read_bytes();newwrap=(Q/'diagnostic-wrapper.o').read_bytes()
oldtexts={n:oldwrap[h[4]:h[4]+h[5]] for n,h in sections(oldwrap) if n.startswith('.text.')};newtexts={n:newwrap[h[4]:h[4]+h[5]] for n,h in sections(newwrap) if n.startswith('.text.')}
check('wrapper text preserved during symbol redirection',oldtexts==newtexts and b'diagnostic_csky_split_rifft_q15\0' in newwrap and b'csky_split_rfft_q15\0' in newwrap)
res={'all_pass':all(x['pass'] for x in checks),'checks':checks,'accounting':{'authentic_C_original_FFT_passes':23,'authentic_C_original_FFT_failures':1,'authentic_C_original_FFT_unrun':32,'separate_diagnostic_FFT_passes':33,'MAC_documented_model_discrepancies':6},'limits':'No replay, production change or canonical admission. Helper mathematical-formula check is not firmware execution. Coefficient exclusion concerns only one MAC intermediate-overflow corner at three selected real-split assembly sites.'}
(O/'DSP-NEGATION-DIAGNOSTIC-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'all_pass':res['all_pass'],'checks':len(checks),'failed':[x['label'] for x in checks if not x['pass']]},indent=2))
