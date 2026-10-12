#include <stdint.h>
/* SDK-bound scan tables; callback providers remain genuine unresolved imports. */
extern void opencfw_em9305_scan_action_325540(void);
extern void opencfw_em9305_scan_action_325548(void);
extern void opencfw_em9305_scan_action_3255a8(void);
extern void opencfw_em9305_scan_action_3255c0(void);
extern void opencfw_em9305_scan_action_3255c8(void);
extern void opencfw_em9305_scan_action_3255e4(void);
extern void opencfw_em9305_scan_action_3255fc(void);
extern void opencfw_em9305_scan_action_325618(void);
extern void opencfw_em9305_scan_action_325648(void);
void (*const opencfw_em9305_scan_callbacks_3353fc[20])(void)={
0,
opencfw_em9305_scan_action_325548,
opencfw_em9305_scan_action_3255c0,
0,
opencfw_em9305_scan_action_325648,
opencfw_em9305_scan_action_3255fc,
opencfw_em9305_scan_action_325618,
opencfw_em9305_scan_action_3255fc,
opencfw_em9305_scan_action_3255e4,
0,
0,
opencfw_em9305_scan_action_325540,
opencfw_em9305_scan_action_325540,
opencfw_em9305_scan_action_3255c8,
opencfw_em9305_scan_action_325648,
0,
opencfw_em9305_scan_action_325540,
opencfw_em9305_scan_action_325540,
opencfw_em9305_scan_action_3255a8,
opencfw_em9305_scan_action_325648
};
const uint8_t opencfw_em9305_scan_transitions_33544c[20]={0,1,0,0,0,3,1,2,0,1,3,2,2,0,2,3,3,3,0,3};
