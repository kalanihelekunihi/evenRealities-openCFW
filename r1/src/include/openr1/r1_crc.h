#ifndef OPENR1_R1_CRC_H
#define OPENR1_R1_CRC_H

#include <stddef.h>
#include <stdint.h>

uint32_t r1_crc32_castagnoli(const uint8_t *bytes, size_t length);
uint32_t r1_crc32_castagnoli_update(
    uint32_t crc, const uint8_t *bytes, size_t length);
uint16_t r1_crc16_ccitt(const uint8_t *bytes, size_t length);
uint16_t r1_crc16_modbus(const uint8_t *bytes, size_t length);

#endif
