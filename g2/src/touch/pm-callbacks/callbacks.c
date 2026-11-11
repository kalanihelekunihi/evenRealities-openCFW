/* SPDX-License-Identifier: MIT
 * ABI guard for reset-copied PM callback descriptors. The runtime
 * registration, callback execution and deep sleep are supplied by the pinned
 * Infineon PDL C source, cy_syspm.c.
 */
#include "callbacks.h"
#include <stddef.h>

_Static_assert(sizeof(touch_pm_callback) == 28u, "touch PM callback ABI");
_Static_assert(sizeof(touch_pm_params) == 8u, "touch PM params ABI");
_Static_assert(offsetof(touch_pm_callback, params) == 12u, "touch PM params offset");
_Static_assert(offsetof(touch_pm_callback, order) == 24u, "touch PM order offset");
