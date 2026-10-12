#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc,trace;
static uint32_t opencfw_em9305_ll_command_pending_310634(void){assert(trace==0);trace=1;*(uint8_t *)0x805ec5=1;return 0x805ec5;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
static uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t n){assert(n==257&&trace==1);trace=2;return alloc?0x840000:0;}
void opencfw_em9305_command_callback_332d2c(void){}
void opencfw_em9305_command_callback_332cd0(void){}
uint32_t opencfw_em9305_common_request_30455c(uint32_t n){assert(n==2&&trace==2);trace=3;return 99;}
uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(p==0x8058f4&&trace==3);trace=4;return 98;}
/* Native command30cba0..30cce8 and channel mapping332c30..332c50.
 * Callback bodies and scheduler contracts remain genuine symbolic imports. */
extern void opencfw_em9305_command_callback_332d2c(void);
extern void opencfw_em9305_command_callback_332cd0(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
uint32_t opencfw_em9305_command_channel_332c30(uint32_t channel)
{
 uint32_t value;
 if(channel==0u)value=37u;
 else if(channel<12u)value=channel-1u;
 else if(channel==12u)value=38u;
 else if(channel>=39u)value=39u;
 else value=channel-2u;
 return (uint8_t)value;
}
uint32_t opencfw_em9305_command_count_30e4bc(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a79u;
 *(volatile uint8_t *)(uintptr_t)0x805a79u=(uint8_t)(count+1u);
 return 0x805a79u;
}
uint32_t opencfw_em9305_command_30cba0(uintptr_t input)
{
 uintptr_t flags=0x805a70u,state=0x8058dcu,record=0x8059f8u;
 if(*(volatile uint8_t *)(flags+4u)!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+3u)!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+2u)!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+1u)!=0u)return 12u;
 if(*(volatile uint8_t *)state!=0u)return 12u;
 if(*(volatile uint8_t *)flags!=0u)return 12u;
 if(*(volatile uint8_t *)(input+8u)>39u)return 48u;
 uint32_t kind=*(volatile uint8_t *)(input+9u);
 if(kind-1u>2u)return 48u;
 if(*(volatile uint8_t *)(input+10u)>1u)return 48u;
 if(kind==3u){if((*(volatile uint8_t *)(uintptr_t)0x805a95u&8u)==0u)return 17u;}
 else if(kind==2u){if((*(volatile uint8_t *)(uintptr_t)0x805a95u&1u)==0u)return 17u;}
 if(*(volatile uint8_t *)(input+11u)!=0u)return 17u;
 (void)opencfw_em9305_ll_command_pending_310634();
 (void)opencfw_em9305_memset((void *)(state+24u),0u,44u);
 (void)opencfw_em9305_memset((void *)record,0u,100u);
 *(volatile uint32_t *)(state+68u)=(uint32_t)record;
 uint32_t id=*(volatile uint16_t *)input;
 *(volatile uint8_t *)(state+50u)=2u;
 uint32_t channel=*(volatile uint8_t *)(input+8u);
 *(volatile uint32_t *)(state+52u)=(uint32_t)(uintptr_t)&opencfw_em9305_command_callback_332d2c;
 *(volatile uint16_t *)(state+2u)=(uint16_t)id;
 *(volatile uint8_t *)record=1u;
 uint32_t mapped=opencfw_em9305_command_channel_332c30(channel);
 kind=*(volatile uint8_t *)(input+9u);
 uint32_t value=*(volatile uint32_t *)(input+4u);
 *(volatile uint8_t *)(record+1u)=(uint8_t)mapped;
 *(volatile uint32_t *)(record+8u)=0x555555u;
 *(volatile uint32_t *)(record+4u)=value;
 uint32_t mode=0u;
 if(kind==3u){mode=3u;*(volatile uint8_t *)(record+13u)=3u;}
 else if(kind==2u){mode=2u;*(volatile uint8_t *)(record+13u)=2u;}
 else if(kind==1u){mode=1u;*(volatile uint8_t *)(record+13u)=1u;}
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint8_t *)(record+12u)=(uint8_t)mode;
 uint32_t duration=*(volatile uint16_t *)(config+60u);
 *(volatile uint16_t *)(record+112u)=257u;
 *(volatile uint32_t *)(record+104u)=(uint32_t)(uintptr_t)&opencfw_em9305_command_callback_332cd0;
 uint32_t scaled;
 scaled=duration*1000u;
 *(volatile uint32_t *)(record+100u)=scaled;
 uintptr_t allocation=opencfw_em9305_wsf_pool_allocate(257u);
 *(volatile uint32_t *)(record+108u)=(uint32_t)allocation;
 if(allocation==0u)return 31u;
 *(volatile uint8_t *)(flags+8u)=1u;
 *(volatile uint8_t *)state=2u; /* STB.AB uses old state address. */
 (void)opencfw_em9305_command_count_30e4bc();
 (void)opencfw_em9305_memset((void *)(state+4u),0u,20u);
 (void)opencfw_em9305_common_request_30455c(2u);
 (void)opencfw_em9305_auxiliary_insert_313220(state+24u);
 return 0u;
}

static uint8_t in[24];
static void setup(void){memset((void *)0x8058dc,0xa5,512);*(uint8_t *)0x8058dc=0;memset((void *)0x805a70,0,16);memset(in,0,sizeof in);*(uint16_t *)in=0x1234;*(uint32_t *)(in+4)=0x71764129;in[9]=1;*(uint8_t *)0x805a95=9;*(uint32_t *)0x805cac=0x820000;*(uint16_t *)0x82003c=65000;trace=0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned n=0;
for(unsigned channel=0;channel<256;channel++)for(unsigned kind=0;kind<5;kind++)for(unsigned mode=0;mode<3;mode++)for(unsigned features=0;features<4;features++)for(alloc=0;alloc<2;alloc++){setup();in[8]=channel;in[9]=kind;in[10]=mode;*(uint8_t *)0x805a95=(features&1?1:0)|(features&2?8:0);unsigned bad=channel>39||kind<1||kind>3||mode>1;unsigned unsupported=(kind==2&&!(features&1))||(kind==3&&!(features&2));unsigned expected=bad?48:unsupported?17:alloc?0:31;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==expected);assert(trace==(bad||unsupported?0:alloc?4:2));if(!bad&&!unsupported){unsigned mapped=channel==0?37:channel<12?channel-1:channel==12?38:channel>=39?39:channel-2;assert(*(uint8_t *)0x8059f8==1&&*(uint8_t *)0x8059f9==mapped&&*(uint32_t *)0x805a00==0x555555&&*(uint32_t *)0x8059fc==0x71764129&&*(uint8_t *)0x805a04==kind&&*(uint8_t *)0x805a05==kind);assert(*(uint16_t *)0x8058de==0x1234&&*(uint8_t *)0x80590e==2&&*(uint32_t *)0x805920==0x8059f8);assert(*(uint32_t *)0x805a5c==65000000&&*(uint16_t *)0x805a68==257&&*(uint32_t *)0x805a64==(alloc?0x840000:0));assert(*(uint8_t *)0x8058dc==(alloc?2:0)&&*(uint8_t *)0x805a78==alloc&&*(uint8_t *)0x805a79==alloc);for(unsigned j=24;j<68;j++)assert(*(uint8_t *)(uintptr_t)(0x8058dc+j)==(j==50?2:(j>=52&&j<56)?(uint8_t)((uintptr_t)&opencfw_em9305_command_callback_332d2c>>(8*(j-52))):0));}n++;}
for(unsigned guard=0;guard<6;guard++){setup();alloc=1;*(uint8_t *)(uintptr_t)(guard==5?0x8058dc:0x805a70+guard)=1;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==12&&trace==0);n++;}
setup();in[11]=1;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==17&&trace==0);n++;
printf("PASS %u\n",n);}
