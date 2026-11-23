#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3255e4..0x3255fa: release the common resource (mode 1), then
 * finish the scan state block at ((uintptr_t)&em9305_ram_803d58 + 0x1280u). */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_init_state_cleanup_325740(uintptr_t);

uint32_t opencfw_em9305_scan_action_3255e4(void)
{
    (void)opencfw_em9305_common_release_304588(1u);
    return opencfw_em9305_init_state_cleanup_325740((uintptr_t)((uintptr_t)&em9305_ram_803d58 + 0x1280u));
}
