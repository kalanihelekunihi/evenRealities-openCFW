/* Device status0x83de4 and charge predicates0x91244/0x91256. The charge-byte
 * getter is shared with the existing status publisher; hardware stays a seam. */
#include <stdint.h>
#include "native_battery_memory.h"
extern uint32_t r1_charge_state_byte_get(void),r1_native_charger_state_get(void);
extern uint32_t r1_phone_cmd_send_op1(const void *,uint32_t,uint32_t);
const uint32_t r1_device_status_default_record[2]
    __attribute__((section(".r1.protocol_status.default_record")))={0x00010200,0};
uint32_t r1_charge_state_is_full(void)
{return r1_native_charger_state_get()==2u;}
uint32_t r1_charge_state_is_active(void)
{return r1_native_charger_state_get()==1u;}
/* Query separately: the hardware state may change between calls. */
uint32_t r1_device_status_handler(uint32_t handle,const void *input,uintptr_t scratch,uint32_t seed)
{
 (void)handle;(void)scratch;(void)seed;
 const volatile uint8_t *packet=input;
 uint32_t charge=r1_charge_state_byte_get();
 uint32_t active=r1_charge_state_is_active();
 uint32_t full=r1_charge_state_is_full();
 const volatile uint8_t *initial=(const void *)r1_device_status_default_record;
 volatile uint8_t record[8];
 write32(record,read32(initial));write32(record+4,read32(initial+4));
 record[0]=(uint8_t)charge;record[1]=full?3:active?1:2;
 uint32_t sequence=read16(packet+3);
 return r1_phone_cmd_send_op1((const void *)record,0,sequence);
}
