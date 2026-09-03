/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_COMPRESS_LOG_CORE_H
#define OPEN_CFW_COMPRESS_LOG_CORE_H

#include <stdarg.h>
#include <stdint.h>

struct open_cfw_compress_log_ring {
    unsigned char *buffer;
    uint32_t capacity;
    uint32_t read_offset;
    uint32_t write_offset;
};

void open_cfw_compress_log_mutex_init(void);
int open_cfw_compress_log_ring_read_locked(void *destination, uint16_t size);
int open_cfw_compress_log_get_all_buffer(void *destination, uint16_t size);
int open_cfw_compress_log_ring_write(const void *source, uint16_t size);
void open_cfw_compress_log_encode_record(
    uint32_t metadata,
    const char *format,
    va_list *arguments
);
void open_cfw_compress_log_output(
    uint32_t metadata,
    uintptr_t identity,
    const char *format,
    ...
);
void open_cfw_compress_log_periodic_sync(void);
void open_cfw_compress_log_force_sync(void);

#endif
