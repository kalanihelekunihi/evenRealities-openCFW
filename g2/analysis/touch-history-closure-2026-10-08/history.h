#ifndef OPENCFW_TOUCH_HISTORY_H
#define OPENCFW_TOUCH_HISTORY_H
#include <stdint.h>
uint32_t touch_define_last(uint8_t *context);
uint32_t touch_integrity(uint32_t *sequence,uint8_t *context);
uint32_t touch_history(uint8_t *row,uint32_t address,uint8_t *context);
uint32_t touch_merge(uint8_t *row,uint32_t address,uint8_t *context);
/* Valid row geometry, bounded payload headers and stable provider table.
 * Raw unsigned sequence ordering is preserved, not wrap-safe newest ordering. */
#endif
