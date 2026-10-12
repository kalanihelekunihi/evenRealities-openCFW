#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t Q,I,O;static unsigned cmd,allocfail,mutation,fail,sends,allocs,params,data,scan,enable,vendor,versions,powers;static uint32_t size_seen,opcode_seen;
static void *opencfw_em9305_memcpy(void*d,const void*s,uint32_t n){return memcpy(d,s,n);}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t size,uint32_t op){allocs++;size_seen=size;opcode_seen=op;if(mutation)*(uint16_t*)Q=mutation==1?0x2007:mutation==2?0x2008:0xfffb;return allocfail?0:O;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=O-5)fail++;sends++;return 19;}
extern uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t);
extern void opencfw_em9305_command_product_version_303258(uintptr_t);
extern uint32_t opencfw_em9305_command_advertising_parameters_30ce18(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_advertising_data_30cdd8(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_scan_response_30df98(uint32_t,uintptr_t);
extern void opencfw_em9305_command_advertising_enable_30aff8(uint32_t);
extern uint32_t opencfw_em9305_command_advertising_power_30bb50(uintptr_t);
/* Native331f00..331f5c: vendor-byte status and 32-byte version command. */
uint32_t opencfw_em9305_dispatch_331f00(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0xfffbu&&command!=0xfff5u)return 0u;
 uint32_t size=33u,opcode=0xfffbu;
 if(command==0xfff5u){(void)opencfw_em9305_command_vendor_byte_30cee4((int8_t)*(volatile uint8_t *)input);size=1u;opcode=*(volatile uint16_t *)request;}
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,opcode);
 if(response==0u)return 1u;
 *(volatile uint8_t *)response=0u;
 uintptr_t cursor=response+1u;
 if(*(volatile uint16_t *)request==0xfffbu){uint8_t version[32] __attribute__((aligned(4)));opencfw_em9305_command_product_version_303258((uintptr_t)version);(void)opencfw_em9305_memcpy((void *)cursor,version,32u);}
 (void)opencfw_em9305_ll_event_send(cursor-6u);
 return 1u;
}
/* Native331dc0..331ec0: full five-command dispatcher and vendor prefix. */
uint32_t opencfw_em9305_dispatch_331dc0(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_331f00(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2006u>=5u)return 0u;
 uint32_t status=0u,size=1u;
 if(command==0x2006u){
  uint32_t h0=*(volatile uint8_t *)(input+3u),h1=*(volatile uint8_t *)(input+1u),l0=*(volatile uint8_t *)(input+2u),l1=*(volatile uint8_t *)input;
  uint32_t type=*(volatile uint8_t *)(input+4u),own=*(volatile uint8_t *)(input+5u),peer=*(volatile uint8_t *)(input+6u);
  uint8_t address[6];(void)opencfw_em9305_memcpy(address,(const void *)(input+7u),6u);
  uint32_t channels=*(volatile uint8_t *)(input+13u),filter=*(volatile uint8_t *)(input+14u);
  status=opencfw_em9305_command_advertising_parameters_30ce18((uint16_t)((h1<<8)+l1),(uint16_t)((h0<<8)+l0),type,own,peer,(uintptr_t)address,channels,filter);
 }else if(command==0x2007u)size=2u;
 else if(command==0x2008u)status=opencfw_em9305_command_advertising_data_30cdd8(*(volatile uint8_t *)input,input+1u);
 else if(command==0x2009u)status=opencfw_em9305_command_scan_response_30df98(*(volatile uint8_t *)input,input+1u);
 else {opencfw_em9305_command_advertising_enable_30aff8(*(volatile uint8_t *)input);return 1u;}
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 command=*(volatile uint16_t *)request;
 if(command-0x2008u<2u||command==0x2006u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(command==0x2007u){uint8_t power=0u;uint32_t result=opencfw_em9305_command_advertising_power_30bb50((uintptr_t)&power);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=power;}
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}

uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t b){if(b!=-91)fail++;vendor++;return 9;}
void opencfw_em9305_command_product_version_303258(uintptr_t p){versions++;for(unsigned j=0;j<32;j++)*(uint8_t*)(p+j)=j+7;}
uint32_t opencfw_em9305_command_advertising_parameters_30ce18(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uintptr_t addr,uint32_t g,uint32_t h){if(a!=((uint32_t)*(uint8_t*)I+((uint32_t)*(uint8_t*)(I+1)<<8))||b!=((uint32_t)*(uint8_t*)(I+2)+((uint32_t)*(uint8_t*)(I+3)<<8))||c!=*(uint8_t*)(I+4)||d!=*(uint8_t*)(I+5)||e!=*(uint8_t*)(I+6)||memcmp((void*)addr,(void*)(I+7),6)||g!=*(uint8_t*)(I+13)||h!=*(uint8_t*)(I+14))fail++;params++;return 0x106;}
uint32_t opencfw_em9305_command_advertising_data_30cdd8(uint32_t n,uintptr_t p){if(n!=165||p!=I+1)fail++;data++;return 0x108;}
uint32_t opencfw_em9305_command_scan_response_30df98(uint32_t n,uintptr_t p){if(n!=165||p!=I+1)fail++;scan++;return 0x109;}
void opencfw_em9305_command_advertising_enable_30aff8(uint32_t v){if(v!=165)fail++;enable++;}
uint32_t opencfw_em9305_command_advertising_power_30bb50(uintptr_t p){if(*(uint8_t*)p)fail++;*(uint8_t*)p=0x85;powers++;return 0x187;}
int main(void){if(mmap((void*)0x20000000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x20000000)return 2;Q=0x20000000;I=Q+64;O=Q+128;for(unsigned j=0;j<32;j++)*(uint8_t*)(I+j)=165+j;unsigned cases=0;
 for(cmd=0;cmd<65536;cmd++)for(allocfail=0;allocfail<2;allocfail++)for(mutation=0;mutation<4;mutation++){
  *(uint16_t*)Q=cmd;memset((void*)O,0xa5,64);sends=allocs=params=data=scan=enable=vendor=versions=powers=0;
  unsigned prefix=cmd==0xfff5||cmd==0xfffb,normal=cmd>=0x2006&&cmd<=0x200a,respond=prefix||(normal&&cmd!=0x200a);unsigned handled=prefix||normal;
  uint32_t r=opencfw_em9305_dispatch_331dc0(Q,I);unsigned fresh=mutation==1?0x2007:mutation==2?0x2008:mutation==3?0xfffb:cmd;
  if(r!=handled||allocs!=respond||sends!=(respond&&!allocfail)||params!=(cmd==0x2006)||data!=(cmd==0x2008)||scan!=(cmd==0x2009)||enable!=(cmd==0x200a)||vendor!=(cmd==0xfff5))fail++;
  uint8_t expected[64];memset(expected,0xa5,64);unsigned ev=0,ep=0;
  if(respond){unsigned size=cmd==0xfffb?33:cmd==0x2007?2:1;if(size_seen!=size||opcode_seen!=cmd)fail++;
   if(!allocfail){if(prefix){expected[0]=0;if(fresh==0xfffb){ev=1;for(unsigned j=0;j<32;j++)expected[j+1]=j+7;}}
    else if(fresh==0x2006||fresh==0x2008||fresh==0x2009)expected[0]=cmd==0x2006?6:cmd==0x2008?8:cmd==0x2009?9:0;
    else if(fresh==0x2007){expected[0]=0x87;expected[1]=0x85;ep=1;}
   }
  }
  if(memcmp(expected,(void*)O,64)||versions!=ev||powers!=ep)fail++;cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
