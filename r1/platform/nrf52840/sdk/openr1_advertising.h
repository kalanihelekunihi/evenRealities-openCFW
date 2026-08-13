#ifndef OPENR1_ADVERTISING_H
#define OPENR1_ADVERTISING_H

#include <stdbool.h>
#include <stdint.h>

uint32_t openr1_advertising_initialize(bool factory_mode,
                                        const uint8_t product_serial[15],
                                        bool serial_provisioned);
uint32_t openr1_advertising_start(void);
uint32_t openr1_advertising_stop(void);
uint32_t openr1_advertising_last_error(void);

#endif
