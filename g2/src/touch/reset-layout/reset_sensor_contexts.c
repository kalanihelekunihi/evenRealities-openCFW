/* SPDX-License-Identifier: MIT
 * Nine typed ten-byte sensor contexts at RAM200005fc, ROMb6c8.
 * CapSense v6 fifth-generation LP sensor ABI; native consumers use stride10,
 * status byte6, raw/baseline/difference halfwords0/2/4. The product ROM widget
 * descriptors bind4+4+1 sensors at200005fc/20000624/2000064c respectively.
 * CDAC compensation fields are authenticated product tuning values.
 */
#include <stdint.h>
#include <stddef.h>
#include "reset_sensor_contexts.h"
touch_reset_sensor_context touch_reset_sensors[9]
 __attribute__((section(".touch_init.sensor_contexts"),used))={
 {.cdacComp=162u},{.cdacComp=32u},{.cdacComp=32u},{.cdacComp=32u},
 {.cdacComp=192u},{.cdacComp=246u},{.cdacComp=245u},{.cdacComp=191u},
 {.cdacComp=2u}
};
