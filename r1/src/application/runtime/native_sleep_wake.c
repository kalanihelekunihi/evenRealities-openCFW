#include <stdint.h>
#include "native_sleep_wake.h"
/* Authenticated cold RW8 @20006ed4; neighboring sleep fields are separate. */
volatile struct r1_sleep_wake_control r1_sleep_wake_control
    __attribute__((section(".r1.sleep.wake.control"),aligned(4)))={0};
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_temp_sleep_status_report(uint32_t);
extern void r1_gomore_sleep_force_wake_native(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_sleep_config_flag_get(void);
void r1_sleep_wake_timer_callback(uint32_t);

/* Stock 0x4a3e8 accepts a type-1 record only when it has encoded stages.
 * Without a living-confirmation latch it drops every record. */
uint32_t r1_sleep_drop_guard(const void *record)
{
    const volatile uint8_t *bytes=(const volatile uint8_t *)record;
    if (r1_sleep_config_flag_get()!=0u)
        return bytes[0]!=1u || (uint16_t)(bytes[30]|(uint16_t)bytes[31]<<8)!=0u;
    const char *ring="[RING]sleep drop: no living confirm during sleep period";
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,"sleep drop: no living confirm during sleep period");
    return 0;
}

/* Native 0x4a4b4 ignores event payload/length, gates on active exactly 1,
 * then takes the timer decision after publishing the updated state byte. */
void r1_algo_sleep_force_awake(uint32_t payload,uint32_t length)
{
    (void)payload;(void)length;
    if (r1_sleep_wake_control.active!=1) return;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,"[RING]algo sleep force awake","[RING]algo sleep force awake");
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003,"algo sleep force awake");
    r1_sleep_wake_control.active=0;
    r1_temp_sleep_status_report(0);
    r1_gomore_sleep_force_wake_native();
    (void)r1_event_publish(12,(const void *)&r1_sleep_wake_control,1);
    if (!r1_sleep_wake_control.timer)
        r1_sleep_wake_control.timer=r1_stream_timer_create_front(
            (uint32_t)(uintptr_t)r1_sleep_wake_timer_callback,3000,0);
}
extern void r1_event_service_0004a4b4(uint32_t,uint32_t)
    __attribute__((alias("r1_algo_sleep_force_awake")));

struct __attribute__((packed,may_alias)) wake_half { uint16_t value; };
/* Preserve the native byte/byte/halfword writes. packet[1] begins as the
 * incoming R3 word, and mutations through the publish pointer remain live. */
__attribute__((noinline,used)) void
r1_sleep_wake_timer_body(uint32_t timer,volatile uint32_t *packet)
{
    volatile uint8_t *bytes=(volatile uint8_t *)packet;
    bytes[0]=6;bytes[1]=1;
    ((volatile struct wake_half *)(bytes+2))->value=0;
    (void)r1_event_publish(14,(const void *)packet,8);
    (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
    r1_sleep_wake_control.timer=0;
}

/* The consumer reads the first four event bytes; define the remaining word
 * while keeping the native event width and timer update order. */
void r1_sleep_wake_timer_callback(uint32_t timer)
{
    volatile uint32_t packet[2]={0,0};
    r1_sleep_wake_timer_body(timer,packet);
}
