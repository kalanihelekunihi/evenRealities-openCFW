#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static unsigned command,calls,responses;
static uint32_t check(unsigned c){assert(command==c);calls++;return 0x12345678;}
uint32_t opencfw_em9305_command_30dbd4(uint32_t a,uint32_t b){assert(a==0x4321&&b==0x65);return check(0x2059);}
uint32_t opencfw_em9305_command_30c5e0(uint32_t a,uint32_t b,uint32_t c){assert(a==0x4321&&b==0x8765&&c==0xcba9);return check(0x205a);}
uint32_t opencfw_em9305_command_30c5c0(uint32_t a,uint32_t b,uint32_t c){assert(a==0x4321&&b==0x8765&&c==0xa9);return check(0x205b);}
uint32_t opencfw_em9305_command_30dc70(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){assert(a==0x4321&&b==0x65&&c==0xa987&&d==0xedcb&&e==0xff);return check(0x205c);}
uint32_t opencfw_em9305_command_30d48c(uint32_t a,uint32_t b,uint32_t c,uint32_t d){assert(a==0x21&&b==0x6543&&c==0xa987&&d==0xcb);return check(0x205d);}
uint32_t opencfw_em9305_ll_connection_response_32f34c(uintptr_t r,uint32_t s,uint32_t l,uintptr_t p,uint32_t id){assert(*(uint16_t *)r==command&&s==0x12345678&&p==0&&l==((command>=0x205a&&command<=0x205c)?3:1)&&id==((command>=0x205a&&command<=0x205c)?0x4321:0));responses++;return 999;}
/* Authenticated command dispatch330fa0..331074. Five commands decode
 * fixed byte fields before invoking distinct native command providers. */
extern uint32_t opencfw_em9305_command_30dbd4(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30c5e0(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30c5c0(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30dc70(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30d48c(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_dispatch_330fa0(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t index=command-0x2059u;
 if(index>=5u)return 0u;
 uint32_t b1=*(volatile uint8_t *)(input+1u),status,id=0u,length=1u;
 if(index==0u){
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_command_30dbd4((uint16_t)(b0+(b1<<8u)),b2);
 }else if(index==1u){
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  id=(uint16_t)(b0+(b1<<8u));
  status=opencfw_em9305_command_30c5e0(id,(uint16_t)(b2+(b3<<8u)),(uint16_t)(b4+(b5<<8u)));
  length=3u;
 }else if(index==2u){
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  id=(uint16_t)(b0+(b1<<8u));
  status=opencfw_em9305_command_30c5c0(id,(uint16_t)(b2+(b3<<8u)),b4);
  length=3u;
 }else if(index==3u){
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b6=*(volatile uint8_t *)(input+6u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  uint32_t b7=*(volatile uint8_t *)(input+7u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  id=(uint16_t)(b0+(b1<<8u));
  status=opencfw_em9305_command_30dc70(id,b2,(uint16_t)(b3+(b4<<8u)),(uint16_t)(b5+(b6<<8u)),b7);
  length=3u;
 }else{
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  uint32_t b0=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30d48c(b0,(uint16_t)(b1+(b2<<8u)),(uint16_t)(b3+(b4<<8u)),b5);
 }
 (void)opencfw_em9305_ll_connection_response_32f34c(request,status,length,0u,id);
 return 1u;
}

int main(void){unsigned cases=0;uint8_t input[8]={0x21,0x43,0x65,0x87,0xa9,0xcb,0xed,0xff};for(command=0x2059;command<=0x205d;command++){uint16_t request=command;calls=responses=0;assert(opencfw_em9305_dispatch_330fa0((uintptr_t)&request,(uintptr_t)input)==1&&calls==1&&responses==1);cases++;}for(unsigned c=0;c<65536;c++){if(c>=0x2059&&c<=0x205d)continue;uint16_t request=c;calls=responses=0;assert(opencfw_em9305_dispatch_330fa0((uintptr_t)&request,0)==0&&calls==0&&responses==0);cases++;}printf("PASS %u\n",cases);}
