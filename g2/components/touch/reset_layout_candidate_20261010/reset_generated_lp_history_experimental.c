/* SPDX-License-Identifier: MIT
 * Experimental capacity for the stock four-slot LP result window.
 * The native configuration yields 212 u16 values (424 bytes), with two
 * bytes remaining before the next known RAM object. The original generated
 * allocation size has not been established, so this unit is not selected.
 */
#include <stdint.h>

enum { TOUCH_STOCK_LP_HISTORY_WORDS = 212 };
uint16_t touch_generated_lp_history[TOUCH_STOCK_LP_HISTORY_WORDS]
    __attribute__((section(".bss.touch_lp_history"), used));

_Static_assert(sizeof(touch_generated_lp_history) == 424u,
               "stock four-slot LP window");
