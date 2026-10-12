#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_child_3246dc(uintptr_t);
static uint32_t queue_value=0x810700u,removed,prepended;
static uintptr_t cleared;
static uint32_t clear_size;
uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t queue){assert(queue==0x805194u);++removed;return queue_value++;}
uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t queue,uintptr_t block){assert(queue==0x805194u);++prepended;assert(block==cleared);return 0x55u+prepended;}
void *opencfw_em9305_memset(void *p,uint32_t value,uint32_t count){assert(value==0u);cleared=(uintptr_t)p;clear_size=count;memset(p,0,count);return p;}
int main(void){
    uintptr_t packet=0x810000u,config=0x811000u;
    assert(mmap((void *)packet,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)packet);
    assert(mmap((void *)config,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)config);
    assert(mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x805000u);
    *(volatile uint32_t *)(uintptr_t)0x805cacu=(uint32_t)config;
    *(volatile uint16_t *)(config+26u)=24u;
    for(unsigned mask=0;mask<16;mask++){
        removed=0u;queue_value=0x810700u;
        for(unsigned i=0;i<4;i++)*(uint32_t *)(packet+208u+i*4u)=(mask&(1u<<i))?(0x810800u+i*32u):0u;
        uint32_t expected=0u;
        for(unsigned i=0;i<4;i++){
            if((mask&(1u<<i))==0u)expected=queue_value++;
            else expected=0x810800u+i*32u;
        }
        queue_value=0x810700u;
        assert(opencfw_em9305_init_callback_child_3246c0(packet)==expected);
        for(unsigned i=0;i<4;i++)assert(*(uint32_t *)(packet+208u+i*4u)!=0u);
        assert(removed==4u-(unsigned)__builtin_popcount(mask));
    }
    for(unsigned mask=0;mask<16;mask++){
        prepended=0u;cleared=0u;clear_size=0u;
        for(unsigned i=0;i<4;i++)*(uint32_t *)(packet+208u+i*4u)=(mask&(1u<<i))?(0x810800u+i*32u):0u;
        uint32_t expected=(mask&8u)?0x55u+(unsigned)__builtin_popcount(mask):0u;
        assert(opencfw_em9305_init_callback_child_3246dc(packet)==expected);
        assert(prepended==(unsigned)__builtin_popcount(mask));
        for(unsigned i=0;i<4;i++)assert(*(uint32_t *)(packet+208u+i*4u)==0u);
        if(mask!=0u)assert(clear_size==24u);
    }
    return 0;
}
