/* Reuse recovered partition configuration with a mutable native RAM device. */
#ifndef R1_NATIVE_FAL_CFG_H
#define R1_NATIVE_FAL_CFG_H
/* The recovered generic configuration exports a const view. Keep that unused
 * declaration distinct while retaining its table macros verbatim. Macro bodies
 * resolve r1_fal_flash_device after the temporary rename is removed. */
#define r1_fal_flash_device r1_fal_flash_device_readonly_view
#include "../../../config-recovered/fal_cfg.h"
#undef r1_fal_flash_device
extern struct fal_flash_dev r1_fal_flash_device;
#endif
