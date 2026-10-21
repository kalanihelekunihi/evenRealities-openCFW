#include <stdint.h>

/* Native 0x32de08. LP_COUNT=6 executes six two-byte iterations.
 * ARC STB.AB advances the output by two after writing byte offset eight,
 * leaving output byte nine untouched. Return value is 0x18. */
static uint8_t rd(uintptr_t p, unsigned n)
{ return *(volatile const uint8_t *)(p + n); }
static void wr16(uintptr_t p, unsigned n, uint16_t v)
{ *(volatile uint16_t *)(p + n) = v; }

uint32_t opencfw_em9305_packet_child_32de08(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    for (unsigned pair=0u; pair<4u; ++pair) {
        uint8_t high=rd(payload,2u+2u*pair);
        uint8_t low=rd(payload,1u+2u*pair);
        wr16(fields,2u*pair,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    }
    *(volatile uint8_t *)(fields+8u)=rd(payload,9u);
    uint8_t high=rd(payload,11u),low=rd(payload,10u);
    wr16(fields,10u,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    for (unsigned pair=0u; pair<6u; ++pair) {
        low=rd(payload,12u+2u*pair);
        high=rd(payload,13u+2u*pair);
        wr16(fields,12u+2u*pair,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    }
    return 24u;
}
