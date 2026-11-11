#include <stdint.h>

/* Native 0x3199f0..0x319a42: stop the record's timer at +808 and, when
 * the configured timeout (+4 of 0x805cbc, ms) is set, restart it at the
 * last whole connection interval (+36 plus 5000 us) before that timeout;
 * then copy the config byte +8 to +824, clear +825 and report the rows
 * status for the record handle. */
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);
extern uint32_t opencfw_em9305_command_rows_status_30e7ac(uint32_t handle, uint32_t status);

uint32_t opencfw_em9305_child_3199f0(uintptr_t record)
{
    uintptr_t timer=record+808u;
    (void)opencfw_em9305_wsf_timer_stop(timer);
    uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cbcu;
    uint32_t timeout=*(volatile uint32_t *)(config+4u);
    if(timeout!=0u){
        uint32_t interval=*(volatile uint32_t *)(record+36u)+5000u;
        uint32_t microseconds=timeout*1000u;
        uint32_t whole=(microseconds/interval-1u)*interval;
        (void)opencfw_em9305_wsf_timer_start_ms(timer,whole/1000u);
        config=*(volatile uint32_t *)(uintptr_t)0x805cbcu;
    }
    uint32_t value=*(volatile uint8_t *)(config+8u);
    uint32_t handle=*(volatile uint8_t *)(record+1u);
    *(volatile uint8_t *)(record+824u)=(uint8_t)value;
    *(volatile uint8_t *)(record+825u)=0u;
    return opencfw_em9305_command_rows_status_30e7ac(handle,0u);
}
