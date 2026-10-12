#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
const uint32_t opencfw_em9305_phy_actions_33522c[2048]={0};
const uint8_t opencfw_em9305_phy_transitions_3352cc[2048]={0};
static unsigned complete,finish,reject,defer0,defer2;
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;complete++;return 0;}
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t p){(void)p;finish++;return 0;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t p,uint32_t a,uint32_t c){(void)p;if(a!=42||c!=1)abort();reject++;return 0;}
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t p){(void)p;defer0++;return 0;}
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t p){(void)p;defer2++;return 0;}
/* Genuine native action/transition tables33522c/3352cc and state children
 * remain providers; their source ownership/extent is not invented. */
extern const uint32_t opencfw_em9305_phy_actions_33522c[];
extern const uint8_t opencfw_em9305_phy_transitions_3352cc[];
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t);
extern uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t);
/* Native321150..3212ee: full master PHY state machine, including signed
 * event comparisons, callback-mutated state rereads and exact pending bits. */
uint32_t opencfw_em9305_init_phy_state_321150(uintptr_t record,uint32_t event)
{
 uint32_t force=0u,action=0u;
 if((int32_t)event>=62){
  action=7u;
  if(event==62u){if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==110u){action=4u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==112u){
   uint32_t bits=*(volatile uint32_t *)(record+644u);action=5u;
   if((bits&(1u<<21u))!=0u){*(volatile uint32_t *)(record+648u)=0u;bits&=~(1u<<21u);}
   else{action=6u;uint32_t original=bits;bits&=~(1u<<22u);if((original&(1u<<22u))==0u)return 0u;*(volatile uint32_t *)(record+648u)=0u;}
   *(volatile uint32_t *)(record+644u)=bits;
  }else return 0u;
 }else if(event==12u){
  uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
  if(operation==7u||operation==17u){action=3u;if(*(volatile uint8_t *)(uintptr_t)0x80281cu!=22u)return 0u;}
  else if(operation==13u){action=3u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(operation==22u){action=2u;force=1u;}
  else if(operation==23u)action=1u;
  else return 0u;
 }else if(event!=32u)return 0u;
 uint32_t active=*(volatile uint8_t *)(record+620u);
 if(active==0u){
  uint32_t state=*(volatile uint8_t *)(record+625u);
  uintptr_t callback=opencfw_em9305_phy_actions_33522c[state*8u+action];
  if(callback!=0u){(void)((uint32_t (*)(uintptr_t))callback)(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_phy_transitions_3352cc[state*8u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  if(next!=0u){*(volatile uint8_t *)(record+620u)=1u;*(volatile uint8_t *)(record+635u)=21u;*(volatile uint8_t *)(record+628u)=0u;}
  return 1u;
 }
 if(active!=1u)return 1u;
 uint32_t procedure=*(volatile uint8_t *)(record+635u);
 if(force!=0u){
  if(procedure-2u>=3u&&procedure!=21u&&procedure!=7u)goto deferred;
  if(procedure!=21u){
  uint32_t bits=*(volatile uint32_t *)(record+644u);
  *(volatile uint8_t *)(record+635u)=21u;
  *(volatile uint8_t *)(record+631u)=1u;
  bits|=1u<<(procedure&31u);
  *(volatile uint32_t *)(record+644u)=bits;
  }
 }else if(procedure!=21u)goto deferred;
 {
  uint32_t state=*(volatile uint8_t *)(record+625u);
  uintptr_t callback=opencfw_em9305_phy_actions_33522c[state*8u+action];
  if(callback!=0u){(void)((uint32_t (*)(uintptr_t))callback)(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_phy_transitions_3352cc[state*8u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  if(next==0u){
   (void)opencfw_em9305_phy_complete_32c818(record);
   *(volatile uint8_t *)(record+635u)=255u;
   *(volatile uint8_t *)(record+620u)=0u;
   (void)opencfw_em9305_phy_finish_32c810(record);
  }
  return 1u;
 }
 deferred:
 if(action==0u){
  (void)opencfw_em9305_phy_defer_32caa0(record);
  uint32_t first=*(volatile uint32_t *)(record+636u),second=*(volatile uint32_t *)(record+644u);
  first|=1u<<21u;second|=1u<<21u;
  *(volatile uint32_t *)(record+636u)=first;
  *(volatile uint32_t *)(record+644u)=second;
 }else if(action==2u){
  if(procedure<19u&&(0x00060002u&(1u<<procedure))!=0u)(void)opencfw_em9305_phy_reject_32698c(record,42u,1u);
  else{(void)opencfw_em9305_phy_defer_32cb48(record);uint32_t bits=*(volatile uint32_t *)(record+644u);bits|=1u<<22u;*(volatile uint32_t *)(record+644u)=bits;}
 }
 return 1u;
}

int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[700];unsigned count=0;
 for(unsigned active=0;active<4;active++)for(unsigned proc=0;proc<256;proc++)for(unsigned event=0;event<256;event++)for(unsigned operation=0;operation<24;operation++){
 memset(r,0,sizeof r);r[620]=active;r[635]=proc;r[631]=9;*(uint32_t*)(r+644)=(1u<<21)|(1u<<22);*(uint32_t*)(r+648)=123;
 *(volatile uint8_t*)0x802818=operation;*(volatile uint8_t*)0x80281c=22;
 complete=finish=reject=defer0=defer2=0;
 unsigned action=99,force=0;
 if(event==32)action=0;
 if(event==62&&proc==21)action=7;
 if(event==110&&proc==21)action=4;
 if(event==112)action=5;
 if(event==12){if(operation==7||operation==17||(operation==13&&proc==21))action=3;else if(operation==22){action=2;force=1;}else if(operation==23)action=1;}
 unsigned accepted=action!=99;
 unsigned execute=accepted&&active==1&&(proc==21||(force&&((proc>=2&&proc<=4)||proc==7)));
 unsigned deferred=accepted&&active==1&&!execute;
 unsigned er=deferred&&action==2&&proc<19&&((0x60002u>>proc)&1);
 unsigned ed2=deferred&&action==2&&!er;
 unsigned ed0=deferred&&action==0;
 unsigned result=opencfw_em9305_init_phy_state_321150((uintptr_t)r,event);
 if(result!=accepted||complete!=execute||finish!=execute||reject!=er||defer0!=ed0||defer2!=ed2||r[631]!=(execute&&force&&proc!=21?1:9))abort();
 count++;
 }
 printf("PASS %u finite transition/gate cases\n",count);return 0;
}
