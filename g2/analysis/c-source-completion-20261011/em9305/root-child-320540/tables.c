#include <stdint.h>
extern void opencfw_em9305_child_31a85c(void);
extern void opencfw_em9305_child_31a870(void);
extern void opencfw_em9305_child_31a8d4(void);
extern void opencfw_em9305_child_31a900(void);
extern void opencfw_em9305_child_31a918(void);
extern void opencfw_em9305_child_31a920(void);
extern void opencfw_em9305_child_31a93c(void);
extern void opencfw_em9305_child_31a980(void);
void (*const opencfw_em9305_ext_scan_actions_334ed0[16])(void) __attribute__((section(".rodata.opencfw_ext_scan_actions")))={0,opencfw_em9305_child_31a870,opencfw_em9305_child_31a918,0,opencfw_em9305_child_31a93c,opencfw_em9305_child_31a980,opencfw_em9305_child_31a93c,0,0,opencfw_em9305_child_31a900,opencfw_em9305_child_31a8d4,opencfw_em9305_child_31a920,0,opencfw_em9305_child_31a85c,opencfw_em9305_child_31a85c,opencfw_em9305_child_31a920};
const uint8_t opencfw_em9305_ext_scan_transitions_334f10[16] __attribute__((section(".rodata.opencfw_ext_scan_transitions")))={0,1,0,0,3,1,2,0,3,2,2,0,3,3,3,0};
_Static_assert(sizeof(opencfw_em9305_ext_scan_actions_334ed0)==64,"ARC pointer table extent");
_Static_assert(sizeof(opencfw_em9305_ext_scan_transitions_334f10)==16,"transition extent");
