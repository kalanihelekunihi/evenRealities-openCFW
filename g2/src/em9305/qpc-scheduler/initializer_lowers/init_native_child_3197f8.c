#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3197f8..0x319838: report LL event 13 for a connection record.
 * The handle is the record index ((record - base at ((uintptr_t)&em9305_ram_805c5c + 0x14u)) / 912); the
 * event carries the 8-byte value at +445 and the halfword at +454. */
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

struct opencfw_em9305_event_13 {
    uint16_t handle;
    uint16_t code;
    uint16_t handle_again;
    uint8_t value[8];
    uint16_t extra;
};

uint32_t opencfw_em9305_child_3197f8(uintptr_t record)
{
    struct opencfw_em9305_event_13 event;
    uintptr_t base=em9305_ram_805c5c.u32_805c70;
    uint32_t handle=(uint8_t)((int32_t)(record-base)/912);
    event.code=13u;
    event.extra=*(volatile uint16_t *)(record+454u);
    event.handle_again=(uint16_t)handle;
    event.handle=(uint16_t)handle;
    (void)opencfw_em9305_memcpy(event.value,(const void *)(record+445u),8u);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
