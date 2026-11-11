#include <stdint.h>
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
/* Stock 0x8a87e / 0x8a896: gate on the low byte, but initialize the full
 * backing word passed to the synchronous publisher. Return type is void. */
void r1_health_publish_spo2_state(uint32_t status)
{
 volatile uint32_t payload=status;
 if(*(volatile uint8_t *)&payload<2u)
  (void)r1_event_publish(0x1003,(const void *)(uintptr_t)&payload,1);
}
void r1_health_publish_temperature_state(uint32_t status)
{
 volatile uint32_t payload=status;
 if(*(volatile uint8_t *)&payload<2u)
  (void)r1_event_publish(0x1007,(const void *)(uintptr_t)&payload,1);
}
