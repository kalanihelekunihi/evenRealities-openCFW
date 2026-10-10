from pathlib import Path
import json,datetime
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis'/('csky-inverse-split-discriminator-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));d.mkdir();Path('/tmp/opencfw-split-discriminator-path').write_text(str(d));old=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';plan=r/'g2/analysis/dependency-gap-audit-fresh-2026-10-09T192823Z/NEXT-INVERSE-SPLIT-DISCRIMINATOR.json';j=json.loads(plan.read_text());(d/'plan.json').write_text(json.dumps(j,indent=2)+'\n')
for n in ['tables.h','harness.ld']:(d/n).write_bytes((old/n).read_bytes())
vals=','.join(str(x['amplitude']) for x in j['cases']);reals=','.join(str(x['first_real_expected']) for x in j['cases']);imags=','.join(str(x['packed_first_imaginary_expected']) for x in j['cases']);accs=','.join(x['packed_plus_next_product_accumulator_expected_hex']+'u' for x in j['cases'])
(d/'mac-difference-probe.S').write_text('''.section .text.probe_mulacsx,"ax",@progbits
.global probe_mulacsx
probe_mulacsx:
 mulacsx.s16.s r2,r0,r1
 mov r0,r2
 rts
''')
(d/'discriminator.c').write_text('''#include "csky_math.h"
#include "tables.h"
extern void csky_split_rifft_q15(q15_t*,uint32_t,q15_t*,q15_t*,uint32_t);
extern void diagnostic_csky_split_rifft_q15(q15_t*,uint32_t,q15_t*,q15_t*,uint32_t);
extern void asm_csky_split_rifft_q15(q15_t*,uint32_t,q15_t*,q15_t*,uint32_t);
extern uint32_t probe_pneg(uint32_t),probe_mulcax(uint32_t,uint32_t),probe_mulacsx(uint32_t,uint32_t,uint32_t);
struct guarded {uint32_t before[4];q15_t x[1024];uint32_t after[4];};
static struct guarded src,orig,model,stock;
static void text(const char*s){while(*s)*(volatile uint32_t*)0x10003000=(unsigned char)*s++;}
static void number(int32_t n){char q[12];uint32_t v,i=0;if(n<0){text("-");v=(uint32_t)(-n);}else v=n;do{q[i++]='0'+v%10;v/=10;}while(v);while(i)*(volatile uint32_t*)0x10003000=q[--i];}
static void hex(uint32_t x){int i;for(i=28;i>=0;i-=4)*(volatile uint32_t*)0x10003000="0123456789abcdef"[(x>>i)&15];}
static void init(struct guarded*p){unsigned i;for(i=0;i<4;i++){p->before[i]=0x12345678+i;p->after[i]=0x87654321+i;}for(i=0;i<1024;i++)p->x[i]=0x5a5a;}
static unsigned verify(q15_t amp,struct guarded*p){unsigned i,mask=0;struct guarded*all[]={&src,&orig,&model,&stock};for(i=0;i<4;i++){unsigned k;for(k=0;k<4;k++)if(all[i]->before[k]!=0x12345678+k||all[i]->after[k]!=0x87654321+k)mask|=1;}
for(i=0;i<1024;i++)if(src.x[i]!=((i==0||i==512)?amp:0))mask|=2;
for(i=512;i<1024;i++)if(p->x[i]!=0x5a5a)mask|=4;
return mask;}
int main(void){const q15_t amps[]={AMPS};const q15_t expected_real[]={REALS},expected_imag[]={IMAGS};const uint32_t expected_acc[]={ACCS};unsigned c,i,passes=0;
for(c=0;c<12;c++){uint32_t guard=0,product,neg,acc;unsigned predictions=0,diagnostic_mismatches=0,original_mismatches=0;init(&src);init(&orig);init(&model);init(&stock);for(i=0;i<1024;i++)src.x[i]=0;src.x[0]=src.x[512]=amps[c];
csky_split_rifft_q15(src.x,256,(q15_t*)realcoef,orig.x,1);guard|=verify(amps[c],&orig);
diagnostic_csky_split_rifft_q15(src.x,256,(q15_t*)realcoef,model.x,1);guard|=verify(amps[c],&model);
asm_csky_split_rifft_q15(src.x,256,(q15_t*)realcoef,stock.x,1);guard|=verify(amps[c],&stock);
/* All independent memory checks complete before any output mismatch branch. */
product=probe_mulcax((uint16_t)amps[c],0x40004000);neg=probe_pneg(product);acc=probe_mulacsx(0xc0004000,(uint16_t)amps[c],neg);
for(i=0;i<512;i++){q15_t original_want=i==0?expected_real[c]:0; q15_t packed_want=i==0?expected_real[c]:i==1?expected_imag[c]:0;if(orig.x[i]!=original_want||model.x[i]!=packed_want||stock.x[i]!=packed_want)predictions++;if(model.x[i]!=stock.x[i])diagnostic_mismatches++;if(orig.x[i]!=stock.x[i])original_mismatches++;}
if(acc!=expected_acc[c])predictions++;
text("case=");number(c);text(" amplitude=");number(amps[c]);text(" guard_mask=");number(guard);text(" real_C/model/asm=");number(orig.x[0]);text("/");number(model.x[0]);text("/");number(stock.x[0]);text(" imag_C/model/asm=");number(orig.x[1]);text("/");number(model.x[1]);text("/");number(stock.x[1]);text(" product=");hex(product);text(" packed_neg=");hex(neg);text(" accumulator=");hex(acc);text(" predictions_failed=");number(predictions);text(" diagnostic_differences=");number(diagnostic_mismatches);text(" original_differences=");number(original_mismatches);text("\\n");
if(guard){text("STOP memory verification failure\\n");return 7;}if(predictions||diagnostic_mismatches){text("STOP numerical prediction failure\\n");return 8;}passes++;}
text("PASS discriminator_cases=");number(passes);text("\\n");return 0;}
'''.replace('AMPS',vals).replace('REALS',reals).replace('IMAGS',imags).replace('ACCS',accs));print(d)
