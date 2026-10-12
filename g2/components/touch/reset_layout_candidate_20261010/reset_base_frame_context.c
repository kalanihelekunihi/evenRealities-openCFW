/* SPDX-License-Identifier: MIT
 * Product MSCLP base-frame runtime at RAM 0x20000b38.
 * Pinned PDL cy_msclp.h gives the exact 256-byte typed configuration,
 * ending where the 24-byte active-scan object starts at 0x20000c38.
 * Authenticated CRT zero descriptor covers the entire region.
 */
#include "reset_base_frame_context.h"
#include <stddef.h>
_Static_assert(sizeof(touch_msclp_base_config)==256u,"MSCLP base frame ABI");
_Static_assert(offsetof(touch_msclp_base_config,mode)==144u,"MSCLP mode offset");
touch_msclp_base_config touch_generated_base_frame_context
 __attribute__((section(".bss.touch_base_frame_context"),used));
