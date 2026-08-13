#include "openr1/r1_crc.h"

uint32_t r1_crc32_castagnoli(const uint8_t *bytes, size_t length) {
    uint32_t crc = 0u;
    for (size_t index = 0u; index < length; ++index) {
        crc ^= (uint32_t)bytes[index] << 24u;
        for (uint8_t bit = 0u; bit < 8u; ++bit) {
            crc = (crc & UINT32_C(0x80000000)) != 0u
                ? (crc << 1u) ^ UINT32_C(0x1edc6f41)
                : crc << 1u;
        }
    }
    return crc;
}

uint16_t r1_crc16_ccitt(const uint8_t *bytes, size_t length) {
    uint16_t crc = UINT16_C(0xffff);
    for (size_t index = 0u; index < length; ++index) {
        crc = (uint16_t)((crc >> 8u) | (uint16_t)(crc << 8u));
        crc ^= bytes[index];
        crc ^= (uint16_t)((crc & UINT16_C(0x00ff)) >> 4u);
        crc ^= (uint16_t)(crc << 12u);
        crc ^= (uint16_t)((crc & UINT16_C(0x00ff)) << 5u);
    }
    return crc;
}

uint16_t r1_crc16_modbus(const uint8_t *bytes, size_t length) {
    uint16_t crc = UINT16_C(0xffff);
    for (size_t index = 0u; index < length; ++index) {
        crc ^= bytes[index];
        for (uint8_t bit = 0u; bit < 8u; ++bit) {
            crc = (crc & 1u) != 0u
                ? (uint16_t)((crc >> 1u) ^ UINT16_C(0xa001))
                : (uint16_t)(crc >> 1u);
        }
    }
    return crc;
}

