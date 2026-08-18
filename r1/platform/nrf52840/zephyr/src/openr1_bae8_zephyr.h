#ifndef OPENR1_BAE8_ZEPHYR_H
#define OPENR1_BAE8_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_storage.h"

int openr1_bae8_zephyr_initialize(void);
int openr1_bae8_zephyr_start_advertising(void);
int openr1_bae8_zephyr_revoke_owner(void);
bool openr1_bae8_zephyr_diagnostic_export_begin(
    uint16_t connection, r1_log_export_info *info);
bool openr1_bae8_zephyr_diagnostic_export_read(
    uint16_t connection, uint32_t offset, uint8_t *output, size_t length);
void openr1_bae8_zephyr_diagnostic_export_finish(uint16_t connection);
uint32_t openr1_bae8_zephyr_remove_ring_failures(void);

#endif
