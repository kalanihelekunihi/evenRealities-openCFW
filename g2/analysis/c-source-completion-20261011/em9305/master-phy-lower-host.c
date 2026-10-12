#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uintptr_t base,seen;static uint32_t empty,reason,time,kind;
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t p){if(p!=base+360)abort();return empty;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){if(p!=base)abort();reason=e;return 77;}
uint32_t opencfw_em9305_wsf_timer_start_seconds(uintptr_t p,uint32_t t){seen=p;time=t;kind=1;return 88;}
uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t p,uint32_t t){seen=p;time=t;kind=2;return 99;}
/* Native324680..324686 and325250..325256 complete state leaves. */
uint32_t opencfw_em9305_phy_start_324680(uintptr_t record)
{ *(volatile uint8_t *)(record+404u)=1u;return (uint32_t)(record+404u); }
uintptr_t opencfw_em9305_phy_record_325250(uintptr_t record)
{ *(volatile uint8_t *)(record+597u)=0u;return record+597u; }
/* Native318278..31828e checks actual queue and dispatches only if empty. */
uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t record)
{
 uint32_t empty=opencfw_em9305_wsf_queue_empty(record+360u);
 if(empty==0u)return empty;
 return opencfw_em9305_receive_terminate_325c08(record,62u);
}
/* Native32c7e4..32c80e; retains original record return when flag clear. */
uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record)
{
 if((*(volatile uint8_t *)(record+11u)&32u)==0u)return (uint32_t)record;
 uintptr_t timer=record+728u;
 if((*(volatile uint8_t *)(record+636u)&1u)==0u)
  return opencfw_em9305_wsf_timer_start_seconds(timer,40u);
 uint32_t timeout=*(volatile uint16_t *)(record+764u);
 return opencfw_em9305_wsf_timer_start_ms(timer,timeout);
}

int main(void){
 uint8_t r[800];base=(uintptr_t)r;unsigned count=0;
 for(unsigned timeout=0;timeout<65536;timeout++)for(unsigned flags=0;flags<4;flags++){
 memset(r,0xa5,sizeof r);r[11]=(flags&1)?32:0;r[636]=(flags>>1)&1;*(uint16_t*)(r+764)=timeout;kind=0;seen=0;
 uint32_t result=opencfw_em9305_phy_timer_start_32c7e4(base);
 if(!(flags&1)){if(result!=(uint32_t)base||kind||seen)abort();}else if(result!=((flags&2)?99:88)||kind!=((flags&2)?2:1)||time!=((flags&2)?timeout:40)||seen!=base+728)abort();
 if(opencfw_em9305_phy_start_324680(base)!=(uint32_t)(base+404)||r[404]!=1||r[403]!=0xa5||r[405]!=0xa5)abort();
 if(opencfw_em9305_phy_record_325250(base)!=base+597||r[597]||r[596]!=0xa5||r[598]!=0xa5)abort();
 empty=flags&1;reason=0;
 if(opencfw_em9305_phy_schedule_318278(base)!=(empty?77:0)||reason!=(empty?62:0))abort();
 count++;
 }
 printf("PASS %u lower-provider cases\n",count);return 0;
}
