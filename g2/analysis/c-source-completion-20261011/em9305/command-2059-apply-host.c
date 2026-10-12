#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t host_mpy(uint32_t id,uint32_t unit){assert(id<8&&(unit==784||unit==912));return id*unit;}
/* Authenticated command apply307d0c, readiness3213d0 and apply309874.
 * MPYUW is retained; disabled-mode path leaves the second byte untouched. */
uint32_t opencfw_em9305_command_apply_307d0c(uint32_t id,uint32_t mode)
{
 uint32_t offset;
 offset=host_mpy(id,784u);
 uintptr_t row=0x803d7eu+offset;
 uint32_t enabled=mode&1u;
 *(volatile uint8_t *)row=(uint8_t)(enabled^1u);
 if(enabled!=0u)*(volatile uint8_t *)(row+1u)=(uint8_t)((mode>>1u)&1u);
 return (uint32_t)row;
}
uint32_t opencfw_em9305_command_ready_3213d0(uint32_t id)
{
 if(id>5u)return 0u;
 uint32_t offset;
 offset=host_mpy(id,784u);
 return *(volatile uint8_t *)(uintptr_t)(0x803d78u+offset)!=0u;
}
uint32_t opencfw_em9305_command_apply_309874(uint32_t id,uint32_t mode,uint32_t first,uint32_t second,uint32_t unused)
{
 (void)unused;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 if(id>=count)return 2u;
 uint32_t offset;
 offset=host_mpy(id,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t row=base+offset;
 if(*(volatile uint8_t *)row==0u)return 2u;
 *(volatile uint16_t *)(row+618u)=(uint16_t)second;
 *(volatile uint16_t *)(row+616u)=(uint16_t)first;
 *(volatile uint8_t *)(row+614u)=(uint8_t)mode;
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned id=0;id<8;id++)for(unsigned mode=0;mode<256;mode++){uintptr_t row=0x803d7eu + id*784;*(uint8_t *)row=99;*(uint8_t *)(row+1)=88;assert(opencfw_em9305_command_apply_307d0c(id,mode)==row&&*(uint8_t *)row==((mode&1)?0:1)&&*(uint8_t *)(row+1)==((mode&1)?((mode>>1)&1):88));cases++;}
for(unsigned id=0;id<8;id++)for(unsigned active=0;active<256;active++){uintptr_t row=0x803d78+id*784;*(uint8_t *)row=active;assert(opencfw_em9305_command_ready_3213d0(id)==(id<=5&&active!=0));cases++;}
for(unsigned count=0;count<10;count++)for(unsigned id=0;id<8;id++)for(unsigned active=0;active<2;active++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810022=count;*(uint32_t *)0x805c70=0x820000;uintptr_t row=0x820000+id*912;*(uint8_t *)row=active;*(uint16_t *)(row+618)=88;*(uint16_t *)(row+616)=77;*(uint8_t *)(row+614)=66;unsigned expected=id<count&&active;assert(opencfw_em9305_command_apply_309874(id,0x12345,0x23456,0x34567,0xffffffff)==(expected?0:2));assert(*(uint16_t *)(row+618)==(expected?0x4567:88)&&*(uint16_t *)(row+616)==(expected?0x3456:77)&&*(uint8_t *)(row+614)==(expected?0x45:66));cases++;}
printf("PASS %u\n",cases);}
