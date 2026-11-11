#include <stdint.h>

/* Native 0x323620..0x323660: report LL event 0x2f for a 912-byte connection
 * entry (index in the table at *0x805c70) with a status byte and five
 * parameter bytes. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_2f {
    uint16_t handle;
    uint8_t code;
    uint8_t status;
    uint8_t zero;
    uint8_t reserved;
    uint16_t handle_again;
    uint8_t parameter[5];
};

uint32_t opencfw_em9305_callback_323620(uintptr_t entry, uint32_t status, uint32_t p0,
                                        uint32_t p1, uint32_t p2, uint32_t p3, uint32_t p4)
{
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    struct ll_event_2f event;
    event.status = (uint8_t)status;
    uint8_t index = (uint8_t)((int32_t)(entry - base) / 912);
    event.parameter[4] = (uint8_t)p4;
    event.parameter[3] = (uint8_t)p3;
    event.parameter[2] = (uint8_t)p2;
    event.parameter[1] = (uint8_t)p1;
    event.handle_again = index;
    event.handle = index;
    event.parameter[0] = (uint8_t)p0;
    event.zero = 0u;
    event.code = 0x2fu;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
