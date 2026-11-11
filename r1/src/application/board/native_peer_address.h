#ifndef R1_NATIVE_PEER_ADDRESS_H
#define R1_NATIVE_PEER_ADDRESS_H
#include <stdint.h>
/* Stock0x20008298..0x200082ac, separate from both advertising contexts. */
extern volatile uint8_t r1_ble_peer_address_slots[3][7];
uint32_t r1_peer_address_from_slots(uint32_t,void *);
uint32_t r1_peer_target_address_valid(const volatile void *);
uint32_t r1_peer_is_target_glasses(uint32_t);
void r1_peer_address_record_update(const volatile void *,const volatile void *);
void r1_connection_control_plan_adv_start(uint32_t);
void r1_app_ble_disconnect(uint32_t);
#endif
