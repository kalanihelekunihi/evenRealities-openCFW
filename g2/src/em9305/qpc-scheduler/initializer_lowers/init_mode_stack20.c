#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x322fdc..0x323026: report LL event 7 for a 912-byte connection
 * entry (index in the table at *((uintptr_t)&em9305_ram_805c5c + 0x14u)) with the status twice; on success
 * (status 0) the event also carries the entry word +676 and halfword +680. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_7 {
    uint16_t handle;
    uint8_t code;
    uint8_t status;
    uint8_t status_again;
    uint8_t reserved;
    uint16_t handle_again;
    uint32_t value;
    uint16_t value_high;
};

uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context, uint32_t status)
{
    uintptr_t base = em9305_ram_805c5c.u32_805c70;
    struct ll_event_7 event;
    event.status_again = (uint8_t)status;
    event.status = (uint8_t)status;
    uint8_t index = (uint8_t)((int32_t)(context - base) / 912);
    event.value_high = 0u;
    event.value = 0u;
    event.code = 7u;
    event.handle_again = index;
    event.handle = index;
    if (status == 0u) {
        event.value = *(volatile uint32_t *)(context + 676u);
        event.value_high = *(volatile uint16_t *)(context + 680u);
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}

uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context)
{
 uint32_t flags=*(volatile uint32_t *)(context+636u);
 if((flags&(1u<<17u))==0u)return (uint32_t)context;
 uint32_t byte12=*(volatile uint8_t *)(context+12u);
 *(volatile uint32_t *)(context+636u)=flags&~(1u<<17u);
 *(volatile uint32_t *)(context+640u)=0u;
 return opencfw_em9305_mode_event_322fdc(context,byte12);
}
