#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Linker anchors at authenticated RAM table roots. Their complete initial
 * callback configuration is still a separate data/source gate. Integer byte
 * addressing preserves the stock lookup beyond each currently known prefix. */
extern uint8_t r1_native_event_table_sensor,r1_native_event_table_system,r1_native_event_table_storage;
extern void vPortFree(void *);
void r1_native_event_dispatch(const void *record)
{
    uint16_t id,length;uint32_t payload;
    const uint8_t *bytes=record;
    memcpy(&id,bytes+4,2);memcpy(&length,bytes+8,2);memcpy(&payload,bytes+12,4);
    uintptr_t address=0;
    if ((uint32_t)id-2u<0xffdu)
        address=(uintptr_t)&r1_native_event_table_sensor+((uint32_t)id-1u)*4u;
    else if ((uint32_t)id-0x1000u<0xfffu)
        address=(uintptr_t)&r1_native_event_table_system+((uint32_t)id-0x1000u+1u)*4u;
    else if ((uint32_t)id-0x2000u<0xfffu)
        address=(uintptr_t)&r1_native_event_table_storage+((uint32_t)id-0x2000u+1u)*4u;
    if (address) {
        uint32_t callback;memcpy(&callback,(const void *)address,4);
        if (callback) ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(payload,length);
    }
    if (length>4) vPortFree((void *)(uintptr_t)payload);
}
