#ifndef OPENR1_TOUCH_ZEPHYR_H
#define OPENR1_TOUCH_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_iqs7211e.h"

#define OPENR1_TOUCH_ZEPHYR_SOURCE_WEAR 0u
#define OPENR1_TOUCH_ZEPHYR_SOURCE_FACTORY 2u
#define OPENR1_TOUCH_ZEPHYR_POWER_CLIENT_BIT UINT8_C(2)
#define OPENR1_TOUCH_ZEPHYR_POWER_RELEASE_TICKS UINT32_C(0x800)

typedef struct {
    bool (*acquire)(void *context, uint8_t client_bit);
    bool (*release_after)(void *context, uint8_t client_bit,
                          uint32_t delay_ticks);
} openr1_touch_zephyr_power_ops;

int openr1_touch_zephyr_initialize(void);
int openr1_touch_zephyr_bind_power(
    const openr1_touch_zephyr_power_ops *operations, void *context);
int openr1_touch_zephyr_set_identity(r1_iqs7211e_layout layout,
                                     uint8_t ring_size);
int openr1_touch_zephyr_acquire(uint8_t source);
int openr1_touch_zephyr_release(uint8_t source);
int openr1_touch_zephyr_set_enabled(bool enabled);
void openr1_touch_zephyr_set_sample_callback(
    r1_iqs7211e_sample_callback callback, void *context);
bool openr1_touch_zephyr_is_provisioned(void);
bool openr1_touch_zephyr_is_active(void);
uint32_t openr1_touch_zephyr_last_error(void);

#endif
