#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

extern uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t output,
                                                            uintptr_t input);
extern bool opencfw_em9305_packet_switch_known(uint8_t opcode,
                                                uintptr_t context,
                                                uintptr_t payload,
                                                uint32_t mode,
                                                uint32_t *status);

/* Native 0x3191dc..0x319712: one source-owned dispatch body. All 43
 * authenticated table rows are represented by the connected switch, so no
 * interior code pointer or stock executable address is retained. */
uint32_t opencfw_em9305_child_3191dc(uint32_t context, uint32_t packet,
                                      uint32_t mode)
{
    uint32_t header_size = opencfw_em9305_short_header_decode_32dedc(context,
                                                                      packet);
    uint32_t payload = packet + header_size;
    uint8_t opcode = *(volatile const uint8_t *)(uintptr_t)payload;
    /* Native 0x3191f2 branch delay stores even an invalid opcode. */
    *(volatile uint8_t *)(uintptr_t)(context + 8u) = opcode;
    if (opcode >= 43u) return 25u;
    uint32_t status = 25u;
    (void)opencfw_em9305_packet_switch_known(opcode, context, payload, mode,
                                              &status);
    return status;
}
