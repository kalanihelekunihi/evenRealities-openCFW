#include <stdint.h>
/* Extents authenticated by exact SDK dispatcher relocation binding; runtime ownership remains gated. */
extern void opencfw_em9305_ecu_callback_315a84(void);
extern void opencfw_em9305_ecu_callback_315ff4(void);
extern void opencfw_em9305_ecu_callback_316298(void);
extern void opencfw_em9305_ecu_callback_315f48(void);
void (*const opencfw_em9305_ecu_callbacks_335378[6])(void) = {
 opencfw_em9305_ecu_callback_315a84,opencfw_em9305_ecu_callback_315ff4,0,0,
 opencfw_em9305_ecu_callback_316298,opencfw_em9305_ecu_callback_315f48
};
const uint8_t opencfw_em9305_ecu_transitions_335390[6]={1,0,0,1,0,0};
