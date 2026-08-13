#ifndef OPENR1_GATT_H
#define OPENR1_GATT_H

#include <stdint.h>

uint32_t openr1_gatt_initialize(void);
uint16_t openr1_gatt_effective_mtu(uint16_t connection);
uint8_t openr1_gatt_effective_data_length(uint16_t connection);
uint32_t openr1_gatt_last_error(void);

#endif
