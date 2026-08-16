#ifndef OPENR1_TWIM1_ZEPHYR_H
#define OPENR1_TWIM1_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    OPENR1_TWIM1_ZEPHYR_OWNER_NONE = 0,
    OPENR1_TWIM1_ZEPHYR_OWNER_MOTION,
    OPENR1_TWIM1_ZEPHYR_OWNER_NFC,
} openr1_twim1_zephyr_owner;

int openr1_twim1_zephyr_initialize(void);
int openr1_twim1_zephyr_acquire(openr1_twim1_zephyr_owner owner);
int openr1_twim1_zephyr_release(openr1_twim1_zephyr_owner owner);
int openr1_twim1_zephyr_write(openr1_twim1_zephyr_owner owner,
                              uint16_t address, const uint8_t *bytes,
                              size_t length);
int openr1_twim1_zephyr_read(openr1_twim1_zephyr_owner owner,
                             uint16_t address, uint8_t *bytes,
                             size_t length);
int openr1_twim1_zephyr_write_read(openr1_twim1_zephyr_owner owner,
                                   uint16_t address,
                                   const uint8_t *write_bytes,
                                   size_t write_length, uint8_t *read_bytes,
                                   size_t read_length);
openr1_twim1_zephyr_owner openr1_twim1_zephyr_current_owner(void);

#endif
