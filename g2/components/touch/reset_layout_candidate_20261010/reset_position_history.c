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
typedef struct { uint16_t x,y,z,id; } touch_position_history_record;
typedef struct { touch_position_history_record *position; uint8_t count; } touch_position_history_header;
_Static_assert(sizeof(touch_position_history_record)==8,"position ABI");
_Static_assert(sizeof(touch_position_history_header)==8,"history header ABI");
_Static_assert(offsetof(touch_position_history_header,count)==4,"history count ABI");
touch_position_history_record touch_slider_history_position
    __attribute__((section(".touch_bss.slider_history_position"),used));
touch_position_history_header touch_reset_position_history
    __attribute__((section(".touch_init.position_history"),used)) = {
    .position=&touch_slider_history_position,.count=0u,
};
