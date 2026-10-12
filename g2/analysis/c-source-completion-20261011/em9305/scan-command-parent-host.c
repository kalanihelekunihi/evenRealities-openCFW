#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned fail,mutate,allocated,status,sends;static uintptr_t sent;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
void *opencfw_em9305_memset(void *d,uint32_t v,uint32_t n){return memset(d,v,n);}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t command){allocated++;assert(n==(command==0xfffc?41:1));if(fail)return 0;if(mutate)*(uint16_t *)0x810000=0x200c;return 0x820005;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){sent=p;sends++;return 0;}
uint32_t opencfw_em9305_command_30ccf8(uint32_t a,uint32_t b){assert(a==2&&b==3);status=12;return 99;}
uint32_t opencfw_em9305_command_30df08(uintptr_t p){assert(*(uint16_t *)p==0x0403&&*(uint16_t *)(p+2)==0x0605&&*(uint8_t *)(p+4)==2&&*(uint8_t *)(p+5)==7&&*(uint8_t *)(p+6)==8);status=77;return status;}
/* Authenticated command-dispatch parent330c60 and shared330e10 handler.
 * Stack records are semantic fields; lower commands remain genuine imports. */
extern uint32_t opencfw_em9305_command_30ccf8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30df08(uintptr_t);
uint32_t opencfw_em9305_command_30dfd8(uint32_t value)
{
 uint32_t second=*(volatile uint8_t *)(uintptr_t)0x805a74u;
 uint32_t first=*(volatile uint8_t *)(uintptr_t)0x805a73u;
 if((first|second)!=0u)return 12u;
 if(value-1u>=7u)return 18u;
 *(volatile uint8_t *)(uintptr_t)0x805b00u=(uint8_t)value;
 return 0u;
}
uintptr_t opencfw_em9305_ll_information_3032b4(uintptr_t output)
{ return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x801820u,40u); }
uint32_t opencfw_em9305_dispatch_shared_330e10(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t status,length;
 if(command==0xfffcu){status=0u;length=41u;}
 else if(command==0xffe0u){
  status=opencfw_em9305_command_30dfd8(*(volatile uint8_t *)input);
  command=*(volatile uint16_t *)request;length=1u;
 }else return 0u;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,command);
 if(response==0u)return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;
 uintptr_t cursor=response+1u;
 if(*(volatile uint16_t *)request==0xfffcu){
  uint8_t scratch[40] __attribute__((aligned(4)));
  (void)opencfw_em9305_memset(scratch,0u,40u);
  (void)opencfw_em9305_ll_information_3032b4((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)cursor,scratch,40u);
 }
 (void)opencfw_em9305_ll_event_send(cursor-6u);
 return 1u;
}
uint32_t opencfw_em9305_dispatch_330c60(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_shared_330e10(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0x200cu){
  uint32_t second=*(volatile uint8_t *)(input+1u);
  uint32_t first=*(volatile uint8_t *)input;
  (void)opencfw_em9305_command_30ccf8(first,second);
  return 1u;
 }
 if(command!=0x200bu)return 0u;
 uint32_t mode=*(volatile uint8_t *)input;
 uint32_t first=*(volatile uint8_t *)(input+5u);
 uint32_t second=*(volatile uint8_t *)(input+6u);
 uint32_t lo=*(volatile uint8_t *)(input+1u);
 uint32_t hi=*(volatile uint8_t *)(input+2u);
 uint32_t lower=*(volatile uint8_t *)(input+3u);
 uint32_t upper=*(volatile uint8_t *)(input+4u);
 uint8_t record[8] __attribute__((aligned(4)));
 *(uint16_t *)(record+2u)=(uint16_t)(lower+(upper<<8u));
 record[4]=(uint8_t)mode;record[5]=(uint8_t)first;record[6]=(uint8_t)second;
 *(uint16_t *)record=(uint16_t)(lo+(hi<<8u));
 uint32_t status=opencfw_em9305_command_30df08((uintptr_t)record);
 command=*(volatile uint16_t *)request;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(1u,command);
 if(response==0u)return 0u;
 if(*(volatile uint16_t *)request==0x200bu)*(volatile uint8_t *)response=(uint8_t)status;
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned commands[]={0x200b,0x200c,0xfffc,0xffe0,0x1234};for(unsigned ci=0;ci<5;ci++)for(fail=0;fail<2;fail++)for(mutate=0;mutate<2;mutate++){memset((void *)0x800000,0,0x100000);allocated=sends=status=sent=0;unsigned cmd=commands[ci];*(uint16_t *)0x810000=cmd;for(unsigned j=0;j<7;j++)*(uint8_t *)(uintptr_t)(0x811000+j)=j+2;for(unsigned j=0;j<40;j++)*(uint8_t *)(uintptr_t)(0x801820+j)=j+11;unsigned result=opencfw_em9305_dispatch_330c60(0x810000,0x811000);if(cmd==0x200b){assert(result==!fail&&allocated==1&&status==77&&sends==!fail);if(!fail){assert(sent==0x820000&&*(uint8_t *)0x820005==(mutate?0:77));}}else if(cmd==0x200c){assert(result==1&&allocated==0&&sends==0&&status==12);}else if(cmd==0xfffc||cmd==0xffe0){assert(result==1&&allocated==1&&sends==!fail);if(!fail){assert(sent==0x820000&&*(uint8_t *)0x820005==0);if(cmd==0xfffc&&!mutate)assert(memcmp((void *)0x820006,(void *)0x801820,40)==0);}}else assert(result==0&&allocated==0&&sends==0);cases++;}for(unsigned a=0;a<3;a++)for(unsigned b=0;b<3;b++)for(unsigned v=0;v<256;v++){*(uint8_t *)0x805a73=a;*(uint8_t *)0x805a74=b;*(uint8_t *)0x805b00=99;unsigned r=opencfw_em9305_command_30dfd8(v);assert(r==((a|b)?12:v>=1&&v<=7?0:18));assert(*(uint8_t *)0x805b00==(r==0?v:99));cases++;}printf("PASS %u\n",cases);}
