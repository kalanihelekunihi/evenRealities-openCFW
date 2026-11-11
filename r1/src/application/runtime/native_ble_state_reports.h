#ifndef R1_NATIVE_BLE_STATE_REPORTS_H
#define R1_NATIVE_BLE_STATE_REPORTS_H
#include <stdint.h>
void r1_charge_state_cache_update(void);
void r1_ear_worn_state_notify(uint32_t);
uint32_t r1_phone_cmd_send_op8(const void *,uint32_t,uint32_t);
#endif
