#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
/* Genuine native action/transition tables33522c/3352cc and state children
 * remain providers; their source ownership/extent is not invented. */
typedef uint32_t (*opencfw_em9305_phy_action_fn)(uintptr_t);
extern const opencfw_em9305_phy_action_fn opencfw_em9305_phy_actions_33522c[];
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
  uintptr_t callback=(uintptr_t)opencfw_em9305_phy_actions_33522c[state*8u+action];
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
  uintptr_t callback=(uintptr_t)opencfw_em9305_phy_actions_33522c[state*8u+action];
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

static unsigned calls;
static uint32_t hook(uintptr_t p){uint8_t*r=(void*)p;r[625]=1;r[635]=99;calls++;return 0;}
const opencfw_em9305_phy_action_fn opencfw_em9305_phy_actions_33522c[40]={hook,hook,hook,hook,hook,hook,hook,hook};
const uint8_t opencfw_em9305_phy_transitions_3352cc[40]={[8]=2,[9]=2,[10]=2,[11]=2,[12]=2,[13]=2,[14]=2,[15]=2};
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;abort();}
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t p){(void)p;abort();}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t p,uint32_t a,uint32_t c){(void)p;(void)a;(void)c;abort();}
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t p){(void)p;abort();}
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t p){(void)p;abort();}
int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned count=0;uint8_t r[700];unsigned events[8]={32,12,12,12,110,112,112,62},operations[8]={0,23,22,7,0,0,0,0};
 for(unsigned active=0;active<2;active++)for(unsigned action=0;action<8;action++)for(unsigned seed=0;seed<256;seed++){
 memset(r,0,sizeof r);r[620]=active;r[635]=21;r[631]=(uint8_t)seed;r[628]=37;*(uint32_t*)(r+644)=1u<<(action==6?22:21);calls=0;
 *(volatile uint8_t*)0x802818=operations[action];*(volatile uint8_t*)0x80281c=22;
 if(opencfw_em9305_init_phy_state_321150((uintptr_t)r,events[action])!=1||calls!=1||r[625]!=2||r[620]!=1||r[631]!=seed||r[635]!=(active?99:21)||r[628]!=(active?37:0))abort();
 count++;
 }
 printf("PASS %u callback-mutated state cases\n",count);return 0;
}
