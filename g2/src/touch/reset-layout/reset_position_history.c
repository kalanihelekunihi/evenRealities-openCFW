/* SPDX-License-Identifier: MIT
 * Native widget1 descriptor ROMb188+60 points to header RAM20000848.
 * Filter4a2a consumes its position pointer+0 and count byte+4.
 * Centroid48cc outputs zero/one position for product centroidConfig&3==1;
 * posFilterConfig00800102 requests one 8-byte record per position.
 * Types agree with CapSense v6 cy_stc_capsense_position_t/touch_t.
 * The selected single-position path owns this record. Wider generated buffer
 * allocation and other configurations remain unqualified.
 */
#include <stdint.h>
#include <stddef.h>
#include "reset_position_history.h"
touch_position_history_record touch_slider_history_position
    __attribute__((section(".touch_bss.slider_history_position"),used));
touch_position_history_header touch_reset_position_history
    __attribute__((section(".touch_init.position_history"),used)) = {
    .position=&touch_slider_history_position,.count=0u,
};
