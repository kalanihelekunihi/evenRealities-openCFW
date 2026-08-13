#ifndef OPENR1_NFC_H
#define OPENR1_NFC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "sdk_errors.h"

typedef struct {
    bool (*acquire_power)(void *context);
    void (*release_power)(void *context);
    bool (*acquire_i2c5)(void *context);
    void (*release_i2c5)(void *context);
} openr1_nfc_resource_ops;

typedef void (*openr1_nfc_frame_handler)(void *context, const uint8_t *bytes,
                                         size_t length);

ret_code_t openr1_nfc_initialize(void);
ret_code_t openr1_nfc_bind_resources(
    const openr1_nfc_resource_ops *operations, void *context);
ret_code_t openr1_nfc_set_frame_handler(openr1_nfc_frame_handler handler,
                                        void *context);
ret_code_t openr1_nfc_set_enabled(bool enabled);
bool openr1_nfc_is_provisioned(void);
bool openr1_nfc_is_active(void);
uint8_t openr1_nfc_ic_reference(void);
uint32_t openr1_nfc_last_error(void);

#endif
