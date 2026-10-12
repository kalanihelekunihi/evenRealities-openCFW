#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_3044e8(uintptr_t,uint32_t,uint32_t,uint32_t,uintptr_t);
static uintptr_t owner=0x801a00u, record=0x801b00u, next_record=0x801c00u;
static unsigned calls[6];
static uint32_t result;
static uint32_t read32(uintptr_t a){return *(volatile uint32_t *)a;}
static void write32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static uint32_t callback(uint32_t input,uint32_t second,uint32_t third,uint32_t fourth,uintptr_t self){assert(input==0u&&second==5u&&third==31u&&fourth==9u&&self==(uintptr_t)callback);++calls[0];return result;}
uint32_t opencfw_em9305_auxiliary_ready_303f68(void){++calls[1];return (uint32_t)owner;}
uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t p){assert(p==record);++calls[2];write32(owner+44u,(uint32_t)next_record);return 0xdeadbeefu;}
uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t p){assert(p==0x8015ccu);++calls[3];assert(read32(0x8015d8u)==18u);assert(read32(0x8015d4u)==27u);assert(read32(next_record+4u)==0x51515151u);return 0u;}
uint32_t opencfw_em9305_radio_request_30faec(uintptr_t p,uint32_t n){assert(p==0x42u && n==257u);++calls[4];return 0x2345u;}
uint32_t opencfw_em9305_radio_followup_30fb3c(uint32_t p,uint32_t n){assert(p==0x42u && n==36u);++calls[5];return 0x3456u;}
uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t p){assert(p==0u);++calls[5];return 0x4567u;}
static void reset(void){for(unsigned i=0;i<6;i++)calls[i]=0;write32(0x801900u,0x42u);write32(owner+44u,(uint32_t)record);write32(record+4u,0x51515151u);write32(record+72u,0xababababu);write32(next_record+4u,0u);}
int main(void){
 void *p=mmap((void *)0x801000u,0x2000u,PROT_READ|PROT_WRITE,MAP_ANONYMOUS|MAP_PRIVATE|MAP_FIXED_NOREPLACE,-1,0);assert(p!=(void *)-1);
 reset();assert(opencfw_em9305_init_callback_3044e8(0x801900u,5u,31u,9u,(uintptr_t)callback)==0x2345u);assert(calls[1]==1&&calls[2]==1&&calls[3]==1&&calls[4]==1);assert(*(volatile uint8_t *)(uintptr_t)0x8015c4u==1u);assert(read32(record+4u)==0xababababu);assert(read32(next_record+4u)==0x51515151u);
 reset();assert(opencfw_em9305_init_callback_3044e8(0x801900u,0u,0u,9u,(uintptr_t)callback)==0x3456u);assert(calls[5]==1&&calls[1]==0);
 reset();assert(opencfw_em9305_init_callback_3044e8(0x801900u,1u,0u,9u,(uintptr_t)callback)==0x42u);assert(calls[5]==0);
 reset();write32(0x801900u,0u);result=0u;assert(opencfw_em9305_init_callback_3044e8(0x801900u,5u,31u,9u,(uintptr_t)callback)==0x4567u);assert(calls[0]==1&&calls[5]==1);
 reset();write32(0x801900u,0u);result=0x42u;assert(opencfw_em9305_init_callback_3044e8(0x801900u,5u,31u,9u,(uintptr_t)callback)==0x2345u);assert(calls[0]==1&&calls[4]==1);
 return 0;
}
