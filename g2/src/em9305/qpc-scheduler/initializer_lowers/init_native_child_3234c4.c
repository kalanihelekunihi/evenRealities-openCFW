#include <stdint.h>

/* Native 0x3234c4..0x3234ec: post LL event 0x33 with status 0 and the five
 * halfword parameters (handle repeated as the event handle). */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct init_event_3234c4 {
    uint16_t handle;
    uint16_t event;
    uint8_t status;
    uint8_t reserved;
    uint16_t connection;
    uint16_t value1;
    uint16_t value2;
    uint16_t value3;
    uint16_t value4;
};

uint32_t opencfw_em9305_child_3234c4(uint32_t handle,uint32_t value1,uint32_t value2,
                                     uint32_t value3,uint32_t value4)
{
    struct init_event_3234c4 message;
    message.handle=(uint16_t)handle;
    message.event=0x33u;
    message.status=0u;
    message.connection=(uint16_t)handle;
    message.value1=(uint16_t)value1;
    message.value2=(uint16_t)value2;
    message.value3=(uint16_t)value3;
    message.value4=(uint16_t)value4;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&message);
}
