/* Authenticated event leaves: special target0x84cc0 (not a locked ledger row)
 * and activity refresh0x82c10. Source compilation does not prove event delivery. */
#include <stdint.h>
#include "native_battery_memory.h"
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
uint32_t r1_protocol_command_00084cc0(uint32_t handle __attribute__((unused)),const void *packet)
{
    (void)handle;
    uint32_t length=(uint16_t)(read16((const volatile uint8_t *)packet+8)-12u);
    uintptr_t next=(uintptr_t)packet;
    if(length) {
        next=(uint32_t)next+12u;
        if(next) {
            return r1_event_publish(15,(const void *)next,9);
        }
    }
    return length;
}
/* The module dispatcher passes the selected callback and binary-search lower
 * bound in r2/r3. The stock handler uses those words as its event record. */
uint32_t r1_activity_refresh_handler(uint32_t handle,const void *packet,
                                     uintptr_t callback,uint32_t lower)
{
    (void)handle;
    const volatile uint8_t *bytes=packet;
    uint32_t flags=bytes[5];
    if(flags&2u) return flags;
    if(flags&1u) return 0;
    uint32_t record_words[2]={(uint32_t)callback,lower};
    volatile uint8_t *record=(volatile uint8_t *)record_words;
    record[0]=4;
    record[1]=0;
    write16(record+2,read16(bytes+3));
    return r1_event_publish(14,(const void *)record_words,8);
}
