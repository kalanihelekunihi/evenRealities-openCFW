#ifndef OPENR1_STORAGE_ZEPHYR_H
#define OPENR1_STORAGE_ZEPHYR_H

#include <stdint.h>

#include "openr1/r1_storage.h"

int openr1_storage_zephyr_initialize(void);
r1_flash *openr1_storage_zephyr_flash(void);
bool openr1_storage_zephyr_ep_scan(r1_ep_scan_result *result);
bool openr1_storage_zephyr_log_append(
    const uint8_t *input, size_t length);
uint16_t openr1_storage_zephyr_log_sector_count(void);
bool openr1_storage_zephyr_structured_log_typed(
    uint8_t severity, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count);
bool openr1_storage_zephyr_structured_log_format(
    uint8_t severity, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count);
size_t openr1_storage_zephyr_structured_log_count(void);
bool openr1_storage_zephyr_structured_log_service(uint32_t now_tick);
bool openr1_storage_zephyr_diagnostic_export_begin(
    r1_log_export_info *info);
bool openr1_storage_zephyr_diagnostic_export_read(
    uint32_t offset, uint8_t *output, size_t length);
void openr1_storage_zephyr_diagnostic_export_finish(void);
bool openr1_storage_zephyr_diagnostic_export_active(void);
uint32_t openr1_storage_zephyr_start_address(void);
uint32_t openr1_storage_zephyr_end_address(void);

#endif
