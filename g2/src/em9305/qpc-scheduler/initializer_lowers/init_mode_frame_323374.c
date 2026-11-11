#include <stdint.h>

/* Native 0x323374..: report mode event 9 for a connection record as
 * {u16 handle, u16 9, u8 0, -, u16 handle, u8 mode, -, u16 a, u16 b},
 * taking mode/a/b from +528/+530/+532. The handle is the record index
 * ((record - base at 0x805c70) / 912). */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

struct opencfw_em9305_mode_event_9 {
    uint16_t handle;
    uint16_t code;
    uint8_t status;
    uint16_t handle_again;
    uint8_t mode;
    uint16_t first;
    uint16_t second;
};

uint32_t opencfw_em9305_mode_event_323374(uintptr_t record)
{
    struct opencfw_em9305_mode_event_9 event;
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    event.status=0u;
    event.code=9u;
    uint32_t handle=(uint8_t)((int32_t)(record-base)/912);
    event.mode=*(volatile uint8_t *)(record+528u);
    event.first=*(volatile uint16_t *)(record+530u);
    event.second=*(volatile uint16_t *)(record+532u);
    event.handle_again=(uint16_t)handle;
    event.handle=(uint16_t)handle;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
