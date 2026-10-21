#include <stdint.h>

/* Native 0x32dfe8: pack eight payload bytes through the already selected
 * source provider 0x304648, then store its low/high ARC return registers. */
extern uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t input);

uint32_t opencfw_em9305_packet_child_32dfe8(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uint64_t bits = opencfw_em9305_ll_pack64_304648(payload + 1u);
    uintptr_t fields = (uintptr_t)fields_word;
    *(volatile uint32_t *)(fields + 0u) = (uint32_t)bits;
    *(volatile uint32_t *)(fields + 4u) = (uint32_t)(bits >> 32u);
    return 9u;
}
