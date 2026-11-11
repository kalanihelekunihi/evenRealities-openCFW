#include <stdint.h>

/* Native 0x31cb8c..0x31cb9c: issue common request 1, then return the
 * command count. */
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t index);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);

uint32_t opencfw_em9305_dispatch_leaf_31cb8c(void)
{
    (void)opencfw_em9305_common_request_30455c(1u);
    return opencfw_em9305_command_count_30e4bc();
}
