#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x328714..0x32874a: tear down an associated record: release the
 * common resource (mode 1), drop its schedule entry (id = 512-byte slot
 * index from *((uintptr_t)&em9305_ram_805be0 + 0x5cu), plus 7), release the record, count down the
 * command credit and, for role byte 2 (+1), post the 323594 event. */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t);
extern void opencfw_em9305_radio_record_release_31ac84(uintptr_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_child_323594(uintptr_t);

void opencfw_em9305_child_328714(uintptr_t record)
{
    (void)opencfw_em9305_common_release_304588(1u);
    uint32_t base=em9305_ram_805be0.u32_805c3c;
    (void)opencfw_em9305_associated_schedule_drop_3136ac(
        (uint8_t)((((uint32_t)record-base)>>9)+7u));
    opencfw_em9305_radio_record_release_31ac84(record);
    (void)opencfw_em9305_command_count_down_30e48c();
    if(*(volatile uint8_t *)(record+1u)==2u)
        (void)opencfw_em9305_child_323594(record);
}
