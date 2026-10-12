#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
typedef uint32_t (*opencfw_em9305_phy_action_fn)(uintptr_t);
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t);
extern uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t);
extern uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t,uint32_t);
extern const opencfw_em9305_phy_action_fn opencfw_em9305_slave_phy_actions_33565c[];
extern const uint8_t opencfw_em9305_slave_phy_transitions_335704[];
/* Native32b04c..32b20e complete slave PHY state machine. */
uint32_t opencfw_em9305_init_slave_phy_state_32b04c(uintptr_t record,uint32_t event)
{
 uint32_t action=0u,force=0u;
 if((int32_t)event>=62){
  if(event==62u){action=6u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==110u){action=4u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(event==112u){
   uint32_t bits=*(volatile uint32_t *)(record+644u),extra=*(volatile uint32_t *)(record+648u);
   if((bits^(1u<<21u))!=0u||extra!=0u)return 0u;
   action=5u;*(volatile uint32_t *)(record+648u)=0u;*(volatile uint32_t *)(record+644u)=0u;
  }else return 0u;
 }else if(event==12u){
  uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
  if(operation==7u||operation==17u){action=3u;if(*(volatile uint8_t *)(uintptr_t)0x80281cu!=22u)return 0u;}
  else if(operation==13u){action=3u;if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;}
  else if(operation==22u){action=2u;force=1u;}
  else if(operation==24u)action=1u;
  else return 0u;
 }else if(event!=32u)return 0u;
 uint32_t active=*(volatile uint8_t *)(record+620u);
 if(active==0u){
  uint32_t state=*(volatile uint8_t *)(record+625u);
  opencfw_em9305_phy_action_fn callback=opencfw_em9305_slave_phy_actions_33565c[state*7u+action];
  if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_slave_phy_transitions_335704[state*7u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  *(volatile uint8_t *)(record+634u)=(uint8_t)(next==5u);
  if(next!=0u){*(volatile uint8_t *)(record+620u)=1u;*(volatile uint8_t *)(record+635u)=21u;*(volatile uint8_t *)(record+628u)=0u;}
  return 1u;
 }
 if(active!=1u)return 1u;
 uint32_t procedure=*(volatile uint8_t *)(record+635u);
 if(force!=0u){
  if(procedure-2u>=3u&&procedure!=21u&&procedure!=7u)goto deferred;
  if(procedure!=21u){
   uint32_t bits=*(volatile uint32_t *)(record+644u);
   *(volatile uint8_t *)(record+635u)=21u;*(volatile uint8_t *)(record+631u)=1u;
   *(volatile uint32_t *)(record+644u)=bits|(1u<<(procedure&31u));
  }
 }else if(procedure!=21u)goto deferred;
 {
  uint32_t state=*(volatile uint8_t *)(record+625u);
  opencfw_em9305_phy_action_fn callback=opencfw_em9305_slave_phy_actions_33565c[state*7u+action];
  if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+625u);}
  uint32_t next=opencfw_em9305_slave_phy_transitions_335704[state*7u+action];
  *(volatile uint8_t *)(record+625u)=(uint8_t)next;
  *(volatile uint8_t *)(record+634u)=(uint8_t)(next==5u);
  if(next==0u){(void)opencfw_em9305_phy_complete_32c818(record);*(volatile uint8_t *)(record+635u)=255u;*(volatile uint8_t *)(record+620u)=0u;(void)opencfw_em9305_phy_finish_32c810(record);}
  return 1u;
 }
 deferred:
 if(action==0u){
  (void)opencfw_em9305_phy_defer_32caa0(record);
  uint32_t first=*(volatile uint32_t *)(record+636u),second=*(volatile uint32_t *)(record+644u);
  *(volatile uint32_t *)(record+636u)=first|(1u<<21u);
  *(volatile uint32_t *)(record+644u)=second|(1u<<21u);
 }else if(action==2u)(void)opencfw_em9305_phy_reject_32698c(record,42u,1u);
 else if(action==3u){
  uint32_t bits=*(volatile uint32_t *)(record+644u),state=*(volatile uint8_t *)(record+625u);
  *(volatile uint32_t *)(record+648u)=0u;*(volatile uint32_t *)(record+644u)=bits&~(1u<<21u);
  if(state!=0u)*(volatile uint8_t *)(record+625u)=0u;
  uint32_t reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
  (void)opencfw_em9305_phy_response_3232dc(record,reason);
 }
 return 1u;
}

static unsigned calls,complete,finish,mode;
static uint32_t hook(uintptr_t p){uint8_t*r=(void*)p;r[625]=(uint8_t)(mode+1);r[635]=99;calls++;return 0;}
const opencfw_em9305_phy_action_fn opencfw_em9305_slave_phy_actions_33565c[42]={hook,hook,hook,hook,hook,hook,hook};
const uint8_t opencfw_em9305_slave_phy_transitions_335704[42]={[7]=5,[8]=5,[9]=5,[10]=5,[11]=5,[12]=5,[13]=5,[14]=2,[15]=2,[16]=2,[17]=2,[18]=2,[19]=2,[20]=2};
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;complete++;return 0;}
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t p){(void)p;finish++;return 0;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t p,uint32_t a,uint32_t c){(void)p;(void)a;(void)c;abort();}
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t p){(void)p;abort();}
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t p){(void)p;abort();}
uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t p,uint32_t r){(void)p;(void)r;abort();}
int main(void){
 if(mmap((void*)0x802000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned count=0;uint8_t r[700] __attribute__((aligned(4)));unsigned events[7]={32,12,12,12,110,112,62},operations[7]={0,24,22,7,0,0,0};
 for(mode=0;mode<3;mode++)for(unsigned active=0;active<2;active++)for(unsigned action=0;action<7;action++)for(unsigned seed=0;seed<256;seed++){
 memset(r,0,sizeof r);r[620]=active;r[635]=21;r[631]=(uint8_t)seed;r[628]=37;r[634]=(uint8_t)seed;*(uint32_t*)(r+644)=1u<<21;calls=complete=finish=0;
 *(volatile uint8_t*)0x802818=operations[action];*(volatile uint8_t*)0x80281c=22;
 unsigned next=mode==0?5:mode==1?2:0;
 if(opencfw_em9305_init_slave_phy_state_32b04c((uintptr_t)r,events[action])!=1||calls!=1||r[625]!=next||r[634]!=(next==5)||r[631]!=seed)abort();
 if(active&&next==0){if(r[620]!=0||r[635]!=255||complete!=1||finish!=1||r[628]!=37)abort();}
 else{if(r[620]!=(next?1:active)||r[635]!=(active||next==0?99:21)||r[628]!=(!active&&next?0:37)||complete||finish)abort();}
 count++;
 }
 printf("PASS %u callback-mutated state and state5 cases\n",count);return 0;
}
