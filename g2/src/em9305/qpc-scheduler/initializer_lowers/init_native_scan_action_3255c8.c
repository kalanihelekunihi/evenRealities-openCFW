#include <stdint.h>

/* Native 0x3255c8..0x3255e4: release the common resource (mode 1), finish
 * the scan state block at 0x804fd8 and report command status 0. */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_init_state_cleanup_325740(uintptr_t);
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t);

uint32_t opencfw_em9305_scan_action_3255c8(void)
{
    (void)opencfw_em9305_common_release_304588(1u);
    (void)opencfw_em9305_init_state_cleanup_325740((uintptr_t)0x804fd8u);
    return opencfw_em9305_command_status_30e8c0(0u);
}
