#include <stdint.h>

/* Native 0x322dd8..0x322e12: report LL event 11 for a 912-byte connection
 * entry (index in the table at *0x805c70) with the status twice and the
 * entry byte +109. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_11 {
    uint16_t handle;
    uint8_t code;
    uint8_t status;
    uint8_t status_again;
    uint8_t reserved;
    uint16_t handle_again;
    uint8_t value;
    uint8_t zero;
};

uint32_t opencfw_em9305_child_322dd8(uintptr_t entry, uint32_t status)
{
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    struct ll_event_11 event;
    event.status_again = (uint8_t)status;
    event.status = (uint8_t)status;
    uint8_t index = (uint8_t)((int32_t)(entry - base) / 912);
    event.code = 11u;
    event.zero = 0u;
    event.value = *(volatile uint8_t *)(entry + 109u);
    event.handle_again = index;
    event.handle = index;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
