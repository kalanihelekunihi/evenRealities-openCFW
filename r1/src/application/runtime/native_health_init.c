#include <stdint.h>
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
/* Stock 0x8a866: preserve the full synchronous backing word, gate its byte. */
void r1_health_init_publish(uint32_t status)
{
 volatile uint32_t payload=status;
 if(*(volatile uint8_t *)&payload<4u)
  (void)r1_event_publish(0x1001,(const void *)(uintptr_t)&payload,1);
}
/* Stock 0x8d380: modes stay live; status1 publication follows diagnostics. */
void r1_event_service_0008d380(void)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000,"[RING]service heartrate algo init","[RING]service heartrate algo init");
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_0(0x001c0003,"service heartrate algo init");
 r1_health_init_publish(1);
}
