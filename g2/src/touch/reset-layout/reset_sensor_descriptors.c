/* SPDX-License-Identifier: MIT
 * Four low-power and five active CapSense slot descriptors in the reset copy.
 * The low-power descriptors at 0x20000808 are consumed by history acquisition;
 * the active descriptors immediately follow at 0x20000818 through 0x2000082b. Each row is a
 * widget index followed by a sensor index, as observed by the slot readers.
 */
#include <stdint.h>
typedef struct {
    uint16_t widget;
    uint16_t sensor;
} touch_reset_sensor_descriptor;
_Static_assert(sizeof(touch_reset_sensor_descriptor)==4,"sensor row ABI");

touch_reset_sensor_descriptor touch_reset_lp_descriptors[4]
    __attribute__((section(".touch_init.lp_sensor_descriptors"),used)) = {
    {0u,0u},{0u,1u},{0u,2u},{0u,3u},
};

touch_reset_sensor_descriptor touch_reset_active_descriptors[5]
    __attribute__((section(".touch_init.active_sensor_descriptors"),used)) = {
    {1u,0u},{1u,1u},{1u,2u},{1u,3u},{2u,0u},
};
