#include <stddef.h>
#include "/Users/kalani/Repo/evenRealities-openCFW/vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/drivers/src/nrfx_gpiote.c"
_Static_assert(NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS==8,"low power slots");
_Static_assert(sizeof(gpiote_control_block_t)==128,"control extent");
_Static_assert(offsetof(gpiote_control_block_t,pin_assignments)==64,"assignments");
_Static_assert(offsetof(gpiote_control_block_t,port_handlers_pins)==112,"port handlers");
_Static_assert(offsetof(gpiote_control_block_t,configured_pins)==120,"configured pins");
_Static_assert(offsetof(gpiote_control_block_t,state)==126,"state");
