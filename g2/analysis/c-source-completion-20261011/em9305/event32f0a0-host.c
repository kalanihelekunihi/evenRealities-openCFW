#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocations,sends,fail,allocated_type,allocated_size;
static uint8_t output[40];
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t t,uint32_t n){allocations++;allocated_type=t;allocated_size=n;return fail?0:(uintptr_t)(output+2);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output);sends++;return 91;}
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t bytes)
{
 uintptr_t out=(uintptr_t)destination,in=(uintptr_t)source;
 if (((out^in)&3u)==0u) {
  uint32_t align=(4u-(uint32_t)(out&3u))&3u;
  while (align!=0u) {
   if (bytes==0u) return destination;
   uint8_t value=*(volatile const uint8_t *)in;
   *(volatile uint8_t *)out=value;
   in+=1u;out+=1u;bytes-=1u;align-=1u;
  }
  while (bytes>=4u) {
   uint32_t value=*(volatile const uint32_t *)in;
   *(volatile uint32_t *)out=value;
   in+=4u;out+=4u;bytes-=4u;
  }
 }
 while (bytes!=0u) {
  uint8_t value=*(volatile const uint8_t *)in;
  *(volatile uint8_t *)out=value;
  in+=1u;out+=1u;bytes-=1u;
 }
 return destination;
}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t output,uintptr_t input)
{ return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)input,6u); }
/* Native event32f0a0..32f34c: full product-gated packet projection. */
uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uintptr_t base=0x8056e8u;
 uint32_t gate,mask,event_type=62u,size,subtype=0u,le=0u;
 switch(type){
 case 5u:gate=16u;mask=1u;size=19u;subtype=1u;le=1u;break;
 case 6u:gate=0u;mask=16u;size=4u;event_type=5u;break;
 case 7u:gate=16u;mask=4u;size=10u;subtype=3u;le=1u;break;
 case 9u:gate=1u;mask=8u;size=8u;event_type=12u;break;
 case 10u:gate=16u;mask=8u;size=12u;subtype=4u;le=1u;break;
 case 16u:gate=16u;mask=32u;size=11u;subtype=6u;le=1u;break;
 case 18u:gate=16u;mask=64u;size=11u;subtype=7u;break;
 case 46u:gate=19u;mask=64u;size=5u;subtype=31u;le=1u;break;
 case 47u:gate=20u;mask=1u;size=9u;subtype=33u;le=1u;break;
 case 48u:gate=19u;mask=128u;size=5u;subtype=32u;le=1u;break;
 default:return 0u;
 }
 if((*(volatile uint8_t *)(base+gate)&mask)==0u)return 0u;
 if(le!=0u&&(*(volatile uint8_t *)(base+7u)&32u)==0u)return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(event_type,size);
 if(event==0u)return 0u;
 if(subtype!=0u)*(volatile uint8_t *)event=(uint8_t)subtype;
 switch(type){
 case 5u:{
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  uint32_t kind=*(volatile uint8_t *)(packet+9u);
  uintptr_t address;
  if((kind&~1u)==2u){*(volatile uint8_t *)(event+5u)=1u;address=packet+29u;}
  else{*(volatile uint8_t *)(event+5u)=(uint8_t)kind;address=packet+10u;}
  (void)opencfw_em9305_radio_address_copy_304604(event+6u,address);
  for(uint32_t i=0u;i<7u;++i)*(volatile uint8_t *)(event+12u+i)=*(volatile uint8_t *)(packet+16u+i);
  break;
 }
 case 6u:
  *(volatile uint8_t *)event=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 7u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<8u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 9u:
  *(volatile uint8_t *)event=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+6u+i);
  for(uint32_t i=0u;i<4u;++i)*(volatile uint8_t *)(event+4u+i)=*(volatile uint8_t *)(packet+10u+i);
  break;
 case 10u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<2u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  (void)opencfw_em9305_memcpy((void *)(event+4u),(const void *)(packet+8u),8u);
  break;
 case 16u:case 18u:
  for(uint32_t i=0u;i<10u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+4u+i);
  break;
 case 46u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<3u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 47u:
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  for(uint32_t i=0u;i<7u;++i)*(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
  break;
 case 48u:
  for(uint32_t i=0u;i<4u;++i)*(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+4u+i);
  break;
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

struct row{unsigned type,off,mask,event,size,sub,le;};
static const struct row rows[]={{5,16,1,62,19,1,1},{6,0,16,5,4,0,0},{7,16,4,62,10,3,1},{9,1,8,12,8,0,0},{10,16,8,62,12,4,1},{16,16,32,62,11,6,1},{18,16,64,62,11,7,0},{46,19,64,62,5,31,1},{47,20,1,62,9,33,1},{48,19,128,62,5,32,1}};
static void expected(uint8_t *e,const uint8_t *p,unsigned t){
 switch(t){
 case 5:e[1]=p[4];memcpy(e+2,p+6,3);e[5]=(p[9]==2||p[9]==3)?1:p[9];memcpy(e+6,p+((p[9]==2||p[9]==3)?29:10),6);memcpy(e+12,p+16,7);break;
 case 6:e[0]=p[4];memcpy(e+1,p+6,3);break;
 case 7:e[1]=p[4];memcpy(e+2,p+6,8);break;
 case 9:e[0]=p[4];memcpy(e+1,p+6,3);memcpy(e+4,p+10,4);break;
 case 10:e[1]=p[4];memcpy(e+2,p+6,2);memcpy(e+4,p+8,8);break;
 case 16:case 18:memcpy(e+1,p+4,10);break;
 case 46:e[1]=p[4];memcpy(e+2,p+6,3);break;
 case 47:e[1]=p[4];memcpy(e+2,p+6,7);break;
 case 48:memcpy(e+1,p+4,4);break;
 }
}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned t=0;t<256;t++)for(unsigned gates=0;gates<4;gates++)for(fail=0;fail<2;fail++)for(unsigned kind=0;kind<256;kind++){
 uint8_t p[40],e[40];for(unsigned j=0;j<40;j++)p[j]=(uint8_t)(j*37+kind*11+t);p[2]=t;p[9]=kind;memset(output,0xa5,40);memset(e,0xa5,40);memset((void *)0x8056e8,0,24);allocations=sends=0;const struct row *r=0;for(unsigned j=0;j<10;j++)if(rows[j].type==t)r=rows+j;
 if(r){*(uint8_t *)(uintptr_t)(0x8056e8+r->off)=(gates&1)?r->mask:0;*(uint8_t *)0x8056ef=(gates&2)?32:0;}
 unsigned admitted=r&&(gates&1)&&(!r->le||(gates&2));unsigned ok=admitted&&!fail;uint32_t v=opencfw_em9305_dispatch_32f0a0((uintptr_t)p);assert(v==ok&&allocations==admitted&&sends==ok);
 if(admitted)assert(allocated_type==r->event&&allocated_size==r->size);
 if(ok){if(r->sub)e[2]=r->sub;expected(e+2,p,t);}assert(!memcmp(output,e,40));cases++;
}
printf("PASS %u\n",cases);}
