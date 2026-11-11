#include <stdint.h>

/* Native 0x30e858..0x30e876: report LL event 0x35 with three byte fields. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_35 {
    uint16_t reserved;
    uint16_t code;
    uint8_t value0;
    uint8_t value1;
    uint8_t value2;
};

uint32_t opencfw_em9305_child_30e858(uint32_t value0, uint32_t value1, uint32_t value2)
{
    struct ll_event_35 event;
    event.reserved = 0u;
    event.code = 0x35u;
    event.value0 = (uint8_t)value0;
    event.value1 = (uint8_t)value1;
    event.value2 = (uint8_t)value2;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
