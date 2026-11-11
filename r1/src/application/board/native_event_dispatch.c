#include <stdint.h>
#include <stddef.h>

/* Linker anchors at authenticated RAM table roots. Their complete initial
 * callback configuration is still a separate data/source gate. Integer byte
 * addressing preserves the stock lookup beyond each currently known prefix.
 * Packed field loads also avoid helper calls before the indirect callback:
 * the profile callback consumes the dispatcher's ambient R3 as a fallback
 * word when the cached record read does not fill all bytes. */
extern uint8_t r1_native_event_table_sensor,r1_native_event_table_system,r1_native_event_table_storage;
extern void vPortFree(void *);
typedef struct __attribute__((packed,may_alias)) { uint16_t value; } r1_event_halfword;
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_event_word;
void r1_native_event_dispatch(const void *record)
{
    const volatile uint8_t *bytes=record;
    uint16_t id=((const volatile r1_event_halfword *)(bytes+4))->value;
    uint32_t payload=((const volatile r1_event_word *)(bytes+12))->value;
    uint16_t length=((const volatile r1_event_halfword *)(bytes+8))->value;
    uintptr_t address=0;
    if ((uint32_t)id-2u<0xffdu)
        address=(uintptr_t)&r1_native_event_table_sensor+((uint32_t)id-1u)*4u;
    else if ((uint32_t)id-0x1000u<0xfffu)
        address=(uintptr_t)&r1_native_event_table_system+((uint32_t)id-0x1000u+1u)*4u;
    else if ((uint32_t)id-0x2000u<0xfffu)
        address=(uintptr_t)&r1_native_event_table_storage+((uint32_t)id-0x2000u+1u)*4u;
    if (address) {
        uint32_t callback=((const volatile r1_event_word *)address)->value;
        if (callback) ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(payload,length);
    }
    if (length>4) vPortFree((void *)(uintptr_t)payload);
}
