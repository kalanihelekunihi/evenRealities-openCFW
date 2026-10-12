#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uintptr_t opencfw_em9305_init_transition_flag_318b38(
    uintptr_t,uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_transition_callback_328018(uintptr_t,uintptr_t);
static uint32_t signals;
uint32_t opencfw_em9305_auxiliary_signal_304394(void)
{++signals;assert(*(uint8_t *)(uintptr_t)0x8052fcu==1u);return 0u;}

static void reset(void)
{memset((void *)(uintptr_t)0x800000u,0,0x70000u);signals=0u;}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x70000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    reset();
    assert(opencfw_em9305_init_transition_flag_318b38(0x1234u,0u,0x803000u)==0x1234u);
    assert(signals==0u);
    *(uint32_t *)(uintptr_t)0x802954u=1u;
    *(uint8_t *)(uintptr_t)0x8052d4u=0x20u;
    *(uint8_t *)(uintptr_t)0x803000u=0x20u;
    assert(opencfw_em9305_init_transition_flag_318b38(5u,0x22u,0x803000u)==0x8052feu);
    assert(signals==1u&&*(uint8_t *)(uintptr_t)0x8052feu==1u);
    *(uint8_t *)(uintptr_t)0x803000u=0u;
    assert(opencfw_em9305_init_transition_flag_318b38(5u,0x22u,0x803000u)==0x8052feu);
    assert(signals==2u&&*(uint8_t *)(uintptr_t)0x8052feu==0u);
    reset();
    *(uint32_t *)(uintptr_t)0x80102cu=0x802000u;
    *(uint8_t *)(uintptr_t)0x802094u=3u;
    *(uint8_t *)(uintptr_t)0x802095u=12u;
    *(uint8_t *)(uintptr_t)0x802098u=1u;
    *(uint32_t *)(uintptr_t)0x80206cu=1u;
    assert(opencfw_em9305_init_transition_callback_328018(0x801000u,0x803000u)==1u);
    assert(signals==0u&&*(uint32_t *)(uintptr_t)0x8053ccu==0u);
    *(uint8_t *)(uintptr_t)0x802095u=11u;
    assert(opencfw_em9305_init_transition_callback_328018(0x801000u,0x803000u)==0u);
    *(uint8_t *)(uintptr_t)0x802095u=12u;
    *(uint8_t *)(uintptr_t)0x802098u=0u;
    assert(opencfw_em9305_init_transition_callback_328018(0x801000u,0x803000u)==0u);
    *(uint8_t *)(uintptr_t)0x802098u=1u;
    *(uint8_t *)(uintptr_t)0x802094u=5u;
    *(uint32_t *)(uintptr_t)0x802080u=0x804000u;
    *(uint32_t *)(uintptr_t)0x802954u=1u;
    *(uint8_t *)(uintptr_t)0x8052d4u=0x20u;
    *(uint8_t *)(uintptr_t)0x803000u=0x20u;
    *(uint8_t *)(uintptr_t)0x802095u=0x22u;
    assert(opencfw_em9305_init_transition_callback_328018(0x801000u,0x803000u)==0u);
    assert(signals==1u&&*(uint32_t *)(uintptr_t)0x8053ccu==0x804160u);
    return 0;
}
