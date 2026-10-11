#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static uint32_t found,ready,duration;static unsigned resets,calls;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==7);return found?0x880000:0;}
uint32_t opencfw_em9305_radio_record_ready_31ac08(uint32_t id){assert(id==7);return ready;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){resets++;return memset(p,v,n);}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){assert(a==3&&b==0&&c==0&&d==90&&e==4&&f==0&&g==2&&h==5);calls++;return duration;}
uint32_t opencfw_em9305_radio_access_raw_318878(void){return 0x12345678;}
uint32_t opencfw_em9305_radio_callback_32d7f4(uintptr_t p){(void)p;return 0;}
/* Native3093a0..309514: pool claim and reset are committed before later
 * busy/duration rejection. Callback32d7f4 remains a genuine provider address. */
uint32_t opencfw_em9305_command_apply_3093a0(uint32_t id,uintptr_t input)
{
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
 if(record==0u) return 66u;
 if(opencfw_em9305_radio_record_ready_31ac08(id)==0u){
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(configuration+13u),index;
  for(index=0u;index<count;++index){
   uintptr_t row=0x80517cu+index*12u;
   if(*(volatile uint8_t *)(row+8u)!=0u) continue;
   uintptr_t control=*(volatile uint32_t *)(row+4u);
   *(volatile uint8_t *)(row+8u)=1u;
   *(volatile uint8_t *)(row+10u)=(uint8_t)index;
   *(volatile uint8_t *)(row+9u)=(uint8_t)id;
   *(volatile uint32_t *)(record+2812u)=(uint32_t)control;
   (void)opencfw_em9305_memset((void *)control,0u,144u);
   uintptr_t buffer=*(volatile uint32_t *)row;
   control=*(volatile uint32_t *)(record+2812u);
   uint32_t spare=*(volatile uint32_t *)(uintptr_t)0x805ce4u;
   *(volatile uint32_t *)(record+1160u)=(uint32_t)buffer;
   *(volatile uint32_t *)control=spare;
   break;
  }
  if(index==count) return 7u;
 }
 uintptr_t buffer=*(volatile uint32_t *)(record+1160u);
 *(volatile uint32_t *)(buffer+3844u)=32767u;
 *(volatile uint32_t *)(buffer+3848u)=0u;
 (void)opencfw_em9305_memset((void *)(buffer+3852u),255u,64u);
 if(*(volatile uint8_t *)(record+369u)!=0u) return 12u;
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t maximum=*(volatile uint32_t *)(record+72u);
 uint32_t limit=*(volatile uint16_t *)(configuration+20u);
 uint32_t enabled=*(volatile uint8_t *)(record+804u);
 if(maximum>limit) limit=maximum;
 uint32_t timing=0u;
 if(enabled!=0u){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;
  if(callback!=0u) timing=((uint32_t (*)(void))callback)();
 }
 uint32_t value=*(volatile uint16_t *)(record+1144u);
 uint32_t channel=*(volatile uint8_t *)(record+63u);
 uint32_t duration=opencfw_em9305_radio_duration_312be4(channel,0u,timing,(uint16_t)limit,value,0u,2u,5u);
 uint32_t upper=*(volatile uint16_t *)(input+2u),scaled_upper;
 scaled_upper=upper*1250u;
 if(duration>scaled_upper) return 69u;
 if((*(volatile uint8_t *)(record+32u)&59u)!=0u) return 18u;
 uint32_t lower=*(volatile uint16_t *)input;
 uint32_t latency=*(volatile uint16_t *)(input+4u),scaled_lower;
 *(volatile uint32_t *)(record+712u)=scaled_upper;
 scaled_lower=lower*1250u;
 *(volatile uint8_t *)(record+718u)=1u;
 *(volatile uint16_t *)(record+716u)=(uint16_t)latency;
 *(volatile uint32_t *)(record+708u)=scaled_lower;
 uint32_t seed=opencfw_em9305_radio_access_raw_318878();
 uint32_t groups=*(volatile uint8_t *)(input+6u),unit=*(volatile uint8_t *)(input+7u);
 *(volatile uint32_t *)(record+784u)=seed;
 *(volatile uint32_t *)(record+2816u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_callback_32d7f4;
 *(volatile uint8_t *)(record+2809u)=1u;
 *(volatile uint8_t *)(record+788u)=(uint8_t)groups;
 *(volatile uint8_t *)(record+789u)=(uint8_t)unit;
 uint32_t offset=*(volatile uint16_t *)(input+8u),scaled_unit;
 scaled_unit=unit*1250u;
 uintptr_t control=*(volatile uint32_t *)(record+2812u);
 *(volatile uint16_t *)(record+796u)=(uint16_t)offset;
 uint32_t extra=*(volatile uint8_t *)(input+10u);
 *(volatile uint32_t *)(record+792u)=scaled_unit;
 *(volatile uint8_t *)(record+798u)=(uint8_t)extra;
 *(volatile uint16_t *)(control+76u)=15u;
 return 0u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);_Alignas(4) uint8_t input[12]={6,0,12,0,9,0,2,8,3,4,5,0};unsigned cases=0;
for(unsigned scenario=0;scenario<8;scenario++){
memset((void *)0x800000,0,0x100000);uintptr_t r=0x880000,config=0x870000,buffer=0x860000,control=0x850000;found=scenario!=0;ready=scenario!=1&&scenario!=2;duration=scenario==4?15001:15000;resets=calls=0;
*(uint32_t *)0x805cac=config;*(uint8_t *)(config+13)=scenario==1?0:2;*(uint16_t *)(config+20)=80;
*(uint32_t *)(r+72)=90;*(uint8_t *)(r+63)=3;*(uint16_t *)(r+1144)=4;*(uint32_t *)(r+1160)=buffer;*(uint32_t *)(r+2812)=control;
*(uint32_t *)(0x80517c+4)=control;*(uint32_t *)0x80517c=buffer;*(uint32_t *)0x805ce4=0x890000;
*(uint8_t *)(r+369)=scenario==3;*(uint8_t *)(r+32)=scenario==5?1:0;
unsigned expected=scenario==0?66:scenario==1?7:scenario==3?12:scenario==4?69:scenario==5?18:0;
assert(opencfw_em9305_command_apply_3093a0(7,(uintptr_t)input)==expected);
if(scenario<2){assert(resets==0&&calls==0);}else{assert(resets==(scenario==2?2:1));assert(*(uint32_t *)(buffer+3844)==32767&&*(uint32_t *)(buffer+3848)==0);for(unsigned n=0;n<64;n++)assert(*(uint8_t *)(buffer+3852+n)==255);assert(calls==(scenario==3?0:1));}
if(scenario==2){assert(*(uint8_t *)(0x80517c+8)==1&&*(uint8_t *)(0x80517c+9)==7);assert(*(uint32_t *)control==0x890000);}
if(expected==0){assert(*(uint32_t *)(r+712)==15000&&*(uint32_t *)(r+708)==7500);assert(*(uint16_t *)(r+716)==9&&*(uint8_t *)(r+718)==1);assert(*(uint32_t *)(r+784)==0x12345678&&*(uint32_t *)(r+792)==10000);assert(*(uint8_t *)(r+788)==2&&*(uint8_t *)(r+789)==8&&*(uint16_t *)(r+796)==1027&&*(uint8_t *)(r+798)==5&&*(uint16_t *)(control+76)==15);}
cases++;}
printf("PASS %u\n",cases);}
