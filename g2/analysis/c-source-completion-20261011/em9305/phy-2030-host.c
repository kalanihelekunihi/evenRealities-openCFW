#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned active,pending,allocation,sends;
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==1);return active;}
static uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t op){assert(id==1&&op==32);return pending;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==10);*(uint8_t *)0x805b18=73;return allocation?0x830000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==73&&p==0x830000);sends++;return 88;}
/* Authenticated PHY policy332f3c/332f80 and providers30d4e4/30dd04.
 * Feature checks precede protocol validation; disabled PHY fields zeroed. */
uint32_t opencfw_em9305_command_phy_capable_332f80(uint32_t first,uint32_t second)
{
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 if((flags&256u)==0u&&((first|second)&2u)!=0u)return 0u;
 if((flags&2048u)==0u&&((first|second)&4u)!=0u)return 0u;
 return 1u;
}
uint32_t opencfw_em9305_command_phy_validate_332f3c(uint32_t mode,uint32_t first,uint32_t second,uint32_t kind)
{
 if(kind>2u||(mode&~3u)!=0u||(first|second)>7u)return 17u;
 if(first!=second&&mode==0u&&(*(volatile uint32_t *)(uintptr_t)0x805a84u&128u)!=0u)return 17u;
 if(first==0u&&(mode&1u)==0u)return 18u;
 if((mode&2u)==0u&&second==0u)return 18u;
 return 0u;
}
uint32_t opencfw_em9305_command_30d4e4(uint32_t mode,uint32_t first,uint32_t second)
{
 if(opencfw_em9305_command_phy_capable_332f80(first,second)==0u)return 17u;
 uint32_t status=opencfw_em9305_command_phy_validate_332f3c(mode,first,second,0u);
 if(status!=0u)return status;
 if((mode&2u)!=0u)second=0u;
 if((mode&1u)!=0u)first=0u;
 *(volatile uint8_t *)(uintptr_t)0x805ac8u=(uint8_t)mode;
 *(volatile uint8_t *)(uintptr_t)0x805acau=(uint8_t)second;
 *(volatile uint8_t *)(uintptr_t)0x805ac9u=(uint8_t)first;
 return 0u;
}
uint32_t opencfw_em9305_command_30dd04(uint32_t id,uint32_t mode,uint32_t first,uint32_t second,uint32_t kind)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 if(opencfw_em9305_ll_slot_pending_307434(id,32u)!=0u)return 12u;
 if(opencfw_em9305_command_phy_capable_332f80(first,second)==0u)return 17u;
 uint32_t status=opencfw_em9305_command_phy_validate_332f3c(mode,first,second,kind);
 if(status!=0u)return status;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(10u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=0x2001u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 if((mode&2u)!=0u)second=0u;
 if((mode&1u)!=0u)first=0u;
 *(volatile uint16_t *)message=(uint16_t)id;
 *(volatile uint8_t *)(message+6u)=(uint8_t)second;
 *(volatile uint8_t *)(message+5u)=(uint8_t)first;
 *(volatile uint16_t *)(message+8u)=(uint16_t)kind;
 *(volatile uint8_t *)(message+4u)=(uint8_t)mode;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x805cac=0x820000;*(uint8_t *)0x820022=4;active=allocation=1;pending=0;unsigned cases=0;
for(unsigned flags=0;flags<4;flags++)for(unsigned feature=0;feature<2;feature++)for(unsigned mode=0;mode<8;mode++)for(unsigned first=0;first<16;first++)for(unsigned second=0;second<16;second++)for(unsigned kind=0;kind<4;kind++){*(uint32_t *)0x805a94=(flags&1?256:0)|(flags&2?2048:0);*(uint32_t *)0x805a84=feature?128:0;unsigned capable=(!((first|second)&2)||(flags&1))&&(!((first|second)&4)||(flags&2));unsigned policy=kind>2||mode>3||(first|second)>7||(first!=second&&mode==0&&feature)?17:(!first&&!(mode&1))||(!second&&!(mode&2))?18:0;assert(opencfw_em9305_command_phy_capable_332f80(first,second)==capable&&opencfw_em9305_command_phy_validate_332f3c(mode,first,second,kind)==policy);sends=0;unsigned expected=capable?policy:17;assert(opencfw_em9305_command_30dd04(1,mode,first,second,kind)==expected&&sends==(expected==0));if(!expected){assert(*(uint16_t *)0x830000==1&&*(uint16_t *)0x830002==0x2001&&*(uint8_t *)0x830004==mode&&*(uint8_t *)0x830005==((mode&1)?0:first)&&*(uint8_t *)0x830006==((mode&2)?0:second)&&*(uint16_t *)0x830008==kind);}if(kind==0){*(uint8_t *)0x805ac8=99;unsigned result=opencfw_em9305_command_30d4e4(mode,first,second);assert(result==expected);if(!result)assert(*(uint8_t *)0x805ac8==mode&&*(uint8_t *)0x805ac9==((mode&1)?0:first)&&*(uint8_t *)0x805aca==((mode&2)?0:second));else assert(*(uint8_t *)0x805ac8==99);}cases++;}
*(uint32_t *)0x805a94=2304;*(uint32_t *)0x805a84=0;
for(unsigned count=0;count<3;count++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned wait=0;wait<2;wait++)for(unsigned alloc=0;alloc<2;alloc++){*(uint8_t *)0x820022=count;active=enabled;pending=wait;allocation=alloc;sends=0;unsigned expected=count<=1||!enabled?2:wait?12:0;assert(opencfw_em9305_command_30dd04(1,0,1,1,0)==expected&&sends==(expected==0&&alloc));cases++;}
printf("PASS %u\n",cases);}
