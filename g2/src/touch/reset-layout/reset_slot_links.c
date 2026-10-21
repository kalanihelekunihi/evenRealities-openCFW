/* SPDX-License-Identifier: MIT
 * Source relocations for the two descriptor pointers in the reset-copied
 * CapSense context at RAM 0x2000051c and 0x20000520.
 */
#include <stdint.h>
typedef struct { uint16_t widget; uint16_t sensor; } touch_reset_sensor_descriptor;
extern touch_reset_sensor_descriptor touch_reset_active_descriptors[4];
extern touch_reset_sensor_descriptor touch_reset_lp_descriptors[4];

touch_reset_sensor_descriptor *touch_reset_active_slots
    __attribute__((section(".touch_init.active_slot_link"),used)) =
    touch_reset_active_descriptors;
touch_reset_sensor_descriptor *touch_reset_lp_slots
    __attribute__((section(".touch_init.lp_slot_link"),used)) =
    touch_reset_lp_descriptors;
