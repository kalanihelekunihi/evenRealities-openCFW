#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned callbacks,expected;
static uint32_t callback(uintptr_t event,uintptr_t self){assert(self==(uintptr_t)callback&&*(uint16_t *)event==0&&*(uint8_t *)(event+2)==24&&*(uint8_t *)(event+3)==expected&&*(uint8_t *)(event+4)==expected);callbacks++;return 77;}
uint32_t opencfw_em9305_ll_stream_kind_valid_30e4dc(uint32_t kind)
{
 if(kind==0u || kind==2u || kind==255u) return 1u;
 if(kind==1u || kind==3u)
  return *(volatile uint8_t *)(uintptr_t)0x805a81u!=0u;
 return 0u;
}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b0cu;
 if(callback==0u) return 0u;
 return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(event,callback);
}
/* Native307b9c..307bdc: authenticated table3357b4 words8035dc/802a60/80389c. */
uint32_t opencfw_em9305_scan_available_307b9c(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805a81u!=0u)return 1u;
 static const uintptr_t states[3]={0x8035dcu,0x802a60u,0x80389cu};
 uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x803560u;
 for(uint32_t bit=0u;bit<3u;++bit){
  if((mask&(1u<<bit))!=0u){
   uint32_t kind=*(volatile uint8_t *)(states[bit]+13u);
   if(opencfw_em9305_ll_stream_kind_valid_30e4dc(kind)==0u)return 0u;
   mask=*(volatile uint8_t *)(uintptr_t)0x803560u;
  }
 }
 return 1u;
}
/* Native30e7f8..30e834: first nonzero error latch, byte countdown, event24. */
uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t status)
{
 uintptr_t root=0x805a70u;
 uint32_t latched=*(volatile uint8_t *)(root+14u);
 if(status!=0u&&latched==0u){latched=status;*(volatile uint8_t *)(root+14u)=(uint8_t)status;}
 uint32_t count=*(volatile uint8_t *)(root+13u);
 if(count==0u)return 0u;
 uint32_t remaining=count-1u;
 *(volatile uint8_t *)(root+13u)=(uint8_t)remaining;
 if((uint8_t)remaining!=0u)return remaining;
 _Alignas(4) uint8_t event[5];
 *(volatile uint8_t *)(event+4u)=(uint8_t)latched;
 *(volatile uint8_t *)(event+3u)=(uint8_t)latched;
 *(volatile uint8_t *)(event+2u)=24u;
 *(volatile uint16_t *)(void *)event=0u;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t cells[]={0x8035e9,0x802a6d,0x8038a9};unsigned cases=0;
for(unsigned cap=0;cap<2;cap++)for(unsigned pos=0;pos<3;pos++)for(unsigned kind=0;kind<256;kind++)for(unsigned mask=0;mask<256;mask++){*(uint8_t *)0x805a81=cap;*(uint8_t *)0x803560=mask;for(unsigned j=0;j<3;j++)*(uint8_t *)cells[j]=2;*(uint8_t *)cells[pos]=kind;unsigned valid=kind==0||kind==2||kind==255;unsigned expected_result=cap||!(mask&(1u<<pos))||valid;assert(opencfw_em9305_scan_available_307b9c()==expected_result);cases++;}
unsigned old_values[]={0,1,18,255};for(unsigned status=0;status<258;status++)for(unsigned old=0;old<4;old++)for(unsigned count=0;count<256;count++)for(unsigned present=0;present<2;present++){unsigned code=status<256?status:status==256?0x100:0xffffffff;*(uint8_t *)0x805a7e=old_values[old];*(uint8_t *)0x805a7d=count;*(uint32_t *)0x805b0c=present?(uintptr_t)callback:0;callbacks=0;expected=(old_values[old]?old_values[old]:code)&255;unsigned want=count==0?0:count==1?(present?77:0):count-1;assert(opencfw_em9305_scan_error_30e7f8(code)==want);assert(callbacks==(count==1&&present)&&*(uint8_t *)0x805a7e==expected&&*(uint8_t *)0x805a7d==(count?count-1:0));cases++;}
printf("PASS %u\n",cases);}
