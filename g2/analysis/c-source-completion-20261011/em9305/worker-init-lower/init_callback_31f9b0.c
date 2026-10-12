#include <stdint.h>
#include <stddef.h>

/* Native 0x31f9b0..0x31fa0c. These four children remain genuine source
 * contracts; their native entry envelopes are 0x3191dc, 0x319714,
 * 0x32a000, and 0x31e4a0 respectively. */
extern uint32_t opencfw_em9305_child_3191dc(uint32_t base, uint32_t event,
                                             uint32_t mode);
extern uint32_t opencfw_em9305_child_319714(uint32_t base, uint32_t event,
                                             uint32_t mode);
extern uint32_t opencfw_em9305_child_32a000(uint32_t context, uint32_t code);
extern uint32_t opencfw_em9305_child_31e4a0(uint32_t context, uint32_t code);

uint32_t opencfw_em9305_callback_31f9b0(uint32_t context, uint32_t event)
{
    volatile const uint8_t *record = (volatile const uint8_t *)(uintptr_t)context;
    if (record[0] == 0u) return 0u;

    uint32_t first = opencfw_em9305_child_3191dc(0x802810u, event, record[2]);
    if (first == 0u) {
        return record[2] == 0u ? opencfw_em9305_child_31e4a0(context, 12u)
                               : opencfw_em9305_child_32a000(context, 12u);
    }

    uint32_t second = opencfw_em9305_child_319714(0x802810u, event, record[2]);
    if (second == 0u) {
        return record[2] == 0u ? opencfw_em9305_child_31e4a0(context, 12u)
                               : opencfw_em9305_child_32a000(context, 12u);
    }
    uint32_t code = (first == 30u || second == 30u) ? 14u : 13u;
    return record[2] == 0u ? opencfw_em9305_child_31e4a0(context, code)
                           : opencfw_em9305_child_32a000(context, code);
}
