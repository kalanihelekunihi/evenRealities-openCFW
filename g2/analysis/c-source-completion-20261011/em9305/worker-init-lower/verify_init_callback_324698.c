#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_324698(uintptr_t);
static uintptr_t slot_address,second_node;
static unsigned fills,queues;
void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes)
{
    assert((uintptr_t)destination==0x820000u&&value==0u);
    assert(bytes==11u);
    ++fills;
    memset(destination,0,bytes);
    *(volatile uint32_t *)slot_address=(uint32_t)second_node;
    return destination;
}
uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t queue,uintptr_t node)
{ assert(queue==0x805194u&&node==second_node);++queues;return 0x3456u; }
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *slot=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *node=mmap((void *)0x820000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&slot!=(void *)-1&&node!=(void *)-1);
    memset(node,0xa5,32u);
    *(uint32_t *)(root+0xcacu)=(uint32_t)(uintptr_t)(root+0x100u);
    *(uint16_t *)(root+0x100u+26u)=11u;
    slot_address=(uintptr_t)slot;second_node=0x820100u;
    *(uint32_t *)slot=0x820000u;
    assert(opencfw_em9305_init_callback_324698((uintptr_t)slot)==0x3456u);
    assert(fills==1u&&queues==1u&&*(uint32_t *)slot==0u);
    for (unsigned i=0;i<11u;i++) assert(node[i]==0u);
    assert(node[11]==0xa5u);
    return 0;
}
