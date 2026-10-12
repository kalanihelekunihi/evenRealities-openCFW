#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_body_325474(uintptr_t);
static char order[16];
static unsigned used;
static uint8_t event_copy[168];
static uint32_t event_count;
static void mark(char tag){order[used++]=tag;order[used]=0;}

uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t output,uint32_t length)
{
    mark('R');assert(length==32u);
    for(unsigned i=0;i<32u;++i)*(uint8_t *)(output+i)=(uint8_t)i;
    return 32u;
}
uint32_t opencfw_em9305_radio_key_operation_30ff70(uintptr_t input,
                                                      uintptr_t key,
                                                      uintptr_t frame)
{
    mark('K');assert(input==0x80527cu&&key==0x80525cu);
    for(unsigned i=0;i<38u;++i)*(uint8_t *)(frame+i)=(uint8_t)(i+1u);
    return 0u;
}
uint32_t opencfw_em9305_radio_key_operation_30ffbc(uintptr_t key,uintptr_t output)
{
    mark('P');assert(key==0x805b60u);
    for(unsigned i=0;i<32u;++i)assert(*(uint8_t *)(key+i)==31u-i);
    for(unsigned i=0;i<64u;++i)*(uint8_t *)(output+i)=(uint8_t)(i+1u);
    return 0u;
}
uint32_t opencfw_em9305_callback_child_322e44(uintptr_t frame)
{
    mark('C');assert(*(uint8_t *)frame==1u);
    return 0u;
}
uint32_t opencfw_em9305_ll_vendor_validate_32e328(uintptr_t data,uint32_t notify)
{mark('V');assert(data==0x80527cu&&notify==0u);return 0xa5u;}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t frame)
{
    mark('E');++event_count;
    for(unsigned i=0;i<168u;++i)event_copy[i]=*(uint8_t *)(frame+i);
    return 0u;
}
void *opencfw_em9305_memset(void *destination,uint32_t fill,uint32_t size)
{mark('Z');return memset(destination,(int)fill,size);}
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t size)
{mark('M');return memcpy(destination,source,size);}

int main(void)
{
    assert(mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x805000u);
    assert(mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x806000u);
    _Alignas(4) uint8_t frame[168];
    memset(frame,0xa5,sizeof frame);
    *(uint8_t *)(uintptr_t)0x805258u=0u;
    assert(opencfw_em9305_init_callback_body_325474((uintptr_t)frame)==0u);
    assert(used==0u && frame[0]==0xa5u);
    *(uint8_t *)(uintptr_t)0x805258u=1u;
    *(uint8_t *)(uintptr_t)0x805b81u=0u;
    assert(opencfw_em9305_init_callback_body_325474((uintptr_t)frame)==0u);
    assert(strcmp(order,"RPZMME")==0);
    assert(event_count==1u && event_copy[2]==19u);
    for(unsigned i=0;i<64u;++i)assert(event_copy[5u+i]==(uint8_t)(i+1u));
    assert(*(uint8_t *)(uintptr_t)0x805258u==0u);
    assert(*(uint8_t *)(uintptr_t)0x805b80u==0u);
    used=0u;order[0]=0;
    *(uint8_t *)(uintptr_t)0x805258u=2u;
    assert(opencfw_em9305_init_callback_body_325474((uintptr_t)frame)==0u);
    assert(strcmp(order,"KC")==0 && event_count==1u);
    assert(*(uint8_t *)(uintptr_t)0x805258u==0u);
    used=0u;order[0]=0;
    memset(frame,0xa5,sizeof frame);
    *(uint8_t *)(uintptr_t)0x805258u=3u;
    assert(opencfw_em9305_init_callback_body_325474((uintptr_t)frame)==0u);
    assert(strcmp(order,"VE")==0 && event_count==2u);
    assert(*(uint32_t *)(void *)event_copy==(1u<<22));
    assert(event_copy[4]==0xa5u && event_copy[5]==0xa5u);
    return 0;
}
