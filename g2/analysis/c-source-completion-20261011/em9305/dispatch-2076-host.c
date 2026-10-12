#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[10],output[16];static unsigned alloc_ok,calls,query_calls;static uint32_t args[6],length;static uintptr_t query_input;
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){assert(cmd==request);length=n;return alloc_ok?(uintptr_t)output:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output-5);return 87;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&request&&status==99);calls++;return 5;}
/* Authenticated response33118c and command dispatch331074. The 0x2076
 * query retains input+2; native post-increment byte load reads input0. */
extern uint32_t opencfw_em9305_command_30c65c(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30da5c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30da2c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30e000(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_query_30bd34(uint32_t,uint32_t,uintptr_t,uintptr_t);
uint32_t opencfw_em9305_ll_response_33118c(uintptr_t request,uint32_t status,uint32_t length,uintptr_t input,uint32_t id)
{
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(response==0u)return 0u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2078u<3u){
  *(volatile uint8_t *)(response+1u)=(uint8_t)id;
  *(volatile uint8_t *)response=(uint8_t)status;
  *(volatile uint8_t *)(response+2u)=(uint8_t)(id>>8u);
 }else if(command==0x2076u){
  uint32_t kind=*(volatile uint8_t *)input;
  uint8_t first=0u,second=0u;
  uint32_t result=opencfw_em9305_command_query_30bd34(id,kind,(uintptr_t)&first,(uintptr_t)&second);
  uint32_t captured_first=*(volatile uint8_t *)&first;
  uint32_t captured_second=*(volatile uint8_t *)&second;
  *(volatile uint8_t *)(response+3u)=(uint8_t)kind;
  *(volatile uint8_t *)(response+1u)=(uint8_t)id;
  *(volatile uint8_t *)response=(uint8_t)result;
  *(volatile uint8_t *)(response+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(response+5u)=(uint8_t)captured_second;
  *(volatile uint8_t *)(response+4u)=(uint8_t)captured_first;
 }
 return opencfw_em9305_ll_event_send(response-5u);
}
uint32_t opencfw_em9305_dispatch_331074(uintptr_t request,uintptr_t input)
{
 uint32_t index=(uint32_t)*(volatile uint16_t *)request-0x2076u;
 if(index>=5u)return 0u;
 uint32_t b1=*(volatile uint8_t *)(input+1u);
 uint32_t b0=*(volatile uint8_t *)input;
 uint32_t id=(uint16_t)(b0+(b1<<8u));
 input+=2u;
 uint32_t status=0u,length=6u;
 if(index==1u){
  uint32_t value=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30c65c(id,0u,value);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 }else if(index==2u){
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t c1=*(volatile uint8_t *)(input+1u);
  uint32_t c0=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30da5c(id,c0,c1,b2,b3,(uint16_t)(b4+(b5<<8u)));
  length=3u;input=0u;
 }else if(index==3u){
  uint32_t value=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30da2c(id,value);
  length=3u;input=0u;
 }else if(index==4u){
  uint32_t second=*(volatile uint8_t *)(input+1u);
  uint32_t first=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30e000(id,first,second);
  length=3u;input=0u;
 }
 (void)opencfw_em9305_ll_response_33118c(request,status,length,input,id);
 return 1u;
}


uint32_t opencfw_em9305_command_30c65c(uint32_t a,uint32_t c,uint32_t d){assert(a==0x2211&&c==0&&d==0x33);calls++;return 99;}
uint32_t opencfw_em9305_command_30da5c(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){uint32_t v[]={a,c,d,e,f,g};memcpy(args,v,sizeof(v));calls++;return 98;}
uint32_t opencfw_em9305_command_30da2c(uint32_t a,uint32_t c){assert(a==0x2211&&c==0x33);calls++;return 97;}
uint32_t opencfw_em9305_command_30e000(uint32_t a,uint32_t c,uint32_t d){assert(a==0x2211&&c==0x33&&d==0x44);calls++;return 96;}
uint32_t opencfw_em9305_command_query_30bd34(uint32_t a,uint32_t c,uintptr_t f,uintptr_t s){assert(a==0x2211&&c==0x33&&*(uint8_t *)f==0&&*(uint8_t *)s==0);query_input=f;*(uint8_t *)f=0x55;*(uint8_t *)s=0x66;query_calls++;return 95;}
int main(void){unsigned cases=0;for(unsigned command=0;command<65536;command++){if(command>=0x2076&&command<=0x207a)continue;request=command;assert(opencfw_em9305_dispatch_331074((uintptr_t)&request,0)==0);cases++;}
for(unsigned allocation=0;allocation<2;allocation++)for(unsigned index=0;index<5;index++){request=0x2076+index;for(unsigned n=0;n<10;n++)input[n]=0x11*(n+1);memset(output,0xaa,sizeof(output));alloc_ok=allocation;calls=query_calls=length=0;assert(opencfw_em9305_dispatch_331074((uintptr_t)&request,(uintptr_t)input)==1);if(index==1){assert(calls==2&&query_calls==0&&length==0);}else{assert(calls==(index!=0)&&length==(index==0?6:3));assert(query_calls==(index==0&&allocation));if(allocation){assert(output[0]==(index==0?95:index==2?98:index==3?97:96)&&output[1]==0x11&&output[2]==0x22);if(index==0)assert(output[3]==0x33&&output[4]==0x55&&output[5]==0x66);}}if(index==2){uint32_t expected[]={0x2211,0x33,0x44,0x55,0x66,0x8877};assert(memcmp(args,expected,sizeof(args))==0);}cases++;}
assert(query_input);printf("PASS %u\n",cases);}
