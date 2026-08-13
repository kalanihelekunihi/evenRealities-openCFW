#ifndef OPENR1_R1_PLATFORM_H
#define OPENR1_R1_PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    bool (*read_accelerometer)(int16_t xyz[3]);
    bool (*read_optical)(uint32_t *green, uint32_t *red, uint32_t *infrared);
    bool (*read_temperature)(int16_t *centi_celsius);
    bool (*flash_read)(uint32_t offset, uint8_t *output, size_t length);
    bool (*flash_write)(uint32_t offset, const uint8_t *input, size_t length);
    uint32_t (*unix_seconds)(void);
} r1_platform;

#endif

