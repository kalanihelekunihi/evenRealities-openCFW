#include <stdint.h>

/* Native 0x320274..0x3202e0: while the link (+0x24) requests (+1) and is not
 * on hold (+241), insert its connection entry's schedule node (+16) into the
 * schedule; when the slot is taken, push the anchor (+24) out by k connection
 * intervals (+266, units of 1250 us) and bump the event counter (+262) until
 * the insertion succeeds. Then run the retry step native 0x320314. */
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern void opencfw_em9305_child_320314(uintptr_t context);

void opencfw_em9305_child_320274(uintptr_t context)
{
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    if (*(volatile uint8_t *)(link + 1u) != 0u && *(volatile uint8_t *)(link + 241u) == 0u) {
        uint32_t handle = *(volatile uint16_t *)(link + 88u);
        uintptr_t entry = *(volatile uint32_t *)(uintptr_t)0x805c70u + handle * 912u;
        uintptr_t compare = (uintptr_t)opencfw_em9305_init_schedule_compare_318b78;
        uint32_t anchor = *(volatile uint32_t *)(entry + 24u);
        uintptr_t node = entry + 16u;
        if (opencfw_em9305_associated_schedule_insert_312da4(node, compare) == 0u) {
            uint32_t step = 1u;
            do {
                uint32_t delay = (step & 0xffffu) * *(volatile uint16_t *)(entry + 266u) * 1250u;
                volatile uint16_t *counter = (volatile uint16_t *)(entry + 262u);
                *counter = (uint16_t)(*counter + 1u);
                *(volatile uint32_t *)(entry + 24u) = anchor + delay;
                ++step;
            } while (opencfw_em9305_associated_schedule_insert_312da4(node, compare) == 0u);
        }
    }
    opencfw_em9305_child_320314(context);
}
