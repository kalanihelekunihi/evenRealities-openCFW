#include "csky_math.h"
#include "tables.h"
extern void csky_abs_max_q15(q15_t*,q15_t*,uint32_t);
extern void asm_csky_copy_q15(q15_t*,q15_t*,uint32_t);
extern void asm_csky_fill_q15(q15_t,q15_t*,uint32_t);
extern void asm_csky_shift_q15(q15_t*,int8_t,q15_t*,uint32_t);
extern void asm_csky_bitreversal_16(uint16_t*,uint16_t,const uint16_t*);
extern void asm_csky_cfft_q15(const csky_cfft_instance_q15*,q15_t*,uint8_t,uint8_t);
extern void asm_csky_rfft_q15(const csky_rfft_instance_q15*,q15_t*,q15_t*);
static void emit(char c){*(volatile unsigned*)0x10003000=(unsigned char)c;}
static void text(const char*s){while(*s)emit(*s++);}
static void number(unsigned n){char s[12];unsigned i=0;do{s[i++]='0'+n%10;n/=10;}while(n);while(i)emit(s[--i]);}
struct guarded {unsigned before; q15_t x[1024]; unsigned after;};
static struct guarded a,b,c,e;
static unsigned cases;
static const q15_t edges[]={-32768,-32767,-16385,-16384,-1,0,1,16383,16384,32766,32767};
static void reset(void){unsigned i;a.before=b.before=c.before=e.before=0x12345678;a.after=b.after=c.after=e.after=0x87654321;for(i=0;i<1024;i++){a.x[i]=b.x[i]=edges[i%11];c.x[i]=e.x[i]=0x5a5a;}}
static int compare(q15_t*x,q15_t*y,unsigned n,const char*family){unsigned i;for(i=0;i<n;i++)if(x[i]!=y[i]){text("DIFF ");text(family);text(" case=");number(cases);text(" index=");number(i);text(" c=");number((unsigned short)x[i]);text(" asm=");number((unsigned short)y[i]);text("\n");return 1;}if(a.before!=0x12345678||b.before!=0x12345678||c.before!=0x12345678||e.before!=0x12345678||a.after!=0x87654321||b.after!=0x87654321||c.after!=0x87654321||e.after!=0x87654321){text("GUARD\n");return 2;}cases++;return 0;}
int main(void){unsigned lens[]={0,1,2,3,4,5,7,8,17,512};int shifts[]={-15,-8,-1,0,1,8,15};q15_t fills[]={-32768,-32767,-1,0,1,32766,32767};unsigned l,s,in,i,pat,inv,real;int err;uint32_t state;
csky_cfft_instance_q15 cf={256,(q15_t*)twiddle,(uint16_t*)bitrev,240};csky_rfft_instance_q15 rf={512,0,1,1,(q15_t*)realcoef,&cf};
text("START ck804ef\n");
#ifdef ABS_ORACLE_ONLY
{unsigned ns[]={0,1,3,4,512},n,j,k;for(n=0;n<5;n++)for(j=0;j<11;j++){q15_t want=0;reset();for(k=0;k<1024;k++)a.x[k]=edges[(j+k)%11];for(k=0;k<ns[n];k++){int v=a.x[k];if(v<0)v=-v;if(v>32767)v=32767;if(v>want)want=v;}csky_abs_max_q15(a.x,c.x,ns[n]);if(c.x[0]!=want){text("ABS ORACLE DIFF\n");return 5;}for(k=1;k<1024;k++)if(c.x[k]!=0x5a5a){text("ABS GUARD DIFF\n");return 6;}cases++;}text("ABS ORACLE PASS cases=");number(cases);text("\n");return 0;}
#endif

/* Minimal actual-kernel smoke before the corpus; guarded copy exercises DSP loop/load/store. */
reset();csky_copy_q15(a.x,c.x,4);asm_csky_copy_q15(b.x,e.x,4);if((err=compare(c.x,e.x,1024,"smoke-copy")))return err;text("SMOKE copy-loop PASS\n");cases=0;
reset(); for(i=0;i<4;i++)a.x[i]=b.x[i]=i==0?-32768:i==1?-1:i==2?1:32767;
csky_shift_q15(a.x,1,c.x,4);asm_csky_shift_q15(b.x,1,e.x,4);if((err=compare(c.x,e.x,1024,"smoke-shift-left")))return err;
if(e.x[0]!=-32768||e.x[1]!=-2||e.x[2]!=2||e.x[3]!=32767){text("ISA shift-left expectation FAIL\n");return 3;}
csky_shift_q15(a.x,-1,c.x,4);asm_csky_shift_q15(b.x,-1,e.x,4);if((err=compare(c.x,e.x,1024,"smoke-shift-right")))return err;
if(e.x[0]!=-16384||e.x[1]!=-1||e.x[2]!=0||e.x[3]!=16383){text("ISA shift-right expectation FAIL\n");return 3;}
reset();csky_fill_q15(-32768,c.x,5);asm_csky_fill_q15(-32768,e.x,5);if((err=compare(c.x,e.x,1024,"smoke-fill")))return err;
for(inv=0;inv<2;inv++)for(real=0;real<2;real++){reset();for(i=0;i<1024;i++)a.x[i]=b.x[i]=0;if(real){rf.ifftFlagR=inv;csky_rfft_q15(&rf,a.x,c.x);asm_csky_rfft_q15(&rf,b.x,e.x);if((err=compare(c.x,e.x,1024,"smoke-rfft")))return err;}else{csky_cfft_q15(&cf,a.x,inv,1);asm_csky_cfft_q15(&cf,b.x,inv,1);if((err=compare(a.x,b.x,1024,"smoke-cfft")))return err;}}
text("SMOKE selected-DSP-kernels PASS\n");
#ifdef SMOKE_ONLY
return 0;
#endif
cases=0;
for(l=0;l<10;l++)for(s=0;s<7;s++)for(in=0;in<2;in++){reset();csky_shift_q15(a.x,shifts[s],in?a.x:c.x,lens[l]);asm_csky_shift_q15(b.x,shifts[s],in?b.x:e.x,lens[l]);if((err=compare(in?a.x:c.x,in?b.x:e.x,1024,"shift")))return err;}
for(l=0;l<10;l++)for(in=0;in<2;in++){reset();csky_copy_q15(a.x,in?a.x:c.x,lens[l]);asm_csky_copy_q15(b.x,in?b.x:e.x,lens[l]);if((err=compare(in?a.x:c.x,in?b.x:e.x,1024,"copy")))return err;}
for(l=0;l<10;l++)for(s=0;s<7;s++){reset();csky_fill_q15(fills[s],c.x,lens[l]);asm_csky_fill_q15(fills[s],e.x,lens[l]);if((err=compare(c.x,e.x,1024,"fill")))return err;}
text("HELPERS230 PASS\n");
for(pat=0;pat<3;pat++){reset();state=0x471512;for(i=0;i<512;i++){state=1664525*state+1013904223;a.x[i]=b.x[i]=pat==0?(q15_t)i:pat==1?(i%2?32767:-32768):(q15_t)(state>>16);}csky_bitreversal_16((uint16_t*)a.x,240,bitrev);asm_csky_bitreversal_16((uint16_t*)b.x,240,bitrev);if((err=compare(a.x,b.x,1024,"bitrev")))return err;}
for(pat=0;pat<14;pat++)for(inv=0;inv<2;inv++)for(real=0;real<2;real++){reset();state=0x471512;for(i=0;i<1024;i++){q15_t v=0;state=1664525*state+1013904223;if(pat==1&&i==0)v=1;if(pat==2&&i==0)v=-1;if(pat==3&&i==0)v=32767;if(pat==4&&i==0)v=-32768;if(pat==5)v=32767;if(pat==6)v=-32768;if(pat==7)v=i%2?32767:-32768;if(pat==8)v=i%4==0?16384:i%4==2?-16384:0;if(pat==9)v=i%4==0?32767:i%4==2?-32768:0;if(pat==10)v=i==0?1:i==511?-1:0;if(pat==11)v=(q15_t)(i*257);if(pat==12)v=(q15_t)(((state>>16)&4095)-2048);if(pat==13)v=(q15_t)(state>>16);a.x[i]=b.x[i]=v;}
if(real){rf.ifftFlagR=inv;csky_rfft_q15(&rf,a.x,c.x);asm_csky_rfft_q15(&rf,b.x,e.x);if((err=compare(c.x,e.x,1024,"rfft")))return err;}else{csky_cfft_q15(&cf,a.x,inv,1);asm_csky_cfft_q15(&cf,b.x,inv,1);if((err=compare(a.x,b.x,1024,"cfft")))return err;}}
text("PASS cases=");number(cases);text("\n");return 0;}
