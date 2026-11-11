#include <stdint.h>
extern uintptr_t r1_packet_field12_get(const volatile uint8_t *);
extern uint32_t r1_protocol_send_checked(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_service_touch_open(uint32_t),r1_service_touch_close(uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_touch_switch_phone_ring[] __attribute__((section(".r1.touch.switch.phone_ring")))="[RING]CMD_SYSTEM_TOUCH_SWITCH PHONE, switch_state = %d";
const char r1_touch_switch_phone_sdk[] __attribute__((section(".r1.touch.switch.phone_sdk")))="CMD_SYSTEM_TOUCH_SWITCH PHONE, switch_state = %d";
const char r1_touch_switch_glasses_ring[] __attribute__((section(".r1.touch.switch.glasses_ring")))="[RING]CMD_SYSTEM_TOUCH_SWITCH GLASSES, switch_state = %d";
const char r1_touch_switch_glasses_sdk[] __attribute__((section(".r1.touch.switch.glasses_sdk")))="CMD_SYSTEM_TOUCH_SWITCH GLASSES, switch_state = %d";
/* Stock0x84874. The registered C dispatcher supplies four arguments and
 * uses only R0; the response is an ordinary private word, not saved registers. */
uint32_t r1_touch_switch_handler_plan_decode(uint32_t handle,const void *packet_view,uintptr_t scratch,uint32_t seed)
{
 (void)scratch;(void)seed;
 const volatile uint8_t *packet=packet_view;
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload)return 0;
 volatile uint32_t response=0;
 (void)r1_protocol_send_checked(handle,7,0,0,(const void *)(uintptr_t)&response,1);
 uint32_t selector=payload[0];
 if(selector!=1 && selector!=2)return selector;
 const char *ring=selector==1?r1_touch_switch_phone_ring:r1_touch_switch_glasses_ring;
 const char *sdk=selector==1?r1_touch_switch_phone_sdk:r1_touch_switch_glasses_sdk;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,ring,ring,payload[1]);
 uint32_t mode=r1_structured_log_mode_get();uint32_t result=mode<<30;
 if(mode&2u)result=nrf_log_frontend_std_1(0x001c0003,sdk,payload[1]);
 if(selector==1)return result;
 if(payload[1])return r1_service_touch_open(0);
 return r1_service_touch_close(0);
}
/* Compatibility name, with the same function address and no second body. */
extern __typeof__(r1_touch_switch_handler_plan_decode) r1_native_touch_switch_handler
 __attribute__((alias("r1_touch_switch_handler_plan_decode")));
