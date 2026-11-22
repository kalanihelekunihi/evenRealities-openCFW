#include <stdint.h>

/* Native 0x3255a8..0x3255be: scan lifecycle action; release common
 * resource 1, then finish the scan on the scan state block 0x804fd8. */
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_init_state_cleanup_325740(uintptr_t);

uint32_t opencfw_em9305_scan_action_3255a8(void)
{
    (void)opencfw_em9305_common_release_304588(1u);
    return opencfw_em9305_init_state_cleanup_325740((uintptr_t)0x804fd8u);
}
