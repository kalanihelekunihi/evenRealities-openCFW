#include <stdint.h>
/* Own only the observed last-send word, not the preceding native context. */
volatile uint32_t r1_health_notification_last_timestamp __attribute__((section(".r1.health.notify.last"),aligned(4)))=0;
extern uint32_t r1_authenticated_phone_connection_gate(void);
extern uint32_t r1_time_backend_timestamp(void);
extern void r1_health_notification_stage_0008c150(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008cd60(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008c750(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008baec(uint32_t,uint32_t);
extern void r1_health_notification_stage_0008b818(uint32_t,uint32_t);
void r1_health_event_notification_throttle(uint32_t kind)
{
    (void)kind;
    if (!r1_authenticated_phone_connection_gate()) return;
    uint32_t now=r1_time_backend_timestamp();
    uint32_t last=r1_health_notification_last_timestamp;
    if (last && now>=last && now-last<10800u) return;
    r1_health_notification_stage_0008c150(0,0);
    r1_health_notification_stage_0008cd60(0,0);
    r1_health_notification_stage_0008c750(0,0);
    r1_health_notification_stage_0008baec(0,0);
    r1_health_notification_stage_0008b818(1,0);
    r1_health_notification_last_timestamp=now;
}
