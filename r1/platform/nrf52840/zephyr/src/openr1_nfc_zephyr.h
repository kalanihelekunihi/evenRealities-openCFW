#ifndef OPENR1_NFC_ZEPHYR_H
#define OPENR1_NFC_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    bool (*acquire_power)(void *context);
    void (*release_power)(void *context);
    bool (*acquire_dock_bus)(void *context);
    void (*release_dock_bus)(void *context);
} openr1_nfc_zephyr_resource_ops;

typedef void (*openr1_nfc_zephyr_frame_handler)(
    void *context, const uint8_t *bytes, size_t length);

int openr1_nfc_zephyr_initialize(void);
int openr1_nfc_zephyr_bind_resources(
    const openr1_nfc_zephyr_resource_ops *operations, void *context);
int openr1_nfc_zephyr_set_frame_handler(
    openr1_nfc_zephyr_frame_handler handler, void *context);
int openr1_nfc_zephyr_set_enabled(bool enabled);
bool openr1_nfc_zephyr_is_provisioned(void);
bool openr1_nfc_zephyr_is_active(void);
uint8_t openr1_nfc_zephyr_ic_reference(void);
uint32_t openr1_nfc_zephyr_last_error(void);

#endif
