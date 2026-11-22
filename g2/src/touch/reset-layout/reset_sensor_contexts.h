/* SPDX-License-Identifier: MIT
 * Recovered 10-byte CapSense LP sensor runtime contexts.
 */
#ifndef G2_TOUCH_RESET_SENSOR_CONTEXTS_H
#define G2_TOUCH_RESET_SENSOR_CONTEXTS_H

#include <stdint.h>
#include <stddef.h>

typedef struct {
 uint16_t raw,bsln,diff;
 uint8_t status,negBslnRstCnt,bslnExt,cdacComp;
} touch_reset_sensor_context;

_Static_assert(sizeof(touch_reset_sensor_context)==10u,"native sensor stride");
_Static_assert(offsetof(touch_reset_sensor_context,status)==6u,"native status byte");
_Static_assert(offsetof(touch_reset_sensor_context,cdacComp)==9u,"vendor LP CDAC");

extern touch_reset_sensor_context touch_reset_sensors[9];

#endif
