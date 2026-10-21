/* Device status0x83de4 and charge predicates0x91244/0x91256. The charge-byte
 * getter is shared with the existing status publisher; hardware stays a seam. */
#include <stdint.h>
#include "native_battery_memory.h"
extern uint32_t r1_charge_state_byte_get(void),r1_native_charger_state_get(void);
extern uint32_t r1_phone_cmd_send_op1(const void *,uint32_t,uint32_t);
const uint32_t r1_device_status_default_record[2]
    __attribute__((section(".r1.protocol_status.default_record")))={0x00010200,0};
#define CHARGE_PREDICATE(name,expected) \
__attribute__((noinline)) uint32_t name(void) { \
    uint32_t state=r1_native_charger_state_get(); \
    register uint32_t native1 __asm__("r1"),native2 __asm__("r2"),native3 __asm__("r3"); \
    __asm__ volatile("" : "=r"(native1), "=r"(native2), "=r"(native3) : : "memory"); \
    register uint32_t out0 __asm__("r0")=state==expected; \
    __asm__ volatile("" : "+r"(out0), "+r"(native1), "+r"(native2), "+r"(native3)); \
    return out0; \
}
CHARGE_PREDICATE(r1_charge_state_is_full,2u)
CHARGE_PREDICATE(r1_charge_state_is_active,1u)
static __attribute__((used,noinline)) uint32_t status_worker(const volatile uint8_t *packet,volatile uint8_t *record)
{
    uint32_t charge=r1_charge_state_byte_get();
    uint32_t active=r1_charge_state_is_active();
    uint32_t full=r1_charge_state_is_full();
    register uint32_t raw3 __asm__("r3");
    __asm__ volatile("" : "=r"(raw3) : : "memory");
    uint32_t incoming3=raw3;
    const volatile uint8_t *initial=(const volatile uint8_t *)r1_device_status_default_record;
    uint32_t first=read32(initial),second=read32(initial+4);
    write32(record,first);write32(record+4,second);
    record[0]=(uint8_t)charge;record[1]=full?3:active?1:2;
    uint32_t sequence=read16(packet+3);
    register uint32_t native3 __asm__("r3")=incoming3;
    __asm__ volatile("" : "+r"(native3));
    uint32_t result=r1_phone_cmd_send_op1((const void *)record,0,sequence);
    register uintptr_t native1 __asm__("r1");
    __asm__ volatile("" : "=r"(native1) : : "memory");
    register uint32_t out0 __asm__("r0")=result;
    __asm__ volatile("" : "+r"(out0), "+r"(native1));return out0;
}
/* The native payload replaces the two saved incoming argument words. */
__attribute__((naked)) uint32_t r1_device_status_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{
    __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\n"
                     "mov r0,r1\n"
                     "mov r1,sp\n"
                     "bl status_worker\n"
                     "pop {r2,r3,r4,r5,r6,pc}\n");
}
