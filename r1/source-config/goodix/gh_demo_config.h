#ifndef R1_GH3X2X_DEMO_CONFIG_WRAPPER_H
#define R1_GH3X2X_DEMO_CONFIG_WRAPPER_H

/*
 * openR1 configuration overlay for the Goodix GH3X2X democode.
 *
 * The democode ships two driver build modes.  With the stock configuration
 * the FIFO read path (GH3X2X_ReadFifodata / GH3X2X_CheckRawdataBuf /
 * GH3X2X_CalRawdataBuf) comes from the binary-only DrvLib archive, which
 * cannot be linked on the Cortex-M4F target (Armv8-M.mainline objects).
 * The R1 firmware contains these bodies compiled from
 * driver/src/gh_drv_control.c, so the openR1 build selects the all-source
 * mode instead.  Only driver TUs reference this macro; kernel TUs include
 * their sibling vendor copy of this header and are unaffected.
 *
 * This file is found first via the include path; #include_next chains to
 * the pinned vendor configuration for every other setting.
 */

#include_next "gh_demo_config.h"

#undef __DRIVER_OPEN_ALL_SOURCE__
#define __DRIVER_OPEN_ALL_SOURCE__ (1)

#endif
