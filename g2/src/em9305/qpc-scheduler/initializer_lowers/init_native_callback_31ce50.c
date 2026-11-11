#include <stdint.h>

/* Native 0x31ce50..0x31ceb4: deliver an LL event message (remembered in
 * 0x805c7c). Broadcast messages (record id 255 or event 3) go to every
 * active idle entry (512-byte stride from *0x805c3c, count at config +57),
 * stamping the message with the entry's handle byte +2; others go to the
 * record found by id. */
extern uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t);
extern uint32_t opencfw_em9305_callback_child_31d0fc(uintptr_t object,uint32_t event);

void opencfw_em9305_callback_31ce50(uintptr_t message)
{
    *(volatile uint32_t *)(uintptr_t)0x805c7cu = (uint32_t)message;
    if (*(volatile uint8_t *)(message + 2u) != 255u && *(volatile uint8_t *)(message + 3u) != 3u) {
        uintptr_t record = opencfw_em9305_ll_record_find_31aa98(*(volatile uint8_t *)message);
        if (record != 0u)
            (void)opencfw_em9305_callback_child_31d0fc(record, *(volatile uint8_t *)(message + 3u));
        return;
    }
    for (uint32_t index = 0u;; ++index) {
        uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
        if (index >= *(volatile uint8_t *)(config + 57u)) return;
        uintptr_t entry = index * 512u + *(volatile uint32_t *)(uintptr_t)0x805c3cu;
        if (*(volatile uint8_t *)entry == 0u || *(volatile uint8_t *)(entry + 3u) != 0u) continue;
        uint32_t handle = *(volatile uint8_t *)(entry + 2u);
        uint32_t event = *(volatile uint8_t *)(message + 3u);
        *(volatile uint16_t *)message = (uint16_t)handle;
        (void)opencfw_em9305_callback_child_31d0fc(entry, event);
    }
}
