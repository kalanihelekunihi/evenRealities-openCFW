#ifndef OPENCFW_TOUCH_EXTENDED_ROWS_H
#define OPENCFW_TOUCH_EXTENDED_ROWS_H
#include <stdint.h>
/* Nonzero size/capacity, valid stable context/provider, bounded row storage.
 * Three history helpers and SROM remain test boundaries; offline module only. */
uint32_t touch_extended_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *context);
uint8_t touch_row_checksum(const uint8_t *row,uint32_t size); /* row+1, size-4 */
#endif
