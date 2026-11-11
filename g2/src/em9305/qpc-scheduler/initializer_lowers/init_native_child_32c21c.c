#include <stdint.h>

/* Native 0x32c21c..0x32c254: when the link (+0x24) is enabled (+67), report
 * the PHY state byte +151 of the session (+0x2c) to native 0x30e8dc for the
 * link id (+1), with bit 1 set when the state differs from +150 or the two
 * 64-bit values at +132 and +140 differ. */
extern uint32_t opencfw_em9305_child_30e8dc(uint32_t,uint32_t);

void opencfw_em9305_child_32c21c(uintptr_t context)
{
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    if (*(volatile uint8_t *)(link + 67u) == 0u) return;
    uintptr_t session = *(volatile uint32_t *)(context + 0x2cu);
    uint32_t state = *(volatile uint8_t *)(session + 151u);
    uint32_t previous = *(volatile uint8_t *)(session + 150u);
    volatile uint32_t *value = (volatile uint32_t *)(session + 132u);
    uint32_t next_high = value[3];
    uint32_t next_low = value[2];
    if (state != previous || ((value[0] ^ next_low) | (value[1] ^ next_high)) != 0u)
        state |= 2u;
    (void)opencfw_em9305_child_30e8dc(*(volatile uint8_t *)(link + 1u), state);
}
