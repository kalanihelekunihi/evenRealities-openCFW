#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_finish_325eb4(uintptr_t,uint32_t);
static uintptr_t request=0x810000u,event=0x820000u;
static unsigned present,stage;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{assert(bytes==4u&&stage==0u);stage=1u;return present?event:0u;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p)
{
    assert(stage==1u&&handler==0x62u&&p==event);
    assert(*(uint16_t *)event==0x37u);
    assert(*(uint8_t *)(event+2u)==19u);
    assert(*(uint8_t *)(event+3u)==0xa5u);
    stage=2u;return 0x5566u;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    *(uint8_t *)(request+1u)=0x37u;
    *(uint8_t *)(uintptr_t)0x805b18u=0x62u;
    for(present=0u;present<2u;present++){
        stage=0u;
        uint32_t result=opencfw_em9305_init_transition_finish_325eb4(request,0xa5u);
        if(present) assert(result==0x5566u&&stage==2u);
        else assert(result==0u&&stage==1u);
    }
    return 0;
}
