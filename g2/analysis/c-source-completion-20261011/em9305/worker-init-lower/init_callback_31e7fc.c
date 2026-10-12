#include <stdint.h>
#include <stddef.h>

/* Native 0x31e7fc..0x31e848. The 0x314154 queue-empty child is already
 * selected source; 0x31e4a0 remains a genuine typed source contract.
 * The product count is reread at the top of each iteration. */
extern uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t queue);
extern uint32_t opencfw_em9305_child_31e4a0(uint32_t context, uint32_t code);

uint32_t opencfw_em9305_callback_31e7fc(void)
{
    uint32_t index = 0u;
    for (;;) {
        uint32_t product = *(volatile const uint32_t *)(uintptr_t)0x805cacu;
        uint32_t count = *(volatile const uint8_t *)(uintptr_t)(product + 34u);
        if (index >= count) return count;

        uint32_t base = *(volatile const uint32_t *)(uintptr_t)0x805c70u;
        uint32_t record = base + index * 912u;
        if (*(volatile const uint8_t *)(uintptr_t)record != 0u &&
            opencfw_em9305_wsf_queue_empty(record + 360u) == 0u &&
            *(volatile const uint8_t *)(uintptr_t)(base + index * 912u + 2u) == 0u) {
            opencfw_em9305_child_31e4a0(record, 61u);
        }
        ++index;
    }
}
