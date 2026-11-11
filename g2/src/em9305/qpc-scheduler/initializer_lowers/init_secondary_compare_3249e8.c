#include <stdint.h>

static uint32_t rd32(uintptr_t p){return *(volatile uint32_t *)p;}
static uint32_t rd8(uintptr_t p){return *(volatile uint8_t *)p;}
static uint32_t mpywhl_3249e8(uint32_t a,uint32_t b)
{
    return (uint32_t)a*(uint32_t)(int32_t)(int16_t)b;
}

struct scaled_pair_3249e8 {uint32_t first,second;};
/* Native 0x324a20..0x324a4c: each value in 1.25 ms units, Cordio
 * LL_MATH_DIV_1250. Stock: MPYDU acc = v*0x1a36e3, SETACC copies the sign of
 * the high word into the guard bits (always 0: the product is below 2^53),
 * ASLACC 0xe1 shifts the accumulator right by 31, MOV reads ACC0_LO. */
static uint32_t div1250_3249e8(uint32_t value)
{
    return (uint32_t)(((uint64_t)value*0x1a36e3u)>>31);
}
static struct scaled_pair_3249e8 scaled_pair_3249e8(uint32_t a,uint32_t b)
{
    return (struct scaled_pair_3249e8){div1250_3249e8(a),div1250_3249e8(b)};
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
