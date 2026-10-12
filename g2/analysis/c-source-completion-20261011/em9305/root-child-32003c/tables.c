#include <stdint.h>
extern void opencfw_em9305_child_31a258(void);
extern void opencfw_em9305_child_31a32c(void);
extern void opencfw_em9305_child_31a350(void);
extern void opencfw_em9305_child_31a368(void);
extern void opencfw_em9305_child_31a3ec(void);
void (*const opencfw_em9305_ext_init_actions_334e30[16])(void) __attribute__((section(".rodata.opencfw_ext_init_actions"))) = {
    0,
    0,
    opencfw_em9305_child_31a32c,
    0,
    opencfw_em9305_child_31a3ec,
    opencfw_em9305_child_31a350,
    opencfw_em9305_child_31a3ec,
    opencfw_em9305_child_31a258,
    0,
    opencfw_em9305_child_31a350,
    0,
    opencfw_em9305_child_31a368,
    0,
    opencfw_em9305_child_31a350,
    opencfw_em9305_child_31a32c,
    opencfw_em9305_child_31a368,
};
const uint8_t opencfw_em9305_ext_init_transitions_334e70[16] __attribute__((section(".rodata.opencfw_ext_init_transitions"))) = {0,1,0,0,3,1,2,0,3,2,2,0,3,3,3,0};
_Static_assert(sizeof(opencfw_em9305_ext_init_actions_334e30)==64,"ARC action table extent");
_Static_assert(sizeof(opencfw_em9305_ext_init_transitions_334e70)==16,"transition extent");
