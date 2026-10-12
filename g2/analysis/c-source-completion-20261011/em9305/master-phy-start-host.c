#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned choose_calls,apply_calls,done_calls,init_calls,timer_calls,terminate_calls,packet_calls;
static uint8_t chosenfirst,chosensecond;static unsigned expectedfirst,expectedsecond;
uint32_t opencfw_em9305_phy_choose_316610(uintptr_t p,uint32_t f,uintptr_t a,uintptr_t c,uint32_t d){(void)p;if(f!=0||d)abort();*(uint8_t*)a=chosenfirst;*(uint8_t*)c=chosensecond;choose_calls++;return 55;}
uint32_t opencfw_em9305_phy_apply_327544(uintptr_t p,uint32_t f){(void)p;if(f!=chosenfirst)abort();apply_calls++;return 0;}
uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t p){(void)p;done_calls++;return 0;}
uint32_t opencfw_em9305_phy_initiate_packet_326740(uintptr_t p,uint32_t f,uint32_t c){(void)p;if(f!=chosenfirst||c!=chosensecond)abort();init_calls++;return 0;}
uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t p){(void)p;timer_calls++;return 77;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){(void)p;if(e!=110)abort();terminate_calls++;return 88;}
uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t p,uint32_t a,uint32_t c,uint32_t d,uint32_t e){(void)p;if(a!=expectedfirst||c!=expectedsecond||d!=23||e!=45)abort();packet_calls++;return 0;}
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;return 99;}
/* Native31b39c..31b3b4: supported PHY mask from stored feature word. */
uint32_t opencfw_em9305_phy_supported_31b39c(void)
{
 uint32_t bits=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 return ((bits&256u)==0u?1u:3u)|((bits>>9u)&4u);
}
/* Native316550..316590 full peer PHY start, preserving fresh flags reload. */
uint32_t opencfw_em9305_phy_action_316550(uintptr_t record)
{
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 uint32_t second=*(volatile uint8_t *)(record+596u),first;
 if((flags&1u)==0u)first=*(volatile uint8_t *)(record+595u);
 else{first=opencfw_em9305_phy_supported_31b39c();flags=*(volatile uint8_t *)(record+594u);}
 if((flags&2u)!=0u)second=opencfw_em9305_phy_supported_31b39c();
 uint32_t four=*(volatile uint8_t *)(record+721u);
 uint32_t three=*(volatile uint8_t *)(record+720u);
 (void)opencfw_em9305_phy_update_packet_326764(record,(uint8_t)first,(uint8_t)second,three,four);
 return opencfw_em9305_phy_complete_32c818(record);
}
extern uint32_t opencfw_em9305_phy_choose_316610(uintptr_t,uint32_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_apply_327544(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_phy_initiate_packet_326740(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);
/* Native3164a8..31654e: choose, compare mapped live PHY, initiate or finish. */
uint32_t opencfw_em9305_phy_action_3164a8(uintptr_t record)
{
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 if((flags&3u)!=3u){
  uint8_t first=*(volatile uint8_t *)(record+595u);
  uint8_t second=*(volatile uint8_t *)(record+596u);
  (void)opencfw_em9305_phy_choose_316610(record,flags,(uintptr_t)&first,(uintptr_t)&second,0u);
  uint32_t mode=*(volatile uint8_t *)(record+76u),index=mode-2u;
  uint32_t mapped=index>=3u?1u:(0x00080402u>>(index*8u))&255u;
  if(first==mapped){
   mode=*(volatile uint8_t *)(record+77u);index=mode-2u;
   mapped=index>=3u?1u:(0x00080402u>>(index*8u))&255u;
   if(second==mapped)goto unchanged;
  }
  (void)opencfw_em9305_phy_apply_327544(record,first);
  (void)opencfw_em9305_phy_update_complete_32e220(record);
  (void)opencfw_em9305_phy_initiate_packet_326740(record,first,second);
  return opencfw_em9305_phy_timer_start_32c7e4(record);
 }
 unchanged:
 (void)opencfw_em9305_phy_update_complete_32e220(record);
 return opencfw_em9305_receive_terminate_325c08(record,110u);
}

int main(void){
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];unsigned count=0;
 for(unsigned flags=0;flags<256;flags++)for(unsigned feature=0;feature<4;feature++){
 memset(r,0,sizeof r);r[594]=flags;r[595]=81;r[596]=93;r[720]=23;r[721]=45;*(volatile uint32_t*)0x805a94=((feature&1)<<8)|((feature>>1)<<11);unsigned supported=1+((feature&1)*2)+((feature>>1)*4);expectedfirst=(flags&1)?supported:81;expectedsecond=(flags&2)?supported:93;packet_calls=0;
 if(opencfw_em9305_phy_action_316550((uintptr_t)r)!=99||packet_calls!=1)abort();
 count++;
 }
 const unsigned map[5]={1,1,2,4,8};
 for(unsigned m1=0;m1<256;m1++)for(unsigned m2=0;m2<256;m2++)for(unsigned changed=0;changed<2;changed++){
 memset(r,0,sizeof r);r[76]=m1;r[77]=m2;chosenfirst=m1<5?map[m1]:1;chosensecond=m2<5?map[m2]:1;if(changed)chosenfirst=99;
 choose_calls=apply_calls=done_calls=init_calls=timer_calls=terminate_calls=0;
 unsigned result=opencfw_em9305_phy_action_3164a8((uintptr_t)r);
 if(result!=(changed?77:88)||choose_calls!=1||done_calls!=1||apply_calls!=changed||init_calls!=changed||timer_calls!=changed||terminate_calls!=!changed)abort();
 count++;
 }
 printf("PASS %u PHY-start cases\n",count);return 0;
}
