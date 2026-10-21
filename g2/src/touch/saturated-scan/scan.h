#ifndef TOUCH_SATURATED_SCAN_OFFLINE_H
#define TOUCH_SATURATED_SCAN_OFFLINE_H
#include <stdint.h>
typedef uint32_t (*touch_mode_switch)(uint32_t,uint8_t *);
/* Selected actual widgets types2/6, mode0; excludes type7 alternate-frame ABI.
 * Transition remains explicit adapter, not reconstructed hardware lifecycle. */
uint32_t touch_execute_saturated(uint32_t *out,uint32_t id,uint32_t slot,uint8_t *context,touch_mode_switch transition);
#endif
