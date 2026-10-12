#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[10],output[10];static unsigned allocation,calls,queries,status_calls;static uint32_t length;
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){assert(cmd==request);length=n;return allocation?(uintptr_t)output:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output-5);return 99;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&request&&status==92);status_calls++;return 98;}
/* Authenticated dispatch3316e0..331814. Scratch padding untouched; fresh
 * request command after allocation governs response query/status layout. */
extern uint32_t opencfw_em9305_command_30d4e4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30dd04(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30cba0(uintptr_t);
extern uint32_t opencfw_em9305_command_30e120(uintptr_t);
extern uint32_t opencfw_em9305_command_query_30c824(uint32_t,uintptr_t,uintptr_t);
uint32_t opencfw_em9305_dispatch_3316e0(uintptr_t request,uintptr_t input)
{
 uint32_t index=(uint32_t)*(volatile uint16_t *)request-0x2030u;
 if(index>=5u)return 0u;
 _Alignas(4) uint8_t scratch[24];
 uint32_t status=0u,id=0u,length=1u;
 if(index==0u){
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b0=*(volatile uint8_t *)input;
  id=b0+(b1<<8u);length=5u;
 }else if(index==1u){
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b0=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30d4e4(b0,b1,b2);
 }else if(index==2u){
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b6=*(volatile uint8_t *)(input+6u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_command_30dd04((uint16_t)(b0+(b1<<8u)),b2,b3,b4,(uint16_t)(b5+(b6<<8u)));
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 }else if(index==3u){
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  *(volatile uint8_t *)(scratch+10u)=(uint8_t)b2;
  *(volatile uint16_t *)scratch=0u;
  *(volatile uint32_t *)(scratch+16u)=0u;
  *(volatile uint8_t *)(scratch+14u)=2u;
  *(volatile uint8_t *)(scratch+11u)=0u;
  *(volatile uint32_t *)(scratch+4u)=0x71764129u;
  *(volatile uint16_t *)(scratch+12u)=256u;
  *(volatile uint8_t *)(scratch+8u)=(uint8_t)b0;
  *(volatile uint8_t *)(scratch+9u)=(uint8_t)b1;
  status=opencfw_em9305_command_30cba0((uintptr_t)scratch);
 }else{
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  *(volatile uint8_t *)(scratch+5u)=(uint8_t)b3;
  *(volatile uint16_t *)scratch=0u;
  *(volatile uint32_t *)(scratch+12u)=0u;
  *(volatile uint8_t *)(scratch+8u)=2u;
  *(volatile uint16_t *)(scratch+6u)=0u;
  *(volatile uint8_t *)(scratch+16u)=127u;
  *(volatile uint8_t *)(scratch+2u)=(uint8_t)b0;
  *(volatile uint8_t *)(scratch+3u)=(uint8_t)b1;
  *(volatile uint8_t *)(scratch+4u)=(uint8_t)b2;
  status=opencfw_em9305_command_30e120((uintptr_t)scratch);
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2033u<2u||command==0x2031u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(command==0x2030u){
  *(volatile uint8_t *)scratch=0u;
  *(volatile uint8_t *)(scratch+23u)=0u;
  uint32_t result=opencfw_em9305_command_query_30c824((uint16_t)id,(uintptr_t)scratch,(uintptr_t)(scratch+23u));
  uint32_t first=*(volatile uint8_t *)scratch;
  uint32_t second=*(volatile uint8_t *)(scratch+23u);
  *(volatile uint8_t *)(response+1u)=(uint8_t)id;
  *(volatile uint8_t *)response=(uint8_t)result;
  *(volatile uint8_t *)(response+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(response+4u)=(uint8_t)second;
  *(volatile uint8_t *)(response+3u)=(uint8_t)first;
 }
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}

uint32_t opencfw_em9305_command_30d4e4(uint32_t a,uint32_t c,uint32_t d){assert(a==0x11&&c==0x22&&d==0x33);calls++;return 91;}
uint32_t opencfw_em9305_command_30dd04(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f){assert(a==0x2211&&c==0x33&&d==0x44&&e==0x55&&f==0x7766);calls++;return 92;}
uint32_t opencfw_em9305_command_30cba0(uintptr_t p){assert(*(uint16_t *)p==0&&*(uint32_t *)(p+16)==0&&*(uint8_t *)(p+14)==2&&*(uint8_t *)(p+11)==0&&*(uint32_t *)(p+4)==0x71764129&&*(uint16_t *)(p+12)==256&&*(uint8_t *)(p+8)==0x11&&*(uint8_t *)(p+9)==0x22&&*(uint8_t *)(p+10)==0x33);calls++;return 93;}
uint32_t opencfw_em9305_command_30e120(uintptr_t p){assert(*(uint16_t *)p==0&&*(uint32_t *)(p+12)==0&&*(uint8_t *)(p+8)==2&&*(uint16_t *)(p+6)==0&&*(uint8_t *)(p+16)==127&&*(uint8_t *)(p+2)==0x11&&*(uint8_t *)(p+3)==0x22&&*(uint8_t *)(p+4)==0x33&&*(uint8_t *)(p+5)==0x44);calls++;return 94;}
uint32_t opencfw_em9305_command_query_30c824(uint32_t id,uintptr_t a,uintptr_t c){assert(id==0x2211&&*(uint8_t *)a==0&&*(uint8_t *)c==0);*(uint8_t *)a=0x55;*(uint8_t *)c=0x66;queries++;return 90;}
int main(void){unsigned cases=0;for(unsigned command=0;command<65536;command++){if(command>=0x2030&&command<=0x2034)continue;request=command;assert(opencfw_em9305_dispatch_3316e0((uintptr_t)&request,0)==0);cases++;}
for(unsigned alloc=0;alloc<2;alloc++)for(unsigned index=0;index<5;index++){request=0x2030+index;for(unsigned n=0;n<10;n++)input[n]=0x11*(n+1);allocation=alloc;calls=queries=status_calls=length=0;memset(output,0xaa,sizeof(output));assert(opencfw_em9305_dispatch_3316e0((uintptr_t)&request,(uintptr_t)input)==1);assert(calls==(index!=0));if(index==2){assert(status_calls==1&&length==0&&queries==0);}else{assert(length==(index==0?5:1)&&queries==(index==0&&alloc));if(alloc){assert(output[0]==90+index);if(index==0)assert(output[1]==0x11&&output[2]==0x22&&output[3]==0x55&&output[4]==0x66);}}cases++;}
printf("PASS %u\n",cases);}
