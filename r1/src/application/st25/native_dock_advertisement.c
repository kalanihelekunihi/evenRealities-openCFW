/* Stock 0x772a8: packet patch, SDK mailbox write, live result logging. */
#include <stdint.h>
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_dock_adv_success_ring[]="[RING]nfc_protocol_control_dock_adv success, switch_flag = %d";
const char r1_dock_adv_success_sdk[]="nfc_protocol_control_dock_adv success, switch_flag = %d";
const char r1_dock_adv_failed_ring[]="[RING]nfc_protocol_control_dock_adv failed, switch_flag = %d";
const char r1_dock_adv_failed_sdk[]="nfc_protocol_control_dock_adv failed, switch_flag = %d";
void r1_st25dvxxkc_dock_advertisement_send(volatile uint8_t *packet,uint32_t switch_flag)
{
 packet[1]=0x55;packet[2]=3;packet[3]=(uint8_t)switch_flag;
 uint32_t status=(uint32_t)ST25DVxxKC_WriteMailboxData(&r1_st25_device,
                           (const uint8_t *)(uintptr_t)packet,23);
 const char *ring=status ? r1_dock_adv_failed_ring : r1_dock_adv_success_ring;
 const char *sdk=status ? r1_dock_adv_failed_sdk : r1_dock_adv_success_sdk;
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c400000,ring,ring,switch_flag);
 if (r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003,sdk,switch_flag);
}
