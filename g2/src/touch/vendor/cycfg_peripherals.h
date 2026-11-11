/* SPDX-License-Identifier: MIT
 * Peripherals header for CapSense sensing_lp.
 * Evidence (wave11): the only users of CY_MSCLP0_EXT_FRM_START_PORT/PIN are in
 * infineon-capsense-v5 cy_capsense_sensing_lp.c:3121, inside
 * #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN). That flag is
 * CY_CAPSENSE_DISABLE (vendor/cycfg_capsense_defines.h:57), so no definition is
 * needed and the former fill-in defines were dropped.
 */
#ifndef CYCFG_PERIPHERALS_H
#define CYCFG_PERIPHERALS_H
#include <stdint.h>
#endif
