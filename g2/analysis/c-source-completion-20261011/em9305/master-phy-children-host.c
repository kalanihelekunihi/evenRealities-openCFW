#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t seen;static uint32_t event;
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){seen=p;event=e;return 1234;}
uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t p){seen=p;return 4321;}
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t);
/* Native32c810 complete tail, event112. */
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record)
{ return opencfw_em9305_receive_terminate_325c08(record,112u); }
/* Native32c818..32c822: timer address derived only when record flag permits. */
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t record)
{
 if((*(volatile uint8_t *)(record+11u)&32u)==0u)return (uint32_t)record;
 return opencfw_em9305_wsf_timer_stop(record+728u);
}
/* Native32caa0..32cabe: copy four fields from captured runtime message. */
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t record)
{
 uintptr_t message=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
 *(volatile uint8_t *)(record+594u)=*(volatile uint8_t *)(message+4u);
 *(volatile uint8_t *)(record+595u)=*(volatile uint8_t *)(message+5u);
 *(volatile uint8_t *)(record+596u)=*(volatile uint8_t *)(message+6u);
 *(volatile uint8_t *)(record+79u)=*(volatile uint8_t *)(message+8u);
 return (uint32_t)record;
}
/* Native32cb48..32cb56 retains adjusted R0 return after halfword store. */
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t record)
{
 uint32_t value=*(volatile uint16_t *)(uintptr_t)0x80281cu;
 *(volatile uint16_t *)(record+720u)=(uint16_t)value;
 return (uint32_t)(record+720u);
}

int main(void){
 if(mmap((void*)0x802000,0x4000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t *r=(void*)0x803000,*m=(void*)0x804000;
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 *(volatile uint32_t*)0x805c6c=(uint32_t)(uintptr_t)m;
 unsigned count=0;
 for(unsigned v=0;v<65536;v++){
 memset(r,0xa5,800);r[11]=(uint8_t)v;seen=0;
 uint32_t result=opencfw_em9305_phy_complete_32c818((uintptr_t)r);
 if(v&32){if(result!=4321||seen!=(uintptr_t)(r+728))abort();}else if(result!=(uint32_t)(uintptr_t)r||seen)abort();
 *(volatile uint16_t*)0x80281c=(uint16_t)v;
 if(opencfw_em9305_phy_defer_32cb48((uintptr_t)r)!=(uint32_t)(uintptr_t)(r+720)||*(uint16_t*)(r+720)!=v)abort();
 m[4]=(uint8_t)v;m[5]=(uint8_t)(v>>8);m[6]=(uint8_t)(v^0x5a);m[8]=(uint8_t)(v+1);
 if(opencfw_em9305_phy_defer_32caa0((uintptr_t)r)!=(uint32_t)(uintptr_t)r||r[594]!=m[4]||r[595]!=m[5]||r[596]!=m[6]||r[79]!=m[8]||r[597]!=0xa5)abort();
 if(opencfw_em9305_phy_finish_32c810((uintptr_t)r)!=1234||seen!=(uintptr_t)r||event!=112)abort();
 count++;
 }
 printf("PASS %u child boundary cases\n",count);return 0;
}
