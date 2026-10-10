#include "csky_math.h"
#include "tables.h"
extern void asm_csky_split_rifft_q15(q15_t*,uint32_t,q15_t*,q15_t*,uint32_t);
extern void csky_split_rifft_q15(q15_t*,uint32_t,q15_t*,q15_t*,uint32_t);
extern void asm_csky_cfft_q15(const csky_cfft_instance_q15*,q15_t*,uint8_t,uint8_t);
static q15_t src[1024] __attribute__((aligned(4))), a[1024] __attribute__((aligned(4))), b[1024] __attribute__((aligned(4)));
static void text(const char*s){while(*s)*(volatile unsigned*)0x10003000=(unsigned char)*s++;}
static void num(unsigned n){char q[12];unsigned i=0;do{q[i++]='0'+n%10;n/=10;}while(n);while(i)*(volatile unsigned*)0x10003000=q[--i];}
static void diff(const char*name){unsigned i;for(i=0;i<512;i++)if(a[i]!=b[i]){text(name);text(" index=");num(i);text(" c=");num((unsigned short)a[i]);text(" asm=");num((unsigned short)b[i]);text("\n");return;}text(name);text(" SAME\n");}
int main(void){unsigned mode,i,n; csky_cfft_instance_q15 cf={256,(q15_t*)twiddle,(uint16_t*)bitrev,240};
for(mode=0;mode<3;mode++){for(i=0;i<1024;i++)src[i]=32767;if(mode==1){src[1]=src[513]=0;for(i=1;i<256;i++){src[1024-2*i]=src[2*i];src[1025-2*i]=-src[2*i+1];}}if(mode==2)for(i=2;i<1024;i++)src[i]=0;
text("FIXTURE ");num(mode);text("\n");
csky_split_rifft_q15(src,256,(q15_t*)realcoef,a,1);asm_csky_split_rifft_q15(src,256,(q15_t*)realcoef,b,1);diff("split-inverse");csky_cfft_q15(&cf,a,1,1);asm_csky_cfft_q15(&cf,b,1,1);diff("complex-inverse");for(i=0;i<512;i++){a[i]=a[i]<<1;b[i]=b[i]<<1;}diff("final-double");}
/* A bounded input reduction, keeping original fixed implementations/tables. */
for(n=512;n>=8;n/=2){for(i=0;i<1024;i++)src[i]=i<n?32767:0;text("PREFIX ");num(n);text("\n");csky_split_rifft_q15(src,256,(q15_t*)realcoef,a,1);asm_csky_split_rifft_q15(src,256,(q15_t*)realcoef,b,1);diff("split-inverse");csky_cfft_q15(&cf,a,1,1);asm_csky_cfft_q15(&cf,b,1,1);for(i=0;i<512;i++){a[i]=a[i]<<1;b[i]=b[i]<<1;}diff("final-double");}
return 0;}
