#ifndef OPENR1_STORAGE_ZEPHYR_H
#define OPENR1_STORAGE_ZEPHYR_H

#include <stdint.h>

#include "openr1/r1_storage.h"

int openr1_storage_zephyr_initialize(void);
r1_flash *openr1_storage_zephyr_flash(void);
uint32_t openr1_storage_zephyr_start_address(void);
uint32_t openr1_storage_zephyr_end_address(void);

#endif
