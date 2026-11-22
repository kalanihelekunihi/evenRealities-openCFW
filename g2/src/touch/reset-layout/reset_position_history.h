/* SPDX-License-Identifier: MIT
 * Recovered slider position-history header and one record.
 */
#ifndef G2_TOUCH_RESET_POSITION_HISTORY_H
#define G2_TOUCH_RESET_POSITION_HISTORY_H

#include <stdint.h>
#include <stddef.h>

typedef struct { uint16_t x,y,z,id; } touch_position_history_record;
typedef struct { touch_position_history_record *position; uint8_t count; } touch_position_history_header;
_Static_assert(sizeof(touch_position_history_record)==8,"position ABI");
_Static_assert(sizeof(touch_position_history_header)==8,"history header ABI");
_Static_assert(offsetof(touch_position_history_header,count)==4,"history count ABI");

extern touch_position_history_record touch_slider_history_position;
extern touch_position_history_header touch_reset_position_history;

#endif
