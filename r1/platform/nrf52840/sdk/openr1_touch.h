#ifndef OPENR1_TOUCH_H
#define OPENR1_TOUCH_H

#include <stdbool.h>
#include <stdint.h>

#include "sdk_errors.h"

#include "openr1/r1_iqs7211e.h"

#define OPENR1_TOUCH_SOURCE_WEAR 0u
#define OPENR1_TOUCH_SOURCE_FACTORY 2u
#define OPENR1_TOUCH_POWER_CLIENT_BIT UINT8_C(2)
#define OPENR1_TOUCH_POWER_RELEASE_TICKS UINT32_C(0x800)

typedef struct {
    bool (*acquire)(void *context, uint8_t client_bit);
    bool (*release_after)(void *context, uint8_t client_bit,
                          uint32_t delay_ticks);
} openr1_touch_power_ops;

ret_code_t openr1_touch_initialize(void);
ret_code_t openr1_touch_bind_power(const openr1_touch_power_ops *operations,
                                   void *context);
ret_code_t openr1_touch_set_identity(r1_iqs7211e_layout layout,
                                     uint8_t ring_size);
ret_code_t openr1_touch_acquire(uint8_t source);
ret_code_t openr1_touch_release(uint8_t source);
ret_code_t openr1_touch_set_enabled(bool enabled);
bool openr1_touch_is_provisioned(void);
bool openr1_touch_is_active(void);
uint32_t openr1_touch_last_error(void);

#endif
