#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern uint32_t opencfw_em9305_pal_random_step(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern void *opencfw_em9305_memset(void*,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
/* Native324aa8..324b38: associated stop action. Capture timing source/count
 * before PRNG call, then reload product flags exactly at native point. */
uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+2u)==1u&&*(volatile uint8_t *)(record+369u)!=0u){
  uint32_t count=*(volatile uint16_t *)(record+2250u);
  uintptr_t input=*(volatile uint32_t *)(record+1424u);
  uint32_t seed=opencfw_em9305_pal_random_step();
  uint32_t crc=opencfw_em9305_crc_update_304678(seed,count,input);
  *(volatile uint8_t *)(record+2786u)=1u;
  *(volatile uint16_t *)(record+1442u)=(uint16_t)crc;
 }
 uint32_t flag=*(volatile uint8_t *)(record+2809u);
 *(volatile uint8_t *)(record+378u)=0u;
 *(volatile uint8_t *)(record+369u)=0u;
 *(volatile uint8_t *)(record+698u)=1u;
 if(flag!=0u){
  uintptr_t packet=*(volatile uint32_t *)(record+1160u);
  *(volatile uint32_t *)(packet+3844u)=32767u;
  *(volatile uint16_t *)(packet+3840u)=0u;
  *(volatile uint32_t *)(packet+3848u)=0u;
  (void)opencfw_em9305_memset((void *)(packet+3852u),255u,15u);
 }
 return opencfw_em9305_ll_schedule_notify_313354(record+380u);
}

static uint8_t row[2824] __attribute__((aligned(4))),packet[3872] __attribute__((aligned(4))),first[8],second[8];static unsigned randoms,crcs,clears,mutate,count;
uint32_t opencfw_em9305_pal_random_step(void){randoms++;*(uint32_t*)(row+1424)=(uint32_t)(uintptr_t)second;*(uint16_t*)(row+2250)=9;row[2809]=(uint8_t)mutate;return 0x19843;}
uint32_t opencfw_em9305_crc_update_304678(uint32_t seed,uint32_t n,uintptr_t p){if(seed!=0x19843||n!=count||p!=(uintptr_t)first)abort();crcs++;return 0x12345678;}
void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){if(p!=packet+3852||v!=255||n!=15)abort();clears++;return memset(p,v,n);}
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t p){if(p!=(uintptr_t)row+380||row[378]||row[369]||row[698]!=1)abort();return 0xfeed1335;}
int main(void){unsigned cases=0;
for(count=0;count<65536;count++)for(unsigned gate=0;gate<4;gate++)for(mutate=0;mutate<2;mutate++){
 memset(row,0,sizeof row);memset(packet,0x91,sizeof packet);row[2]=(gate&1)?1:2;row[369]=(gate&2)?1:0;row[378]=27;row[2809]=1;*(uint16_t*)(row+2250)=count;*(uint32_t*)(row+1424)=(uint32_t)(uintptr_t)first;*(uint32_t*)(row+1160)=(uint32_t)(uintptr_t)packet;randoms=crcs=clears=0;
 unsigned active=gate==3,flag=active?mutate:1;
 if(opencfw_em9305_associated_action_324aa8((uintptr_t)row)!=0xfeed1335||randoms!=active||crcs!=active||clears!=flag||row[2786]!=active||(active&&*(uint16_t*)(row+1442)!=0x5678))abort();
 if(flag){if(*(uint16_t*)(packet+3840)||*(uint32_t*)(packet+3844)!=32767||*(uint32_t*)(packet+3848)||packet[3851]||packet[3852]!=255||packet[3866]!=255||packet[3867]!=0x91||packet[3839]!=0x91||packet[3842]!=0x91)abort();}
 else if(packet[3844]!=0x91||packet[3852]!=0x91)abort();
 cases++;
}
printf("PASS %u associated-stop child-mutation cases\n",cases);return 0;}
