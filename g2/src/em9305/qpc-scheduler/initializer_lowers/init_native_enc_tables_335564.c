#include <stdint.h>
/* SDK-bound extents and callback slot mapping; final placement/runtime bounds remain open. */
extern void opencfw_em9305_child_31b714(void);
extern void opencfw_em9305_enc_action_315974(void);
extern void opencfw_em9305_enc_action_3159bc(void);
extern void opencfw_em9305_enc_action_315dd8(void);
extern void opencfw_em9305_enc_action_315e14(void);
extern void opencfw_em9305_enc_action_315f80(void);
extern void opencfw_em9305_enc_action_3165a4(void);
extern void opencfw_em9305_enc_action_3165c4(void);
extern void opencfw_em9305_enc_action_3197d0(void);
void (*const opencfw_em9305_enc_actions_335564[49])(void) = {
    opencfw_em9305_enc_action_315dd8,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    0,
    0,
    0,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    0,
    0,
    opencfw_em9305_enc_action_3165c4,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_enc_action_3159bc,
    opencfw_em9305_enc_action_315974,
    0,
    opencfw_em9305_child_31b714,
    opencfw_em9305_enc_action_315f80,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    0,
    0,
    0,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_enc_action_315e14,
    opencfw_em9305_child_31b714,
    0,
    0,
    0,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    0,
    0,
    opencfw_em9305_enc_action_3165a4,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_child_31b714,
    opencfw_em9305_enc_action_3197d0,
    0,
    0,
    0,
};
const uint8_t opencfw_em9305_enc_transitions_335628[49] = {1,0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,3,0,2,3,4,3,3,3,3,3,4,4,5,4,4,4,4,5,5,5,5,5,5,6,6,6,6,0,6,6,6};
_Static_assert(sizeof(opencfw_em9305_enc_actions_335564)==196,"ARC action extent");
_Static_assert(sizeof(opencfw_em9305_enc_transitions_335628)==49,"transition extent");

/* Native consumer bounds the index to 0..8 before this load. */
const uint8_t opencfw_em9305_enc_switch_3344b7[9] = {0,0,0,1,0,0,0,2,3};
