#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern uint32_t r1_touch_synthetic_release_boundary(void);
/* Individual cold fields only; eventual context owners must alias them. */
volatile uint32_t r1_touch_client_bits __attribute__((section(".r1.touch.clients"),aligned(4)))=0;
void *volatile r1_touch_task_thread_handle __attribute__((section(".r1.touch.thread"),aligned(4)))=0;
const char r1_touch_close_ring[] __attribute__((section(".r1.touch.close.ring")))="[RING]service_touch_close: source=%d";
const char r1_touch_close_sdk[] __attribute__((section(".r1.touch.close.sdk")))="service_touch_close: source=%d";
const char r1_touch_open_ring[] __attribute__((section(".r1.touch.open.ring")))="[RING]service_touch_open: source=%d";
const char r1_touch_open_sdk[] __attribute__((section(".r1.touch.open.sdk")))="service_touch_open: source=%d";
__attribute__((noinline)) uint32_t r1_touch_task_event_post(uint32_t flags)
{return osThreadFlagsSet(r1_touch_task_thread_handle,flags);}
static uint32_t source_mask(uint32_t source)
{uint32_t shift=source&255u;return shift<32u?UINT32_C(1)<<shift:0;}
uint32_t r1_service_touch_open(uint32_t source)
{
 uint32_t mask=source_mask(source),clients=r1_touch_client_bits;
 if(mask&clients)return clients;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_touch_open_ring,r1_touch_open_ring,source);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_touch_open_sdk,source);
 if(!r1_touch_client_bits)(void)r1_touch_task_event_post(2);
 clients=r1_touch_client_bits;r1_touch_client_bits=clients|mask;
 /* Native leaves the loaded pre-OR word in r0, not the newly stored word. */
 return clients;
}
uint32_t r1_service_touch_close(uint32_t source)
{
 uint32_t mask=source_mask(source),clients=r1_touch_client_bits;
 if(!(mask&clients))return clients;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_touch_close_ring,r1_touch_close_ring,source);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_touch_close_sdk,source);
 clients=r1_touch_client_bits&~mask;r1_touch_client_bits=clients;
 if(clients)return clients;
 (void)r1_touch_synthetic_release_boundary();
 return r1_touch_task_event_post(4);
}
