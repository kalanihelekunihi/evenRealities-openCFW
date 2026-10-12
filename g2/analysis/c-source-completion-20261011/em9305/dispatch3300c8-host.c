#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned called,events,sends,fail,status,allocated,mutate;static uint32_t length;
static uintptr_t req=0x810000;
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t v){if(r!=req||v!=status)__builtin_trap();++events;return 0;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t command){if(command!=*(uint16_t*)req)__builtin_trap();++allocated;length=n;if(mutate)*(uint16_t*)req=0;return fail?0:0x812005;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=0x812000)__builtin_trap();++sends;return 0;}
uint32_t opencfw_em9305_command_config_clear_30ca18(uint32_t n){if(n!=*(uint8_t*)0x811000)__builtin_trap();called=3;return status;}
uint32_t opencfw_em9305_command_config_pairs_30b3f8(uint32_t n,uintptr_t p){if(n!=*(uint8_t*)0x811000||*(uint32_t*)p!=(uint32_t)(p+56)||*(uint32_t*)(p+4)!=(uint32_t)(p+28))__builtin_trap();called=4;return status;}
static uint32_t config(uintptr_t p,uintptr_t o,unsigned kind){
 if(o!=0x8018d8)__builtin_trap();
 called=kind;
 if(*(uint32_t*)(p+4)!=0x040302||*(uint32_t*)(p+8)!=0x070605||*(uint8_t*)p!=1)__builtin_trap();
 uintptr_t rows=(p&~(uintptr_t)0xffffffffu)|*(uint32_t*)(p+(kind==1?24:20));
 unsigned count=*(uint8_t*)0x805bf4,limit=count<2?count:2;
 for(unsigned i=0;i<limit;++i){uintptr_t row=rows+i*(kind==1?10:14),src=0x81100f+i*(kind==1?9:14);
  if(kind==1){if(*(uint8_t*)row!=*(uint8_t*)src||*(uint16_t*)(row+2)!=*(uint16_t*)(src+1)||*(uint16_t*)(row+4)!=*(uint16_t*)(src+3)||memcmp((void*)(row+6),(void*)(src+5),4))__builtin_trap();}
  else if(memcmp((void*)row,(void*)src,14))__builtin_trap();
 }
 return status;
}
uint32_t opencfw_em9305_command_config_basic_30d00c(uintptr_t p,uintptr_t o){return config(p,o,1);}
uint32_t opencfw_em9305_command_config_extended_30d204(uintptr_t p,uintptr_t o){return config(p,o,2);}
extern uint32_t opencfw_em9305_command_config_basic_30d00c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_config_extended_30d204(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_config_clear_30ca18(uint32_t);
extern uint32_t opencfw_em9305_command_config_pairs_30b3f8(uint32_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_stride(uint32_t n,uint32_t w){return n*w;}
/* Native3300c8..330400: full four-opcode configuration and response graph. */
uint32_t opencfw_em9305_dispatch_3300c8(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status,length;
 _Alignas(4) uint8_t scratch[60];
 if(command==0x2062u||command==0x2063u){
  uint8_t fields[15];
  static const uint8_t basic_order[15]={5,2,14,13,11,4,6,1,3,12,10,0,7,8,9};
  static const uint8_t extended_order[15]={5,2,14,10,4,6,1,3,9,0,7,8,11,12,13};
  const uint8_t *order=command==0x2062u?basic_order:extended_order;
  for(uint32_t i=0u;i<15u;++i)fields[order[i]]=*(volatile uint8_t *)(input+order[i]);
  uint32_t count=fields[14],limit=count<2u?count:2u;
  *(volatile uint8_t *)(uintptr_t)0x8018d4u=fields[0];
  *(volatile uint8_t *)(uintptr_t)0x805bf4u=(uint8_t)count;
  uintptr_t rows=(uintptr_t)scratch+(command==0x2062u?28u:0u);
  uint32_t width=command==0x2062u?10u:14u;
  uint32_t in_width=command==0x2062u?9u:14u;
  for(uint32_t i=0u;i<limit;++i){
   uintptr_t row=rows+opencfw_em9305_config_stride(i,width),src=input+15u+i*in_width;
   uint8_t v[14];
   if(command==0x2062u){static const uint8_t idx[9]={2,4,1,3,0,5,6,7,8};for(uint32_t n=0u;n<9u;++n)v[idx[n]]=*(volatile uint8_t *)(src+idx[n]);
    *(volatile uint8_t *)row=v[0];
    for(uint32_t n=6u;n<=9u;++n)*(volatile uint8_t *)(row+n)=v[n-1u];
    *(volatile uint16_t *)(row+2u)=(uint16_t)(v[1]|((uint32_t)v[2]<<8u));
    *(volatile uint16_t *)(row+4u)=(uint16_t)(v[3]|((uint32_t)v[4]<<8u));
   }else{static const uint8_t idx[14]={3,5,7,9,0,2,4,6,8,1,10,11,12,13};for(uint32_t n=0u;n<14u;++n)v[idx[n]]=*(volatile uint8_t *)(src+idx[n]);
    *(volatile uint8_t *)row=v[0];*(volatile uint8_t *)(row+1u)=v[1];
    for(uint32_t n=10u;n<14u;++n)*(volatile uint8_t *)(row+n)=v[n];
    for(uint32_t n=2u;n<=8u;n+=2u)*(volatile uint16_t *)(row+n)=(uint16_t)(v[n]|((uint32_t)v[n+1u]<<8u));
   }
  }
  uintptr_t config=(uintptr_t)scratch+(command==0x2062u?0u:28u);
  *(volatile uint32_t *)(config+(command==0x2062u?24u:20u))=(uint32_t)rows;
  if(command==0x2062u){
   *(volatile uint8_t *)(config+20u)=fields[14];
   *(volatile uint16_t *)(config+18u)=(uint16_t)(fields[12]|((uint32_t)fields[13]<<8u));
   *(volatile uint16_t *)(config+16u)=(uint16_t)(fields[10]|((uint32_t)fields[11]<<8u));
   *(volatile uint8_t *)(config+14u)=fields[9];*(volatile uint8_t *)(config+13u)=fields[8];*(volatile uint8_t *)(config+12u)=fields[7];
  }else{
   *(volatile uint8_t *)(config+19u)=fields[14];*(volatile uint8_t *)(config+18u)=fields[13];*(volatile uint8_t *)(config+17u)=fields[12];*(volatile uint8_t *)(config+16u)=fields[11];
   *(volatile uint16_t *)(config+14u)=(uint16_t)(fields[9]|((uint32_t)fields[10]<<8u));
   *(volatile uint8_t *)(config+13u)=fields[8];*(volatile uint8_t *)(config+12u)=fields[7];
  }
  *(volatile uint32_t *)(config+8u)=fields[4]|((uint32_t)fields[5]<<8u)|((uint32_t)fields[6]<<16u);
  *(volatile uint32_t *)(config+4u)=fields[1]|((uint32_t)fields[2]<<8u)|((uint32_t)fields[3]<<16u);
  *(volatile uint8_t *)config=fields[0];
  status=command==0x2062u?opencfw_em9305_command_config_basic_30d00c(config,0x8018d8u):opencfw_em9305_command_config_extended_30d204(config,0x8018d8u);
  uint32_t live_count=*(volatile uint8_t *)(uintptr_t)0x805bf4u;
  uint32_t doubled=live_count*2u;
  if((uint8_t)doubled==252u){(void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;}
  length=(uint8_t)(doubled+3u);
 }else if(command==0x2065u){
  uint32_t first=*(volatile uint8_t *)input;
  *(volatile uint8_t *)(uintptr_t)0x8018d4u=(uint8_t)first;
  status=opencfw_em9305_command_config_clear_30ca18(first);length=2u;
 }else if(command==0x2064u){
  uint32_t count=*(volatile uint8_t *)input,limit=count<2u?count:2u;
  *(volatile uint8_t *)(uintptr_t)0x805bf4u=(uint8_t)count;
  for(uint32_t i=0u;i<limit;++i){uintptr_t src=input+1u+i*4u;
   uint32_t a=*(volatile uint8_t *)src,b=*(volatile uint8_t *)(src+1u),c=*(volatile uint8_t *)(src+2u),d=*(volatile uint8_t *)(src+3u);
   *(volatile uint16_t *)(scratch+56u+i*2u)=(uint16_t)(a|(b<<8u));
   *(volatile uint16_t *)(scratch+28u+i*2u)=(uint16_t)(c|(d<<8u));
  }
  *(volatile uint32_t *)(scratch+4u)=(uint32_t)(uintptr_t)(scratch+28u);
  *(volatile uint32_t *)scratch=(uint32_t)(uintptr_t)(scratch+56u);
  status=opencfw_em9305_command_config_pairs_30b3f8(count,(uintptr_t)scratch);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;
 }else return 0u;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(!response)return 1u;
 command=*(volatile uint16_t *)request;
 if(command-0x2062u<2u){
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805bf4u;
  *(volatile uint8_t *)response=(uint8_t)status;
  uint32_t first=*(volatile uint8_t *)(uintptr_t)0x8018d4u;
  if(status!=0u)count=0u;
  *(volatile uint8_t *)(response+2u)=(uint8_t)count;
  *(volatile uint8_t *)(response+1u)=(uint8_t)first;
  for(uint32_t i=0u;i<count;++i){uint32_t value=*(volatile uint16_t *)(uintptr_t)(0x8018d8u+i*2u);
   *(volatile uint8_t *)(response+3u+i*2u)=(uint8_t)value;*(volatile uint8_t *)(response+4u+i*2u)=(uint8_t)(value>>8u);}
 }else if(command==0x2065u){*(volatile uint8_t *)response=(uint8_t)status;*(volatile uint8_t *)(response+1u)=*(volatile uint8_t *)(uintptr_t)0x8018d4u;}
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}

int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
 for(unsigned cmd=0;cmd<65536;++cmd)for(fail=0;fail<2;++fail){
  called=events=sends=allocated=mutate=0;status=0;memset((void*)0x812000,0xa5,600);for(unsigned i=0;i<60;++i)*(uint8_t*)(uintptr_t)(0x811000+i)=i+1;*(uint8_t*)0x81100e=2;*(uint16_t*)req=cmd;
  unsigned result=opencfw_em9305_dispatch_3300c8(req,0x811000),known=cmd>=0x2062&&cmd<=0x2065;
  if(result!=known||called!=(known?cmd==0x2062?1:cmd==0x2063?2:cmd==0x2064?4:3:0)||events!=(cmd==0x2064)||sends!=(known&&cmd!=0x2064&&!fail))return 3;
  ++cases;
 }
 for(unsigned c=0;c<256;++c)for(status=0;status<2;++status)for(mutate=0;mutate<2;++mutate){
  called=events=sends=allocated=0;fail=0;memset((void*)0x812000,0xa5,600);for(unsigned i=0;i<60;++i)*(uint8_t*)(uintptr_t)(0x811000+i)=i+1;*(uint8_t*)0x81100e=c;*(uint16_t*)req=0x2062;
  if(opencfw_em9305_dispatch_3300c8(req,0x811000)!=1)return 4;
  if((uint8_t)(c*2)==252){if(events!=1||allocated)return 5;}
  else{if(length!=(uint8_t)(c*2+3)||sends!=1)return 6;if(mutate){for(unsigned i=0;i<510;++i)if(*(uint8_t*)(uintptr_t)(0x812005+i)!=0xa5)return 7;}else if(*(uint8_t*)0x812005!=status||*(uint8_t*)0x812006!=1||*(uint8_t*)0x812007!=(status?0:c))return 8;}
  ++cases;
 }
 printf("PASS %u\n",cases);return 0;}
