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
/* Build-only native interface. Portable planner/backing/identity/hardware
 * admission is separate and is not changed by this control-flow source. */
__attribute__((used,noinline)) static uint32_t touch_switch_kernel(uint32_t handle,const volatile uint8_t *packet,volatile uint32_t *frame)
{
 const volatile uint8_t *payload=(const void *)r1_packet_field12_get(packet);
 if(!payload)return 0;
 frame[2]=0;frame[0]=(uintptr_t)(frame+2);frame[1]=1;
 (void)r1_protocol_send_checked(handle,7,0,0,(const void *)(uintptr_t)(frame+2),1);
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
/* Native saves r1/r2/r3 then reuses those words for the response pointer,
 * length and zeroed response. Callback mutations of the response remain visible. */
__attribute__((naked,noinline)) uint32_t r1_native_touch_switch_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{__asm__ volatile("push {r1,r2,r3,r4,r5,r6,r7,lr}\nmov r2,sp\nbl touch_switch_kernel\npop {r1,r2,r3,r4,r5,r6,r7,pc}");}
