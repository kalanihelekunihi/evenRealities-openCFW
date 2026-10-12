#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,valid,fail,allocations,sends,status,size,mutate;
uint32_t opencfw_em9305_ll_connection_gate_30e524(void){return gate;}
uint32_t opencfw_em9305_ll_stream_kind_valid_30e4dc(uint32_t a){assert(a==7);return valid;}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){assert(*(uint16_t *)p==0&&*(uint8_t *)(p+2)==4);status=*(uint8_t *)(p+3);return 888;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){allocations++;size=n;if(fail)return 0;if(mutate){*(uint16_t *)0x810000=66;*(uint16_t *)0x810002=55;*(uint16_t *)0x810004=0x0301;*(uint8_t *)0x810006=3;*(uint8_t *)0x805b18=9;}return 0x820000;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){assert(handler==(mutate?9:6)&&p==0x820000);sends++;return 777;}
/* Authenticated scan command children30ccf8/30df08 and status30e8c0.
 * Preserve allocation-failure returns and fresh payload reads after allocation. */
uint32_t opencfw_em9305_command_status_30e8c0(uint32_t status)
{
 uint8_t record[4] __attribute__((aligned(4)));
 record[3]=(uint8_t)status;record[2]=4u;*(uint16_t *)record=0u;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)record);
}
uint32_t opencfw_em9305_command_30ccf8(uint32_t selector,uint32_t enable)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)
  return opencfw_em9305_command_status_30e8c0(12u);
 if(selector==1u&&opencfw_em9305_ll_stream_kind_valid_30e4dc(
       *(volatile uint8_t *)(uintptr_t)0x805afdu)==0u)
  return opencfw_em9305_command_status_30e8c0(18u);
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u)return 0u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+4u)=(uint8_t)(enable!=0u);
 *(volatile uint8_t *)(message+3u)=(uint8_t)((selector==0u)+1u);
 *(volatile uint8_t *)(message+2u)=2u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}
uint32_t opencfw_em9305_command_30df08(uintptr_t record)
{
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t limit=(flags&128u)!=0u?3u:1u;
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 uint32_t secondguard=*(volatile uint8_t *)(uintptr_t)0x805a74u;
 uint32_t firstguard=*(volatile uint8_t *)(uintptr_t)0x805a73u;
 if((firstguard|secondguard)!=0u)return 12u;
 uint32_t first=*(volatile uint16_t *)record;
 if(first>=0x4001u)return 18u;
 uint32_t second=*(volatile uint16_t *)(record+2u);
 if(first<second||second<4u)return 18u;
 uint32_t mode=*(volatile uint8_t *)(record+4u);
 if(mode>=2u)return 18u;
 uint32_t phy=*(volatile uint8_t *)(record+5u);
 uint32_t phylimit=(flags&64u)!=0u?3u:1u;
 if(phylimit<phy)return 18u;
 uint32_t secondary=*(volatile uint8_t *)(record+6u);
 if(limit<secondary)return 18u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(12u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=1026u;
 first=*(volatile uint16_t *)record;
 second=*(volatile uint16_t *)(record+2u);
 *(volatile uint16_t *)(message+4u)=(uint16_t)first;
 *(volatile uint16_t *)(message+6u)=(uint16_t)second;
 uint32_t modes=*(volatile uint16_t *)(record+4u);
 *(volatile uint16_t *)(message+8u)=(uint16_t)modes;
 secondary=*(volatile uint8_t *)(record+6u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+10u)=(uint8_t)secondary;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}


static void reset(void){memset((void *)0x800000,0,0x100000);gate=valid=1;fail=allocations=sends=status=size=mutate=0;*(uint8_t *)0x805afd=7;*(uint8_t *)0x805b18=6;*(uint16_t *)0x810000=20;*(uint16_t *)0x810002=10;*(uint8_t *)0x810004=1;*(uint8_t *)0x810005=1;*(uint8_t *)0x810006=1;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned g=0;g<2;g++)for(unsigned v=0;v<2;v++)for(unsigned f=0;f<2;f++)for(unsigned selector=0;selector<4;selector++)for(unsigned enable=0;enable<3;enable++){reset();gate=g;valid=v;fail=f;unsigned r=opencfw_em9305_command_30ccf8(selector,enable);if(!g){assert(r==888&&status==12&&!allocations);}else if(selector==1&&!v){assert(r==888&&status==18&&!allocations);}else{assert(r==(f?0:777)&&allocations==1&&size==6&&sends==!f);if(!f)assert(*(uint8_t *)0x820002==2&&*(uint8_t *)0x820003==(selector==0?2:1)&&*(uint8_t *)0x820004==(enable!=0));}cases++;}
for(unsigned flags=0;flags<4;flags++)for(unsigned phy=0;phy<5;phy++)for(unsigned secondary=0;secondary<5;secondary++)for(unsigned f=0;f<2;f++){reset();*(uint32_t *)0x805a94=flags<<6;*(uint8_t *)0x810005=phy;*(uint8_t *)0x810006=secondary;fail=f;unsigned allowed=phy<=((flags&1)?3:1)&&secondary<=((flags&2)?3:1);unsigned r=opencfw_em9305_command_30df08(0x810000);assert(r==(allowed?0:18)&&allocations==allowed&&sends==(allowed&&!f));if(allowed&&!f)assert(*(uint16_t *)0x820002==1026&&*(uint16_t *)0x820004==20&&*(uint16_t *)0x820006==10&&*(uint16_t *)0x820008==(1+(phy<<8))&&*(uint8_t *)0x82000a==secondary);cases++;}
for(unsigned cut=0;cut<6;cut++){reset();if(cut==0)gate=0;if(cut==1)*(uint8_t *)0x805a73=1;if(cut==2)*(uint16_t *)0x810000=0x4001;if(cut==3)*(uint16_t *)0x810000=9;if(cut==4)*(uint16_t *)0x810002=3;if(cut==5)*(uint8_t *)0x810004=2;assert(opencfw_em9305_command_30df08(0x810000)==(cut<2?12:18)&&!allocations);cases++;}
reset();mutate=1;assert(opencfw_em9305_command_30df08(0x810000)==0&&sends==1&&*(uint16_t *)0x820004==66&&*(uint16_t *)0x820006==55&&*(uint16_t *)0x820008==0x0301&&*(uint8_t *)0x82000a==3);cases++;printf("PASS %u\n",cases);}
