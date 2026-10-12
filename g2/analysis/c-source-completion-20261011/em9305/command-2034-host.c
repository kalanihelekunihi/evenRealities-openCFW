#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc,allocs,patterns,requests,inserts,pending,bounds,clamps,enters,exits;
static uint32_t opencfw_em9305_ll_command_pending_310634(void){pending++;return 0;}
static uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t l,uintptr_t u){bounds++;*(uint8_t *)l=156;*(uint8_t *)u=10;return 10;}
static uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t n){clamps++;return n+1;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 0;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 0;}
static uint32_t opencfw_em9305_command_channel_332c30(uint32_t n){return n? n<12?n-1:n==12?38:n>=39?39:n-2:37;}
static uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t n){assert(n==257);allocs++;return alloc?0x840000:0;}
static uint32_t opencfw_em9305_command_count_30e4bc(void){return ++*(uint8_t *)0x805a79;}
static uint32_t opencfw_em9305_common_request_30455c(uint32_t n){assert(n==2||n==3);requests++;return 99;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t n){assert(n==0x8058f4);inserts++;return 99;}
uint32_t opencfw_em9305_command_duration_332be4(uint32_t a,uint32_t b,uint32_t c){assert(a==19);return a+10*b+1000*c;}
uint32_t opencfw_em9305_command_pattern_332b94(uint32_t a,uint32_t b,uintptr_t p){assert(a==19&&b<8&&p==0x840000);patterns++;return 98;}
void opencfw_em9305_command_callback_332e2c(void){}
void opencfw_em9305_command_callback_332db4(void){}
/* Native command30e120..30e350: complete guards/update/allocate paths.
 * Native332be4 does not write R3, preserving allocator request257. Its DSP
 * accumulator result remains a genuine import until decoded and verified. */
extern uint32_t opencfw_em9305_command_duration_332be4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_pattern_332b94(uint32_t,uint32_t,uintptr_t);
extern void opencfw_em9305_command_callback_332e2c(void);
extern void opencfw_em9305_command_callback_332db4(void);
uint32_t opencfw_em9305_command_30e120(uintptr_t input)
{
 uintptr_t state=0x8058dcu,flags=0x805a70u,policy=0x805994u;
 uint32_t original=*(volatile uint8_t *)state;
 if(original>=2u)return 12u;
 if(*(volatile uint8_t *)(flags+4u)!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+3u)!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+2u)!=0u)return 12u;
 if(*(volatile uint8_t *)flags!=0u)return 12u;
 if(*(volatile uint8_t *)(flags+1u)!=0u)return 12u;
 if(original==1u){
  uint32_t requested=*(volatile uint8_t *)(input+4u);
  uint32_t existing=*(volatile uint8_t *)(policy+1u);
  if((requested==3u)!=(existing==3u))return 12u;
 }
 if(*(volatile uint8_t *)(input+2u)>=40u)return 48u;
 if(*(volatile uint8_t *)(input+4u)>=8u)return 48u;
 uint32_t mode=*(volatile uint8_t *)(input+5u);
 if(mode-1u>=4u)return 48u;
 if(mode-3u<2u){if((*(volatile uint8_t *)(uintptr_t)0x805a95u&8u)==0u)return 17u;}
 else if(mode==2u){if((*(volatile uint8_t *)(uintptr_t)0x805a95u&1u)==0u)return 17u;}
 if(*(volatile uint8_t *)(input+6u)!=0u)return 17u;
 (void)opencfw_em9305_ll_command_pending_310634();
 uint8_t lower,upper;
 (void)opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&lower,(uintptr_t)&upper);
 int32_t power=(int8_t)*(volatile uint8_t *)(input+16u);
 uint32_t adjusted;
 if(power==126)adjusted=lower;
 else if(power==127)adjusted=upper;
 else {
  if((uint32_t)(power-21)<(uint32_t)-147)return 48u;
  if((int8_t)upper<power)return 17u;
  if(power<(int8_t)lower)return 17u;
  adjusted=opencfw_em9305_ll_signed_clamp_310230((uint32_t)power);
 }
 *(volatile uint8_t *)(input+16u)=(uint8_t)adjusted;
 if(*(volatile uint8_t *)state==0u)
  (void)opencfw_em9305_memset((void *)(state+4u),0u,20u);
 if(*(volatile uint8_t *)(input+4u)==3u){
  *(volatile uint8_t *)(state+185u)=3u;
  *(volatile uint8_t *)state=1u;
  (void)opencfw_em9305_common_request_30455c(3u);
  *(volatile uint8_t *)(flags+8u)=1u;
  (void)opencfw_em9305_command_count_30e4bc();
  return 0u;
 }
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t pattern=*(volatile uint8_t *)(input+3u);
 uint32_t kind=*(volatile uint8_t *)(input+4u);
 uint32_t channel=*(volatile uint8_t *)(input+2u);
 *(volatile uint8_t *)policy=(uint8_t)pattern;
 *(volatile uint8_t *)(policy+1u)=(uint8_t)kind;
 uint32_t mapped=opencfw_em9305_command_channel_332c30(channel);
 mode=*(volatile uint8_t *)(input+5u);
 *(volatile uint8_t *)(policy+2u)=(uint8_t)mapped;
 if(mode==4u){*(volatile uint16_t *)(policy+4u)=1u;*(volatile uint8_t *)(policy+3u)=3u;}
 else if(mode==2u){*(volatile uint16_t *)(policy+4u)=0u;*(volatile uint8_t *)(policy+3u)=2u;}
 else if(mode==3u){*(volatile uint16_t *)(policy+4u)=2u;*(volatile uint8_t *)(policy+3u)=3u;}
 else if(mode==1u){*(volatile uint16_t *)(policy+4u)=0u;*(volatile uint8_t *)(policy+3u)=1u;}
 uint32_t requested_power=*(volatile uint8_t *)(input+16u);
 *(volatile uint32_t *)(state+196u)=0xffffffffu;
 *(volatile uint32_t *)(state+200u)=0u;
 *(volatile uint8_t *)(state+204u)=(uint8_t)requested_power;
 (void)opencfw_em9305_wsf_critical_exit();
 uint32_t fresh=*(volatile uint8_t *)state;
 uintptr_t pending=state+24u;
 if(fresh==1u)return 0u;
 uintptr_t record=state+72u;
 (void)opencfw_em9305_memset((void *)pending,0u,148u);
 *(volatile uint32_t *)(state+68u)=(uint32_t)record;
 uint32_t encoding=*(volatile uint8_t *)(state+188u);
 uint32_t saved_power=*(volatile uint8_t *)(state+204u);
 uint32_t id=*(volatile uint16_t *)input;
 uint32_t saved_channel=*(volatile uint8_t *)(state+186u);
 uint32_t saved_mode=*(volatile uint8_t *)(state+187u);
 uint32_t saved_pattern=*(volatile uint8_t *)(state+184u);
 *(volatile uint8_t *)(state+74u)=(uint8_t)saved_power;
 *(volatile uint16_t *)(state+2u)=(uint16_t)id;
 *(volatile uint32_t *)(state+80u)=0x555555u;
 *(volatile uint32_t *)(state+52u)=(uint32_t)(uintptr_t)&opencfw_em9305_command_callback_332e2c;
 *(volatile uint32_t *)(state+172u)=(uint32_t)(uintptr_t)&opencfw_em9305_command_callback_332db4;
 *(volatile uint32_t *)(state+76u)=0x71764129u;
 *(volatile uint16_t *)(state+180u)=257u;
 *(volatile uint8_t *)(state+50u)=2u;
 *(volatile uint8_t *)(state+73u)=(uint8_t)saved_channel;
 *(volatile uint8_t *)(state+85u)=(uint8_t)saved_mode;
 *(volatile uint8_t *)(state+86u)=(uint8_t)encoding;
 *(volatile uint8_t *)(state+84u)=(uint8_t)saved_mode;
 uint32_t duration=opencfw_em9305_command_duration_332be4(saved_pattern,saved_mode,encoding);
 *(volatile uint16_t *)(state+182u)=(uint16_t)duration;
 uintptr_t allocation=opencfw_em9305_wsf_pool_allocate(257u);
 *(volatile uint32_t *)(state+176u)=(uint32_t)allocation;
 if(allocation==0u)return 31u;
 uint32_t input_kind=*(volatile uint8_t *)(input+4u);
 uint32_t input_pattern=*(volatile uint8_t *)(input+3u);
 (void)opencfw_em9305_command_pattern_332b94(input_pattern,input_kind,allocation);
 uint32_t saved_duration=*(volatile uint16_t *)(state+182u);
 *(volatile uint8_t *)state=1u;
 *(volatile uint8_t *)(flags+8u)=1u;
 *(volatile uint32_t *)(state+192u)=saved_duration;
 (void)opencfw_em9305_command_count_30e4bc();
 (void)opencfw_em9305_common_request_30455c(2u);
 (void)opencfw_em9305_auxiliary_insert_313220(pending);
 return 0u;
}

static uint8_t in[24];
static void setup(unsigned state){memset((void *)0x8058dc,0xa5,512);memset((void *)0x805a70,0,16);*(uint8_t *)0x8058dc=state;memset(in,0,24);in[3]=19;*(uint16_t *)in=0x1234;allocs=patterns=requests=inserts=pending=bounds=clamps=enters=exits=0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned powers[]={128,130,155,156,0,10,11,21,126,127};
for(unsigned state=0;state<2;state++)for(unsigned kind=0;kind<9;kind++)for(unsigned mode=0;mode<6;mode++)for(unsigned pi=0;pi<10;pi++)for(unsigned features=0;features<4;features++)for(alloc=0;alloc<2;alloc++){setup(state);in[2]=39;in[4]=kind;in[5]=mode;in[16]=powers[pi];*(uint8_t *)0x805995=kind;*(uint8_t *)0x805a95=(features&1?1:0)|(features&2?8:0);int power=(int8_t)in[16];unsigned range=power==126||power==127;unsigned expected=kind>=8||mode<1||mode>4?48:mode==2&&!(features&1)?17:mode>=3&&!(features&2)?17:!range&&(power<-126||power>20)?48:!range&&(power<-100||power>10)?17:kind==3||state?0:alloc?0:31;assert(opencfw_em9305_command_30e120((uintptr_t)in)==expected);unsigned reached=kind<8&&mode>=1&&mode<=4&&(mode==1||(mode==2?(features&1):(features&2)));assert(pending==reached&&bounds==reached);unsigned good=expected==0||expected==31;if(good){unsigned adjusted=power==126?156:power==127?10:(uint8_t)(power+1);assert(in[16]==adjusted);if(kind==3){assert(requests==1&&inserts==0&&allocs==0&&*(uint8_t *)0x8058dc==1&&*(uint8_t *)0x805995==3);}else{assert(enters==1&&exits==1&&*(uint8_t *)0x805994==19&&*(uint8_t *)0x805995==kind&&*(uint8_t *)0x805996==39&&*(uint8_t *)0x8059a8==adjusted);if(state){assert(!allocs&&!patterns&&!requests&&!inserts);}else{unsigned m=mode>=3?3:mode;unsigned encoding=mode==3?2:mode==4?1:0;unsigned duration=19+10*m+1000*encoding;assert(allocs==1&&patterns==alloc&&requests==alloc&&inserts==alloc&&*(uint16_t *)0x805992==duration&&*(uint16_t *)0x805990==257&&*(uint32_t *)0x80598c==(alloc?0x840000:0));}}}cases++;}
printf("PASS %u\n",cases);}
