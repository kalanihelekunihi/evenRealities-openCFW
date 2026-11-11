/* SPDX-License-Identifier: MIT
 * Generated-config stand-in for CapSense middleware. Points at the
 * reconstructed touch CapSense context until design.cycapsense is emitted.
 */
#ifndef CYCFG_CAPSENSE_H
#define CYCFG_CAPSENSE_H

#include "cycfg_capsense_defines.h"
#include "cy_capsense_structure.h"

/* Product context lives in reset_capsense_context.c (touch_reset_capsense_context). */
extern cy_stc_capsense_context_t touch_reset_capsense_context;
#define cy_capsense_context touch_reset_capsense_context

#endif
