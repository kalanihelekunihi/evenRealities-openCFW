#include <stdint.h>

/* Native 0x32aa48..0x32aa9a: deliver an extended-advertising event. Record
 * it in 0x805cbc; for a specific record id (byte 2 != 255) step that record's
 * state machine with the event byte +3, otherwise step every active entry
 * (2824-byte stride from *0x805c38, count at config +12). */
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t);
extern uint32_t opencfw_em9305_child_32ad38(uintptr_t machine, uint32_t event);

void opencfw_em9305_callback_32aa48(uintptr_t message)
{
    *(volatile uint32_t *)(uintptr_t)0x805cbcu = (uint32_t)message;
    if (*(volatile uint8_t *)(message + 2u) != 255u) {
        uintptr_t record = opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)message);
        if (record != 0u)
            (void)opencfw_em9305_child_32ad38(record, *(volatile uint8_t *)(message + 3u));
        return;
    }
    uint32_t offset = 0u;
    for (uint32_t index = 0u;; ++index, offset += 2824u) {
        uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
        if (index >= *(volatile uint8_t *)(config + 12u)) return;
        uintptr_t entry = *(volatile uint32_t *)(uintptr_t)0x805c38u + offset;
        if (*(volatile uint8_t *)entry != 0u)
            (void)opencfw_em9305_child_32ad38(entry, *(volatile uint8_t *)(message + 3u));
    }
}
