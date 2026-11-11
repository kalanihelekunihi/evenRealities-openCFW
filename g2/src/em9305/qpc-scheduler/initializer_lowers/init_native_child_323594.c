#include <stdint.h>

/* Native 0x323594..0x3235ba: post LL event 0x2a carrying the record's id
 * byte (+2) as handle and the byte at +290. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct init_event_323594 {
    uint16_t handle;
    uint16_t event;
    uint8_t id;
    uint8_t value;
};

uint32_t opencfw_em9305_child_323594(uintptr_t record)
{
    struct init_event_323594 message;
    uint32_t id=*(volatile uint8_t *)(record+2u);
    message.handle=(uint16_t)id;
    message.event=0x2au;
    message.id=(uint8_t)id;
    message.value=*(volatile uint8_t *)(record+290u);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&message);
}
