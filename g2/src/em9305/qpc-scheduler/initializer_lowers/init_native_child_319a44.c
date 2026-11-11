#include <stdint.h>

/* Native 0x319a44..0x319ade: start a periodic-advertising sync from the
 * pending command at *0x805cbc. Request common resource 1, reset the sync
 * fields (+824..+831, +2260, +2262) with the command's mode byte +8, then
 * open the sync (native 0x32a780). On failure report the status for the
 * record id (+1) and post event 4; on success with a timeout (command +4,
 * ms) arm the timer at +808 for the timeout rounded down to whole sync
 * intervals (+0x24 plus 5000 us), less one interval. */
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_child_32a780(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_command_rows_status_30e7ac(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_319a44(uintptr_t record)
{
    (void)opencfw_em9305_common_request_30455c(1u);
    uintptr_t command = *(volatile uint32_t *)(uintptr_t)0x805cbcu;
    uint32_t mode = *(volatile uint8_t *)(command + 8u);
    *(volatile uint8_t *)(record + 2262u) = 0u;
    *(volatile uint8_t *)(record + 2260u) = 0u;
    *(volatile uint32_t *)(record + 828u) = 0u;
    *(volatile uint8_t *)(record + 826u) = 0u;
    *(volatile uint8_t *)(record + 825u) = 0u;
    *(volatile uint8_t *)(record + 824u) = (uint8_t)mode;
    uint32_t status = opencfw_em9305_child_32a780(record, *(volatile uint32_t *)(command + 4u));
    if (status != 0u) {
        (void)opencfw_em9305_command_rows_status_30e7ac(*(volatile uint8_t *)(record + 1u), status);
        return opencfw_em9305_child_325a40(record, 4u);
    }
    command = *(volatile uint32_t *)(uintptr_t)0x805cbcu;
    uint32_t timeout = *(volatile uint32_t *)(command + 4u);
    if (timeout == 0u) return 0u;
    uint32_t interval = *(volatile uint32_t *)(record + 0x24u) + 5000u;
    uint32_t periods = timeout * 1000u / interval - 1u;
    return opencfw_em9305_wsf_timer_start_ms(record + 808u, interval * periods / 1000u);
}
