#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x319e08..0x319e9e: (re)start a connection's procedure state.
 * Requests common resource 1, clears the procedure bytes (+825..+828,
 * +2260, +2262), loads +824 from the config at ((uintptr_t)&em9305_ram_805c5c + 0x60u) and asks 32a780
 * to start with the config timeout. A failure status is reported and
 * forwarded through 325a40 (event 4). On success the started counter
 * (((uintptr_t)&em9305_ram_805a6c + 0x6u)) is bumped, the secondary count raised when +59 is set, the
 * supervision timer at +808 armed (timeout - interval/1000 - 10 ms) and
 * success reported. */
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t index);
extern uint32_t opencfw_em9305_child_32a780(uintptr_t record, uint32_t timeout);
extern uint32_t opencfw_em9305_command_rows_status_30e7ac(uint32_t handle, uint32_t status);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t record, uint32_t status);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);

uint32_t opencfw_em9305_child_319e08(uintptr_t record)
{
    (void)opencfw_em9305_common_request_30455c(1u);
    uintptr_t config=em9305_ram_805c5c.u32_805cbc;
    uint32_t value=*(volatile uint8_t *)(config+8u);
    *(volatile uint8_t *)(record+2262u)=0u;
    *(volatile uint8_t *)(record+2260u)=0u;
    *(volatile uint32_t *)(record+828u)=0u;
    *(volatile uint8_t *)(record+826u)=0u;
    *(volatile uint8_t *)(record+825u)=0u;
    *(volatile uint8_t *)(record+824u)=(uint8_t)value;
    uint32_t status=opencfw_em9305_child_32a780(record,*(volatile uint32_t *)(config+4u));
    if(status!=0u){
        (void)opencfw_em9305_command_rows_status_30e7ac(*(volatile uint8_t *)(record+1u),status);
        return opencfw_em9305_child_325a40(record,4u);
    }
    volatile uint8_t *started=&em9305_ram_805a6c.u8_805a72;
    uint32_t secondary=*(volatile uint8_t *)(record+59u);
    *started=(uint8_t)(*started+1u);
    if(secondary!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
    uint32_t timeout=*(volatile uint32_t *)(*(volatile uint32_t *)(uintptr_t)((uintptr_t)&em9305_ram_805c5c + 0x60u)+4u);
    if(timeout!=0u){
        uint32_t interval=*(volatile uint32_t *)(record+36u);
        (void)opencfw_em9305_wsf_timer_start_ms(record+808u,timeout-interval/1000u-10u);
    }
    return opencfw_em9305_command_rows_status_30e7ac(*(volatile uint8_t *)(record+1u),0u);
}
