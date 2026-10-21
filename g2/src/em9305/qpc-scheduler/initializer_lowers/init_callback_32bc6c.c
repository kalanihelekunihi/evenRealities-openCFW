#include <stdint.h>

extern uint32_t opencfw_em9305_child_3191dc(uint32_t context,
                                               uint32_t packet,
                                               uint32_t mode);
extern uint32_t opencfw_em9305_child_32a000(uint32_t packet, uint32_t code);

/* Native 0x32bc6c..0x32bc94. R1 is the incoming packet argument retained
 * across the first-byte test; the native callback reads R2 from record+2 in
 * the 3191dc call delay slot. The zero first byte returns R0=0. */
uint32_t opencfw_em9305_callback_32bc6c(uint32_t record, uint32_t packet)
{
    uint32_t first = *(volatile const uint8_t *)(uintptr_t)record;
    if (first == 0u) return 0u;
    uint32_t mode = *(volatile const uint8_t *)(uintptr_t)(record + 2u);
    uint32_t result = opencfw_em9305_child_3191dc(0x802810u, packet, mode);
    uint32_t code = result == 0x1eu ? 0xeu : result == 0u ? 0xcu : 0xdu;
    return opencfw_em9305_child_32a000(record, code);
}
