#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned active;
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){(void)id;return active;}
/* Native PHY slot reads307008/30701c, query30c824..30c860 and310634.
 * Keep the first output store before the second slot/config read. */
uint32_t opencfw_em9305_ll_rx_phy_307008(uint32_t id)
{
 uint32_t offset;
 offset=id*912u;
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint8_t *)(slots+offset+77u);
}
uint32_t opencfw_em9305_ll_tx_phy_30701c(uint32_t id)
{
 uint32_t offset;
 offset=id*912u;
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint8_t *)(slots+offset+76u);
}
uint32_t opencfw_em9305_command_query_30c824(uint32_t id,uintptr_t first,uintptr_t second)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u))return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u)return 2u;
 *(volatile uint8_t *)first=(uint8_t)opencfw_em9305_ll_tx_phy_30701c(id);
 *(volatile uint8_t *)second=(uint8_t)opencfw_em9305_ll_rx_phy_307008(id);
 return 0u;
}
uint32_t opencfw_em9305_ll_command_pending_310634(void)
{
 *(volatile uint8_t *)(uintptr_t)0x805ec5u=1u;
 return 0x805ec5u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x805cac=0x820000;*(uint32_t *)0x805c70=0x830000;unsigned n=0;
for(unsigned count=0;count<4;count++)for(unsigned id=0;id<5;id++)for(active=0;active<2;active++)for(unsigned v=0;v<256;v++){*(uint8_t *)0x820022=count;*(uint8_t *)(uintptr_t)(0x830000+id*912+76)=v;*(uint8_t *)(uintptr_t)(0x830000+id*912+77)=255-v;*(uint8_t *)0x840000=99;*(uint8_t *)0x840001=98;unsigned ok=id<count&&active;assert(opencfw_em9305_command_query_30c824(id,0x840000,0x840001)==(ok?0:2));assert(*(uint8_t *)0x840000==(ok?v:99)&&*(uint8_t *)0x840001==(ok?255-v:98));n++;}
active=1;*(uint8_t *)0x820022=2;*(uint8_t *)0x83004c=231;*(uint8_t *)0x83004d=12;assert(opencfw_em9305_command_query_30c824(0,0x83004d,0x840001)==0&&*(uint8_t *)0x840001==231);assert(opencfw_em9305_ll_command_pending_310634()==0x805ec5&&*(uint8_t *)0x805ec5==1);printf("PASS %u\n",n+2);}
