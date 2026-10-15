/* Recovered R1 2.2.6.0009 routines, not original vendor source.
 * Contracts: application disassembly at 0x5D87C, 0x5D8A4 and 0x5D8CC.
 * The tables are generated from named polynomials, authenticated against stock
 * by verify_stock_checksums.py. No retained executable bytes are used here. */
#include "r1_stock_checksums.h"
#include "stock_checksum_tables.inc"

uint16_t r1_stock_crc16_modbus(const uint8_t *bytes, uint32_t length) {
    uint16_t crc = UINT16_C(0xffff);
    for (uint32_t i = 0; i < length; ++i)
        crc = (uint16_t)(r1_stock_crc16_table[(crc ^ bytes[i]) & 255u] ^ (crc >> 8));
    return crc;
}

void r1_stock_crc32_update(const uint8_t *bytes, uint32_t length, uint32_t *state) {
    uint32_t crc = *state;
    for (uint32_t i = 0; i < length; ++i)
        crc = r1_stock_crc32_table[bytes[i] ^ (crc >> 24)] ^ (crc << 8);
    *state = crc;
}

uint32_t r1_stock_hash131(const uint8_t *bytes, uint32_t length) {
    uint32_t hash = 0;
    for (uint32_t i = 0; i < length; ++i)
        hash = hash * 131u + bytes[i];
    return hash;
}
