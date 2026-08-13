#ifndef OPENR1_I2C5_RESOURCES_H
#define OPENR1_I2C5_RESOURCES_H

#include <stdbool.h>

#include "sdk_errors.h"

/*
 * Board-local ownership gate for the shared P1.11/P1.14 conductor pair.
 * A future licensed YHM2710 provider must take this same lease; this interface
 * intentionally exposes no bus transfer or register operation.
 */
ret_code_t openr1_i2c5_resources_initialize(void);
bool openr1_i2c5_try_acquire(void);
void openr1_i2c5_release(void);

#endif
