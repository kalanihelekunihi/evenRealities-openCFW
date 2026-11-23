#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3232a8..0x3232da: report mode event 46 for the connection
 * context (handle = context index in the 912-byte table at *((uintptr_t)&em9305_ram_805c5c + 0x14u)).
 * The 12-byte event carries the handle at +0 and +6, the reason at +4 and
 * the context byte +552 at +8; bytes +5 and +9..+11 are not written, as
 * in stock. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_mode_event_3232a8(uintptr_t context,uint32_t reason)
{
    _Alignas(4) uint8_t event[12];
    uintptr_t base=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x14u);
    int32_t index=(int32_t)(context-base)/912;
    event[4]=(uint8_t)reason;
    uint32_t mode=*(volatile uint8_t *)(context+552u);
    *(uint16_t *)(void *)(event+2)=46u;
    event[8]=(uint8_t)mode;
    *(uint16_t *)(void *)(event+6)=(uint8_t)index;
    *(uint16_t *)(void *)event=(uint8_t)index;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
