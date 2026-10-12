#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_callback_32ca90(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32c86c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cfe8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cb0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cf80(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cf50(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cae4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t,uintptr_t);
static unsigned radio_calls;
uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t context,uintptr_t input)
{assert(context==0x810000u&&input==0x810236u);++radio_calls;return 0x12345u;}
static unsigned child_calls;
uint32_t opencfw_em9305_mode_callback_child_317ea4(uintptr_t context)
{assert(context==0x810000u);++child_calls;return 0x12345u;}
int main(void)
{
    uint8_t *global=mmap((void *)0x802000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *context=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(global!=(void *)-1&&root!=(void *)-1&&context!=(void *)-1);
    *(uint32_t *)(root+0xc6cu)=0x806000u;
    uint8_t *source=mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(source!=(void *)-1);
    source[4]=0x5au;
    assert(opencfw_em9305_mode_callback_32ca90((uintptr_t)context,0)==0x810000u);
    assert(context[12]==0x5au);
    *(uint32_t *)(source+4u)=0x12345678u;
    *(uint32_t *)(source+8u)=0x9abcdef0u;
    assert(opencfw_em9305_mode_callback_32c86c((uintptr_t)context,0)==0x810000u);
    assert(*(uint32_t *)(context+712u)==0x9abcdef0u);
    assert(*(uint32_t *)(context+708u)==0x12345678u);
    global[0x81cu]=0xa5u;
    assert(opencfw_em9305_mode_callback_32cfe8((uintptr_t)context,0)==0x810275u);
    assert(context[12]==0xa5u&&context[629]==1u);
    source[4]=0x12u;source[5]=0x34u;
    assert(opencfw_em9305_mode_callback_32cb0c((uintptr_t)context,0)==0x81025eu);
    assert(context[606]==0x12u&&context[607]==0x34u);
    assert(opencfw_em9305_mode_callback_32cf80((uintptr_t)context,0)==0x8102e8u);
    assert(context[744]==0x12u);
    *(uint32_t *)(global+0x81cu)=0xaabbccddu;
    *(uint16_t *)(global+0x820u)=0x1122u;
    assert(opencfw_em9305_mode_callback_32cf50((uintptr_t)context,0)==0x810214u);
    assert(context[526]==1u&&*(uint32_t *)(context+528)==0xaabbccddu);
    assert(*(uint16_t *)(context+532)==0x1122u);
    *(uint32_t *)(global+0x81cu)=0x01020304u;
    assert(opencfw_em9305_mode_callback_32cf50((uintptr_t)context,0)==0x810000u);
    assert(*(uint32_t *)(context+528)==0xaabbccddu);
    *(uint16_t *)(source+4u)=0x6789u;
    *(uint16_t *)(source+6u)=0xabcdu;
    assert(opencfw_em9305_mode_callback_32cae4((uintptr_t)context,0)==0x12345u);
    assert(*(uint16_t *)(context+570u)==0x6789u);
    assert(*(uint16_t *)(context+572u)==0xabcdu);
    assert(*(uint16_t *)(context+590u)==0x2345u&&radio_calls==1u);
    return 0;
}
