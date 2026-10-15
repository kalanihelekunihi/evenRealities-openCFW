#ifndef R1_STOCK_CHECKSUMS_H
#define R1_STOCK_CHECKSUMS_H
#include <stdint.h>
/* Stock 0x5D87C, 0x5D8A4, 0x5D8CC. Valid readable buffers are required;
 * crc32 state must be writable even for an empty input, as in stock. */
uint16_t r1_stock_crc16_modbus(const uint8_t *bytes, uint32_t length);
void r1_stock_crc32_update(const uint8_t *bytes, uint32_t length, uint32_t *state);
uint32_t r1_stock_hash131(const uint8_t *bytes, uint32_t length);
#endif
