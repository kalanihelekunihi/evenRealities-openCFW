#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include "associated_312918_regs.h"

extern uint32_t opencfw_em9305_init_callback_r2_experiment_32b61c(uintptr_t);
static uintptr_t const record=0x810000u,config=0x806000u;
static unsigned calls[9];
static uint32_t allocator_ok=1u,expected_timing=11u,expected_phy=2u,expected_size=100u,timer_mutates;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(v==0u&&n==148u&&p==(void *)(record+380u));++calls[0];return memset(p,(int)v,n);}
uint32_t opencfw_em9305_associated_random_31896c(void){++calls[1];return 9u;}
uint32_t opencfw_em9305_radio_crc_seed_318960(void){assert(*(volatile uint32_t *)(record+500u)==0x1234u);++calls[2];return 0x12345678u;}
uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t v){assert(v==5u);++calls[3];return 7u;}
uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t a,uint32_t b){assert(b==7u);++calls[4];return a+b;}
uint32_t opencfw_em9305_associated_four_slots_then_object_init_regs(uintptr_t a,uintptr_t p,struct opencfw_associated_312918_regs *regs){assert(a==record+428u&&p==record+380u);assert(*(volatile uint8_t *)(record+656u)==3u);++calls[5];++calls[6];*regs=(struct opencfw_associated_312918_regs){0x12340002u,0x12340003u,0x12340004u,0x12340005u,0x12340006u,0x12340007u};return 0u;}
uint32_t opencfw_em9305_associated_optional_call_regs(uintptr_t callback,uint32_t address,uint32_t budget,const struct opencfw_associated_312918_regs *regs){assert(callback==0x12345678u&&address==0x801a14u&&budget==25u);assert(regs->r2==0x12340002u&&regs->r3==0x12340003u&&regs->r4==0x12340004u&&regs->r5==0x12340005u&&regs->r6==0x12340006u&&regs->r7==0x12340007u);if(timer_mutates){*(volatile uint8_t *)(record+63u)=4u;*(volatile uint16_t *)(record+1144u)=120u;}return 11u;}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t req,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t ext,uint32_t mode,uint32_t overhead){assert(phy==expected_phy&&req==0u&&timing==expected_timing&&spacing==25u&&size==expected_size&&ext==0u&&mode==2u&&overhead==5u);++calls[7];return 70u;}
uint32_t opencfw_em9305_associated_slot_query_31b2fc(uint32_t id,uintptr_t out){(void)id;(void)out;return 0u;}
uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id,uint32_t direction,uint32_t minimum,uint32_t maximum,uint32_t extent,uintptr_t output,uintptr_t callback){assert(id==4u&&direction==1u&&minimum==70u&&maximum==100u&&extent==70u&&callback==(uintptr_t)opencfw_em9305_associated_slot_query_31b2fc);++calls[8];if(!allocator_ok)return 0u;*(volatile uint32_t *)output=73u;return 1u;}
uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t p,uint32_t n){(void)p;(void)n;return 0u;}
uint32_t opencfw_em9305_associated_cycle_tail_32b618(uintptr_t p){(void)p;return 0u;}
uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t p){(void)p;return 0u;}
uint32_t opencfw_em9305_associated_cycle_start_32b82c(uintptr_t p,uintptr_t o){assert(p==record&&o==record+380u);assert(*(volatile uint32_t *)(record+700u)==73u&&*(volatile uint32_t *)(record+400u)==73u);return 0u;}

static void setup(void){
 memset((void *)record,0,4096u);memset((void *)0x805000u,0,4096u);memset((void *)config,0,4096u);for(unsigned i=0;i<9;i++)calls[i]=0;
 *(uint32_t *)(uintptr_t)0x805cacu=(uint32_t)config;
 *(uint32_t *)(uintptr_t)0x805c38u=(uint32_t)record;
 *(uint8_t *)(uintptr_t)0x805bedu=3u;
 *(uint32_t *)(uintptr_t)0x805cc8u=0x11u;
 *(uint32_t *)(uintptr_t)0x805cccu=0x22u;
 *(uint32_t *)(uintptr_t)0x805ca0u=0x33u;
 *(uint32_t *)(uintptr_t)0x805ca4u=0x44u;
 *(uint32_t *)(uintptr_t)0x805c28u=0x55u;
 *(uint32_t *)(uintptr_t)0x801a14u=0x12345678u;
 *(uint16_t *)(config+20u)=20u;*(uint8_t *)(config+24u)=12u;
 *(uint32_t *)(record+72u)=25u;*(uint32_t *)(record+712u)=100u;*(uint32_t *)(record+708u)=60u;*(uint32_t *)(record+392u)=50u;
 *(int8_t *)(record+60u)=7;*(uint8_t *)(record+63u)=2u;*(uint8_t *)(record+697u)=4u;
 *(uint32_t *)(record+372u)=0xabcdefu;*(uint32_t *)(record+784u)=0x1234u;
 *(uint8_t *)(record+796u)=2u;*(uint8_t *)(record+797u)=4u;*(uint8_t *)(record+798u)=3u;
 *(uint16_t *)(record+1144u)=100u;*(uint8_t *)(record+804u)=1u;
}
int main(void){
 for(uintptr_t base=0x801000u;base<=0x806000u;base+=4096u)assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
 assert(mmap((void *)record,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)record);
 setup();assert(opencfw_em9305_init_callback_r2_experiment_32b61c(record)==0u);assert(calls[0]==1u&&calls[1]==1u&&calls[2]==1u&&calls[3]==1u&&calls[4]==2u&&calls[5]==1u&&calls[6]==1u&&calls[7]==1u&&calls[8]==1u);assert(*(volatile uint32_t *)(record+392u)==70u);
 setup();*(uint32_t *)(record+712u)=60u;assert(opencfw_em9305_init_callback_r2_experiment_32b61c(record)==69u);assert(calls[8]==0u);
 setup();allocator_ok=0u;assert(opencfw_em9305_init_callback_r2_experiment_32b61c(record)==67u);assert(calls[8]==1u);
 setup();allocator_ok=1u;timer_mutates=1u;expected_phy=4u;expected_size=120u;
 assert(opencfw_em9305_init_callback_r2_experiment_32b61c(record)==0u);assert(calls[7]==1u);
 return 0;
}
