#include <stdint.h>

static uint32_t rd32(uintptr_t p){return *(volatile uint32_t *)p;}
static uint32_t rd8(uintptr_t p){return *(volatile uint8_t *)p;}
static uint32_t mpywhl_3249e8(uint32_t a,uint32_t b)
{
#ifdef __arc__
    uint32_t out;
    __asm__ volatile("mpywhl %0,%1,%2":"=r"(out):"r"(a),"r"(b):"r58","r59","memory");
    return out;
#else
    return a*(uint32_t)(int32_t)(int16_t)b;
#endif
}

struct scaled_pair_3249e8 {uint32_t first,second;};
static struct scaled_pair_3249e8 scaled_pair_3249e8(uint32_t a,uint32_t b)
{
#ifdef __arc__
    uint32_t first,second;
    /* Exact named native DSP sequence from 0x324a20..0x324a4c. The
     * accumulator and guard state are architectural, so preserve SETACC
     * and ASLACC rather than substituting guessed division arithmetic. */
    __asm__ volatile(
        "mov r3,0x1a36e3\n\t"
        "mpydu 0,%2,r3\n\t"
        "asr r2,r59,0x1f\n\t"
        "setacc r2,r2,768\n\t"
        "mov r2,0xe1\n\t"
        "aslacc r2\n\t"
        "mov %0,r58\n\t"
        "mpydu 0,%3,r3\n\t"
        "asr r3,r59,0x1f\n\t"
        "setacc r3,r3,768\n\t"
        "mov r2,0xe1\n\t"
        "aslacc r2\n\t"
        "mov %1,r58\n\t"
        :"=&r"(first),"=&r"(second):"r"(a),"r"(b):
        "r2","r3","r58","r59","memory","cc");
    return (struct scaled_pair_3249e8){first,second};
#else
    /* Host fixture model only. Native numerical proof requires ARC DSP. */
    return (struct scaled_pair_3249e8){a,b};
#endif
}

/* Native 0x3249e8..0x324a5c: return one of the two original records.
 * Incoming R0/R1 are candidate pointers, not records themselves. */
uintptr_t opencfw_em9305_init_secondary_compare_3249e8(
    uintptr_t first,uintptr_t second)
{
    uintptr_t status=rd32(second+44u);
    if(rd8(status)!=9u)return second;
    uintptr_t second_record=rd32(second+36u);
    uint32_t second_word=rd32(second_record+708u);
    uint32_t second_extent=rd32(second_record+252u);
    if(mpywhl_3249e8(second_word,10000u)<(second_extent<<1u))
        return second;
    uintptr_t first_record=rd32(first+36u);
    uint32_t first_word=rd32(first_record+708u);
    uint32_t first_extent=rd32(first_record+252u);
    if(mpywhl_3249e8(first_word,10000u)<(first_extent<<1u))
        return first;
    struct scaled_pair_3249e8 scaled=scaled_pair_3249e8(
        first_extent,second_extent);
    if(scaled.first<(scaled.second>>2u))return second;
    if(scaled.second<(scaled.first>>2u))return first;
    return second;
}
