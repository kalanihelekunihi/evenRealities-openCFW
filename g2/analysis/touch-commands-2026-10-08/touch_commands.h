#ifndef OPENCFW_TOUCH_COMMANDS_H
#define OPENCFW_TOUCH_COMMANDS_H
#include <stdint.h>
enum touch_command {
 TOUCH_CMD_IDENTITY=1, TOUCH_CMD_DFU_REQUEST=2, TOUCH_CMD_SENSOR_VALUES=4,
 TOUCH_CMD_SAVE_BASELINE_REQUEST=5, TOUCH_CMD_BASELINE_VALUE=6,
 TOUCH_CMD_SET_GESTURE_PARAMETER=7, TOUCH_CMD_GESTURE_PARAMETER_VALUE=8
};
#define TOUCH_RESPONSE_CAPACITY 16u
#define TOUCH_ACK_TRAILER 0x17u /* observed byte; checksum meaning unproven */
static inline uint16_t touch_u16le(const uint8_t *p) { return (uint16_t)(p[0]|((uint16_t)p[1]<<8)); }
void app_event(uint32_t events);
void touch_deferred(void);
/* Bounded command4 reconstruction: widget1 count<=4, widget2 count<=1.
 * Shared static buffers require caller serialization; helpers are offline C,
 * not a complete firmware, flash provider, or device-safe patch. */
#endif
