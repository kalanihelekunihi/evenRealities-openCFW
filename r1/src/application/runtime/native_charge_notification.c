#include <stdint.h>
extern uint32_t r1_charge_state_byte_get(void);
extern uint32_t r1_charge_state_is_active(void),r1_charge_state_is_full(void);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
const uint32_t r1_charge_notification_template[2]
 __attribute__((section(".r1.charge.notification.template"),aligned(4)))={0x10200,0};
/* Stock 0x838e0 initializes both packet words before publishing seven bytes.
 * Keep separate hardware queries: the charger can change between them. */
__attribute__((section(".text.r1_event_service_000838e0")))
void r1_event_service_000838e0(void)
{
 uint32_t charge=r1_charge_state_byte_get();
 uint32_t active=r1_charge_state_is_active();
 uint32_t full=r1_charge_state_is_full();
 const volatile uint32_t *initial=r1_charge_notification_template;
 volatile uint32_t packet[2];packet[0]=initial[0];packet[1]=initial[1];
 volatile uint8_t *bytes=(volatile uint8_t *)packet;
 bytes[0]=(uint8_t)charge;bytes[1]=full?3:active?1:2;
 uint32_t handle=r1_phone_connection_handle_get();
 (void)r1_protocol_response_send_0x100(handle,127,1,0,(const void *)(uintptr_t)packet,7);
}
