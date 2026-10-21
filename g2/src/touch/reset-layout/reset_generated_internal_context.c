/* SPDX-License-Identifier: MIT
 * Source-owned LP internal context at RAM20000c50. Reset zero descriptor
 * clears this entire120-byte typed object; no retained-value fabrication.
 * Final whole-firmware scatter/reachability remains a separate obligation.
 */
#include "reset_generated_internal_context.h"
struct touch_internal_context_lp touch_generated_internal_context
 __attribute__((section(".touch_bss.internal_context"),used));
