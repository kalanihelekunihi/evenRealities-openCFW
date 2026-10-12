#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc_ok,found,lookups,allocs,sends;
static uint32_t host_mpy(uint32_t id,uint32_t unit){assert(id<8);return id*unit;}
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t peer){assert(peer==0x12340003);lookups++;return found?0x830000:0;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==10);allocs++;*(uint8_t *)0x805b18=71;return alloc_ok?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t msg){assert(handler==71&&msg==0x840000);sends++;return 99;}
/* Authenticated command association apply307fcc/30805c. Same10-byte
 * message opcode has distinct half4 policies (one vs zero). */
uint32_t opencfw_em9305_command_apply_307fcc(uint32_t id,uint32_t value,uint32_t peer)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 if(id>=count)return 2u;
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(peer);
 if(associated==0u)return 66u;
 if(*(volatile uint8_t *)(associated+369u)!=1u)return 12u;
 uint32_t offset;
 offset=host_mpy(id,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 if(*(volatile uint8_t *)row==0u)return 2u;
 if((*(volatile uint8_t *)(row+547u)&2u)==0u)return 26u;
 if(*(volatile uint8_t *)(row+534u)==0u)return 26u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(10u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=0x2201u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)(message+8u)=(uint16_t)value;
 *(volatile uint16_t *)(message+6u)=(uint16_t)peer;
 *(volatile uint16_t *)message=(uint16_t)id;
 *(volatile uint16_t *)(message+4u)=1u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
uint32_t opencfw_em9305_command_apply_30805c(uint32_t id,uint32_t value,uint32_t peer)
{
 if(peer>=0xf00u)return 18u;
 if(peer>=6u)return 66u;
 uint32_t peer_offset;
 peer_offset=host_mpy(peer,784u);
 uintptr_t peer_row=0x803d78u+peer_offset;
 if(*(volatile uint8_t *)peer_row==0u)return 66u;
 if(*(volatile uint8_t *)(peer_row+1u)!=1u)return 66u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 if(id>=count)return 2u;
 uint32_t offset;
 offset=host_mpy(id,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 if(*(volatile uint8_t *)row==0u)return 2u;
 if((*(volatile uint8_t *)(row+547u)&2u)==0u)return 26u;
 if(*(volatile uint8_t *)(row+534u)==0u)return 26u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(10u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=0x2201u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)(message+8u)=(uint16_t)value;
 *(volatile uint16_t *)(message+6u)=(uint16_t)peer;
 *(volatile uint16_t *)message=(uint16_t)id;
 *(volatile uint16_t *)(message+4u)=0u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned variant=0;variant<2;variant++)for(unsigned count=0;count<5;count++)for(unsigned id=0;id<5;id++)for(unsigned lookup=0;lookup<2;lookup++)for(unsigned role=0;role<3;role++)for(unsigned active=0;active<2;active++)for(unsigned flags=0;flags<4;flags++)for(unsigned start=0;start<2;start++)for(unsigned allocation=0;allocation<2;allocation++){
memset((void *)0x800000,0,0x100000);lookups=allocs=sends=0;found=lookup;alloc_ok=allocation;*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810022=count;*(uint32_t *)0x805c70=0x820000;uintptr_t row=0x820000+id*912;*(uint8_t *)row=active;*(uint8_t *)(row+547)=flags;*(uint8_t *)(row+534)=start;*(uint8_t *)(0x830000+369)=role;*(uint8_t *)(0x803d78+3*784)=lookup;*(uint8_t *)(0x803d79+3*784)=role;
unsigned expected=variant?(!lookup||role!=1?66:id>=count?2:!active?2:!(flags&2)||!start?26:0):(id>=count?2:!lookup?66:role!=1?12:!active?2:!(flags&2)||!start?26:0);
unsigned result=variant?opencfw_em9305_command_apply_30805c(id,0xabcde,3):opencfw_em9305_command_apply_307fcc(id,0xabcde,0x12340003);assert(result==expected);unsigned eligible=expected==0;assert(allocs==eligible&&sends==(eligible&&allocation));assert(lookups==(!variant&&id<count));if(sends){uint16_t *msg=(uint16_t *)0x840000;assert(msg[0]==id&&msg[1]==0x2201&&msg[2]==!variant&&msg[3]==3&&msg[4]==0xbcde);}cases++;
}
for(unsigned peer=6;peer<0x10000;peer++){assert(opencfw_em9305_command_apply_30805c(0xffffffff,0,peer)==(peer>=0xf00?18:66));cases++;}
printf("PASS %u\n",cases);}
