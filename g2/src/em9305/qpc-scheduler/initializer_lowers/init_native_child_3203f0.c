#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3203f0..0x32042c: tear down a link record: release common
 * resource 1, count down the init state when flag +14 bit 0 is set, release
 * the two pending WSF events (+392, +400), then decrement the link count at
 * ((uintptr_t)&em9305_ram_805a6c + 0x7u) and count down the command state. */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);

uint32_t opencfw_em9305_child_3203f0(uintptr_t record)
{
    (void)opencfw_em9305_common_release_304588(1u);
    if ((*(volatile uint8_t *)(record + 14u) & 1u) != 0u)
        (void)opencfw_em9305_init_state_count_down_30e49c();
    volatile uint32_t *event = (volatile uint32_t *)(record + 392u);
    if (*event != 0u) {
        (void)opencfw_em9305_wsf_event_release(*event);
        *event = 0u;
    }
    event = (volatile uint32_t *)(record + 400u);
    if (*event != 0u) {
        (void)opencfw_em9305_wsf_event_release(*event);
        *event = 0u;
    }
    volatile uint8_t *links = &em9305_ram_805a6c.u8_805a73;
    *links = (uint8_t)(*links - 1u);
    return opencfw_em9305_command_count_down_30e48c();
}
