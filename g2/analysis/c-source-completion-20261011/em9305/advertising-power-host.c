#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
static int32_t measured;
static uint32_t opencfw_em9305_radio_status_311a00(uint32_t q){if(q!=1)__builtin_trap();return (uint32_t)measured;}
/* Native310230..310260: signed live upper/lower caps and measured query. */
uint32_t opencfw_em9305_command_radio_power_310230(int32_t requested,uint32_t unused)
{
 (void)unused;
 int32_t measured=(int32_t)opencfw_em9305_radio_status_311a00(1u);
 int32_t upper=(int8_t)*(volatile uint8_t *)(uintptr_t)0x8012b8u;
 if(upper>measured)upper=measured;
 if(upper<requested)return (uint32_t)upper;
 int32_t lower=(int8_t)*(volatile uint8_t *)(uintptr_t)0x8012b9u;
 return (uint32_t)(lower>requested?lower:requested);
}

int main(void){if(mmap((void*)0x800000,8192,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;unsigned cases=0,fail=0;int32_t qs[]={-128,-58,-1,0,10,127};
for(unsigned q=0;q<6;q++)for(int32_t upper=-128;upper<128;upper++)for(int32_t lower=-128;lower<128;lower++)for(int32_t req=-128;req<128;req++){
 measured=qs[q];*(uint8_t*)0x8012b8=upper;*(uint8_t*)0x8012b9=lower;int32_t cap=upper<measured?upper:measured,want=req>cap?cap:req<lower?lower:req;
 if((int32_t)opencfw_em9305_command_radio_power_310230(req,37)!=want)fail++;cases++;}
printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;}
