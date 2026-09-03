/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_COMPRESS_LOG_PORT_H
#define OPEN_CFW_COMPRESS_LOG_PORT_H

#include <stdint.h>

struct open_cfw_compress_log_manager {
    uint32_t magic;
    uint8_t active_file;
    uint8_t oldest_file;
    uint8_t file_count;
    uint8_t reserved;
    uint32_t current_offset;
};

void open_cfw_compress_log_path_format(
    uint8_t file_index,
    unsigned char *path,
    unsigned int capacity
);
int open_cfw_compress_log_file_exists(uint8_t file_index);
int open_cfw_compress_log_manager_reconcile(void);
int open_cfw_compress_log_manager_load(void);
int open_cfw_compress_log_manager_save(void);
void open_cfw_compress_log_file_remove(uint8_t file_index);
int open_cfw_compress_log_write_file_version_header(void *stream);
void open_cfw_compress_log_rotate_file(void);
void open_cfw_compress_log_sync_to_files(
    const unsigned char *data,
    unsigned int size
);
void open_cfw_compress_log_export_timeout_callback(void *argument);
void open_cfw_compress_log_export_notify(uint8_t active);
uint8_t open_cfw_compress_log_export_active(void);

#endif
