#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned phase,notify;static uint32_t expectedone,expectedtwo,expectedthree,expectedfour,expectedreason;
uint32_t opencfw_em9305_phy_start_324680(uintptr_t p){(void)p;if(phase!=1)abort();phase=2;return 33;}
uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t p){(void)p;if(phase!=2)abort();phase=3;return 77;}
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t p){if((*(uint32_t*)(p+636)&(1u<<21))==0)abort();phase=1;return 55;}
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t p){(void)p;phase=1;return 55;}
uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t p,uint32_t a,uint32_t c,uint32_t d,uint32_t e){(void)p;if(a!=expectedone||c!=expectedtwo||d!=expectedthree||e!=expectedfour)abort();phase=1;return 66;}
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;return 88;}
uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t p,uint32_t r){if(r!=expectedreason||*(uint32_t*)(p+640)!=0||(*(uint32_t*)(p+636)&(1u<<21)))abort();notify++;return 99;}
extern uint32_t opencfw_em9305_phy_start_324680(uintptr_t);
extern uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t);
extern uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t);
/* Native31592c..31593a, retains incoming record across both calls. */
uint32_t opencfw_em9305_phy_action_31592c(uintptr_t record)
{
 (void)opencfw_em9305_phy_start_324680(record);
 return opencfw_em9305_phy_schedule_318278(record);
}
/* Native315a0c..315a26. */
uint32_t opencfw_em9305_phy_action_315a0c(uintptr_t record)
{
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 *(volatile uint32_t *)(record+636u)=bits|(1u<<21u);
 (void)opencfw_em9305_phy_defer_32caa0(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315e60..315e6e. */
uint32_t opencfw_em9305_phy_action_315e60(uintptr_t record)
{
 (void)opencfw_em9305_phy_defer_32cb48(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315e84..315eaa: exact byte capture sequence before packet child. */
uint32_t opencfw_em9305_phy_action_315e84(uintptr_t record)
{
 uint32_t one=*(volatile uint8_t *)(record+720u);
 uint32_t four=*(volatile uint8_t *)(uintptr_t)0x80281du;
 uint32_t three=*(volatile uint8_t *)(uintptr_t)0x80281cu;
 uint32_t two=*(volatile uint8_t *)(record+721u);
 (void)opencfw_em9305_phy_update_packet_326764(record,one,two,three,four);
 return opencfw_em9305_phy_complete_32c818(record);
}
/* Native315f0c..315f46: incidental R0 flags retained on no-notify paths. */
uint32_t opencfw_em9305_phy_action_315f0c(uintptr_t record)
{
 (void)opencfw_em9305_phy_complete_32c818(record);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 if((bits&(1u<<21u))==0u)return bits;
 bits&=~(1u<<21u);
 uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
 *(volatile uint32_t *)(record+640u)=0u;
 *(volatile uint32_t *)(record+636u)=bits;
 uint32_t reason;
 if(operation==7u)reason=26u;
 else if(operation==17u||operation==13u)reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
 else return bits;
 return opencfw_em9305_phy_response_3232dc(record,reason);
}

int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];unsigned count=0;
 for(unsigned seed=0;seed<65536;seed++){
 memset(r,0,sizeof r);*(uint32_t*)(r+636)=seed;phase=1;if(opencfw_em9305_phy_action_31592c((uintptr_t)r)!=77||phase!=3)abort();
 phase=0;if(opencfw_em9305_phy_action_315a0c((uintptr_t)r)!=77||phase!=3||*(uint32_t*)(r+636)!=(seed|(1u<<21)))abort();
 phase=0;if(opencfw_em9305_phy_action_315e60((uintptr_t)r)!=77||phase!=3)abort();
 expectedone=(uint8_t)seed;expectedtwo=(uint8_t)(seed>>8);expectedthree=(uint8_t)(seed^0x55);expectedfour=(uint8_t)(seed+3);r[720]=expectedone;r[721]=expectedtwo;*(volatile uint8_t*)0x80281c=expectedthree;*(volatile uint8_t*)0x80281d=expectedfour;
 phase=0;if(opencfw_em9305_phy_action_315e84((uintptr_t)r)!=88||phase!=1)abort();
 count++;
 }
 for(unsigned operation=0;operation<256;operation++)for(unsigned seed=0;seed<256;seed++)for(unsigned bit=0;bit<2;bit++){
 memset(r,0,sizeof r);*(uint32_t*)(r+636)=seed|(bit<<21);*(uint32_t*)(r+640)=123;*(volatile uint8_t*)0x802818=operation;*(volatile uint8_t*)0x80281d=(uint8_t)seed;expectedreason=operation==7?26:seed;notify=0;
 unsigned should=bit&&(operation==7||operation==17||operation==13);uint32_t result=opencfw_em9305_phy_action_315f0c((uintptr_t)r);
 if(result!=(should?99:seed)||notify!=should||*(uint32_t*)(r+636)!=seed||*(uint32_t*)(r+640)!=(bit?0:123))abort();
 count++;
 }
 printf("PASS %u action cases\n",count);return 0;
}
