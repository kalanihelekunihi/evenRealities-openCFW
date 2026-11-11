#include <stdint.h>

/* Native 0x328d78..0x328dd2: deliver an LL control event. For a specific
 * record id (byte 2 != 255) pass the event byte +3 to native 0x329034 for
 * that record; otherwise do so for every active entry in state 1 (512-byte
 * stride from *0x805c3c, count at config +57), stamping the message with the
 * entry's handle byte +2 first. */
extern uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t);
extern uint32_t opencfw_em9305_child_329034(uintptr_t,uint32_t);

void opencfw_em9305_callback_328d78(uintptr_t message)
{
    if (*(volatile uint8_t *)(message + 2u) != 255u) {
        uintptr_t record = opencfw_em9305_ll_record_find_31aa98(*(volatile uint8_t *)message);
        if (record != 0u)
            (void)opencfw_em9305_child_329034(record, *(volatile uint8_t *)(message + 3u));
        return;
    }
    for (uint32_t index = 0u;; ++index) {
        uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
        if (index >= *(volatile uint8_t *)(config + 57u)) return;
        uintptr_t entry = *(volatile uint32_t *)(uintptr_t)0x805c3cu + index * 512u;
        if (*(volatile uint8_t *)entry == 0u || *(volatile uint8_t *)(entry + 3u) != 1u) continue;
        uint32_t handle = *(volatile uint8_t *)(entry + 2u);
        uint32_t event = *(volatile uint8_t *)(message + 3u);
        *(volatile uint16_t *)message = (uint16_t)handle;
        (void)opencfw_em9305_child_329034(*(volatile uint32_t *)(uintptr_t)0x805c3cu + index * 512u,
                                          event);
    }
}
