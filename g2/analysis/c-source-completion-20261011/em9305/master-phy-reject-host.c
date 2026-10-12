#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t packet[8];static unsigned fail,size,calls;static uintptr_t seen;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){size=n;*(volatile uint8_t*)0x802818=0x5a;return fail?0:(uint32_t)(uintptr_t)packet;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t p,uintptr_t q){seen=p;if(q!=(uintptr_t)packet)abort();calls++;return 77;}
uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t p,uint32_t n){seen=p;if(n!=12)abort();return 55;}
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t,uint32_t);
/* Native32698c..3269ea, complete reject packet constructor/submit. */
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t record,uint32_t reason,uint32_t extended)
{
 uint32_t use_extended=1u;
 if(extended==0u){
  use_extended=0u;
  if((*(volatile uint8_t *)(record+544u)&4u)!=0u)
   use_extended=*(volatile uint8_t *)(record+534u)!=0u;
 }
 if(*(volatile uint8_t *)(record+834u)!=0u)reason=68u;
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(use_extended!=0u?3u:2u);
 if(packet==0u)return 0u;
 if(use_extended!=0u){
  *(volatile uint8_t *)packet=17u;
  uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)reason;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)operation;
 }else{
  *(volatile uint8_t *)(packet+1u)=(uint8_t)reason;
  *(volatile uint8_t *)packet=13u;
 }
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
/* Native31634c and3163a4 actual action tails. */
uint32_t opencfw_em9305_phy_action_31634c(uintptr_t record)
{ return opencfw_em9305_phy_response_3232dc(record,12u); }
uint32_t opencfw_em9305_phy_action_3163a4(uintptr_t record)
{ return opencfw_em9305_phy_reject_32698c(record,35u,1u); }

int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[900];unsigned count=0;
 for(unsigned flags=0;flags<256;flags++)for(unsigned reason=0;reason<256;reason++)for(unsigned cfg=0;cfg<16;cfg++){
 memset(r,0,sizeof r);memset(packet,0xa5,sizeof packet);r[544]=flags;r[534]=cfg&1;r[834]=(cfg>>1)&1;fail=(cfg>>2)&1;unsigned ext=(cfg>>3)&1;
 calls=0;seen=0;unsigned use=ext||((flags&4)&&(cfg&1));unsigned er=r[834]?68:reason;
 unsigned result=opencfw_em9305_phy_reject_32698c((uintptr_t)r,reason,ext);
 if(size!=(use?3:2)||result!=(fail?0:77)||calls!=!fail)abort();
 if(!fail){if(seen!=(uintptr_t)r||packet[0]!=(use?17:13)||packet[use?2:1]!=er||packet[use?3:2]!=0xa5)abort();if(use&&packet[1]!=0x5a)abort();}
 count++;
 }
 if(opencfw_em9305_phy_action_31634c((uintptr_t)r)!=55||seen!=(uintptr_t)r)abort();
 printf("PASS %u packet cases\n",count);return 0;
}
