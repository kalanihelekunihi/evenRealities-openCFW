/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the complete G2 2.2.6.10 compact-log file
 * port at 0x0044A474...0x0044A9B3.  EasyLogger calls in the stock object are
 * diagnostic-only and are intentionally omitted.  Persistence, rotation,
 * version-header, export-state, and delayed-timeout behavior are preserved.
 */

#include "compress_log_port.h"

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_COMPRESS_LOG_FILE_COUNT 5u
#define OPEN_CFW_COMPRESS_LOG_MAX_FILE_BYTES 512000u
#define OPEN_CFW_COMPRESS_LOG_MANAGER_MAGIC 0x4c4d4752u
#define OPEN_CFW_COMPRESS_LOG_EXPORT_TIMEOUT_TICKS 120000u
#define OPEN_CFW_COMPRESS_LOG_PATH_CAPACITY 48u

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(struct open_cfw_compress_log_manager) == 12u,
    "G2 compact-log manager ABI changed");
_Static_assert(offsetof(struct open_cfw_compress_log_manager, active_file) == 4u,
    "G2 compact-log active-file offset changed");
_Static_assert(offsetof(struct open_cfw_compress_log_manager, current_offset) == 8u,
    "G2 compact-log current-offset ABI changed");
#endif

#ifndef OPEN_CFW_COMPRESS_LOG_MANAGER
#define OPEN_CFW_COMPRESS_LOG_MANAGER \
    (*(volatile struct open_cfw_compress_log_manager *)(uintptr_t)0x20073f9cu)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_INITIALIZED
#define OPEN_CFW_COMPRESS_LOG_INITIALIZED \
    (*(volatile uint8_t *)(uintptr_t)0x20074fa0u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_EXPORT_STATE
#define OPEN_CFW_COMPRESS_LOG_EXPORT_STATE \
    (*(volatile uint8_t *)(uintptr_t)0x20074fa1u)
#endif

#ifndef OPEN_CFW_COMPRESS_LOG_FILE_PATH_FORMAT
#define OPEN_CFW_COMPRESS_LOG_FILE_PATH_FORMAT \
    ((const unsigned char *)(uintptr_t)0x0076a134u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MANAGER_PATH
#define OPEN_CFW_COMPRESS_LOG_MANAGER_PATH \
    ((const unsigned char *)(uintptr_t)0x0076a150u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MODE_READ
#define OPEN_CFW_COMPRESS_LOG_MODE_READ \
    ((const char *)(uintptr_t)0x0044a790u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MODE_WRITE
#define OPEN_CFW_COMPRESS_LOG_MODE_WRITE \
    ((const char *)(uintptr_t)0x0044a794u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MODE_UPDATE
#define OPEN_CFW_COMPRESS_LOG_MODE_UPDATE \
    ((const char *)(uintptr_t)0x0044a8fcu)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MODE_UPDATE_CREATE
#define OPEN_CFW_COMPRESS_LOG_MODE_UPDATE_CREATE \
    ((const char *)(uintptr_t)0x0044a900u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_VERSION_FORMAT
#define OPEN_CFW_COMPRESS_LOG_VERSION_FORMAT \
    ((const unsigned char *)(uintptr_t)0x00775aacu)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_VERSION
#define OPEN_CFW_COMPRESS_LOG_VERSION \
    ((const char *)(uintptr_t)0x0078a640u)
#endif

#ifndef OPEN_CFW_COMPRESS_LOG_FILE_OPEN
void *open_cfw_file_open(const void *path, const char *mode);
#define OPEN_CFW_COMPRESS_LOG_FILE_OPEN(path, mode) \
    open_cfw_file_open((path), (mode))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILE_CLOSE
int open_cfw_file_close(void *stream);
#define OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream) \
    open_cfw_file_close(stream)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILE_READ
unsigned int open_cfw_file_read(
    void *buffer,
    unsigned int size,
    unsigned int count,
    void *stream
);
#define OPEN_CFW_COMPRESS_LOG_FILE_READ(buffer, size, count, stream) \
    open_cfw_file_read((buffer), (size), (count), (stream))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILE_WRITE
unsigned int open_cfw_file_write(
    const void *buffer,
    unsigned int size,
    unsigned int count,
    void *stream
);
#define OPEN_CFW_COMPRESS_LOG_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_file_write((buffer), (size), (count), (stream))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILE_SEEK
int open_cfw_file_seek(void *stream, int offset, unsigned int origin);
#define OPEN_CFW_COMPRESS_LOG_FILE_SEEK(stream, offset, origin) \
    open_cfw_file_seek((stream), (offset), (origin))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILE_REMOVE
int open_cfw_file_remove(const void *path);
#define OPEN_CFW_COMPRESS_LOG_FILE_REMOVE(path) open_cfw_file_remove(path)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_SNPRINTF
int open_cfw_runtime_snprintf(
    unsigned char *buffer,
    unsigned int count,
    const unsigned char *format,
    ...
);
#define OPEN_CFW_COMPRESS_LOG_SNPRINTF(...) \
    open_cfw_runtime_snprintf(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_PUSH_DELAYED
void open_cfw_event_loop_push_delayed(
    void (*callback)(void *),
    void *argument,
    unsigned int delay
);
#define OPEN_CFW_COMPRESS_LOG_PUSH_DELAYED(callback, argument, delay) \
    open_cfw_event_loop_push_delayed((callback), (argument), (delay))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_REMOVE_DELAYED
unsigned char open_cfw_event_loop_remove_delayed(void (*callback)(void *));
#define OPEN_CFW_COMPRESS_LOG_REMOVE_DELAYED(callback) \
    open_cfw_event_loop_remove_delayed(callback)
#endif

#if !defined(OPEN_CFW_COMPRESS_LOG_PATH_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_EXISTS_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_RECONCILE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_LOAD_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_SAVE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_REMOVE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_HEADER_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_ROTATE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_SYNC_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_TIMEOUT_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_NOTIFY_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_ACTIVE_ONLY)
#define OPEN_CFW_COMPRESS_LOG_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_PATH_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_path_format(
    uint8_t file_index,
    unsigned char *path,
    unsigned int capacity
)
{
    (void)OPEN_CFW_COMPRESS_LOG_SNPRINTF(
        path,
        capacity,
        OPEN_CFW_COMPRESS_LOG_FILE_PATH_FORMAT,
        (unsigned int)file_index
    );
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_EXISTS_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_file_exists(uint8_t file_index)
{
    unsigned char path[OPEN_CFW_COMPRESS_LOG_PATH_CAPACITY];
    void *stream;

    open_cfw_compress_log_path_format(file_index, path, sizeof(path));
    stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(path, OPEN_CFW_COMPRESS_LOG_MODE_READ);
    if (stream == NULL) {
        return 0;
    }
    (void)OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream);
    return 1;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_RECONCILE_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_manager_reconcile(void)
{
    uint8_t index;
    uint8_t present = 0u;
    uint8_t oldest = OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file;
    uint8_t found = 0u;

    if (OPEN_CFW_COMPRESS_LOG_MANAGER.file_count == 0u) {
        return 0;
    }
    if (open_cfw_compress_log_file_exists(
            OPEN_CFW_COMPRESS_LOG_MANAGER.active_file) == 0) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset = 0u;
    }
    for (index = 0u; index < OPEN_CFW_COMPRESS_LOG_MANAGER.file_count; ++index) {
        uint8_t slot = (uint8_t)(
            (OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file + index) %
            OPEN_CFW_COMPRESS_LOG_FILE_COUNT
        );
        if (open_cfw_compress_log_file_exists(slot) != 0) {
            if (found == 0u) {
                found = 1u;
                oldest = slot;
            }
            ++present;
        }
    }
    if (present != OPEN_CFW_COMPRESS_LOG_MANAGER.file_count ||
        oldest != OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file = oldest;
        OPEN_CFW_COMPRESS_LOG_MANAGER.file_count = present;
        return open_cfw_compress_log_manager_save();
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_LOAD_ONLY)
static void open_cfw_compress_log_manager_reset(void)
{
    OPEN_CFW_COMPRESS_LOG_MANAGER.magic = OPEN_CFW_COMPRESS_LOG_MANAGER_MAGIC;
    OPEN_CFW_COMPRESS_LOG_MANAGER.active_file = 0u;
    OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file = 0u;
    OPEN_CFW_COMPRESS_LOG_MANAGER.file_count = 0u;
    OPEN_CFW_COMPRESS_LOG_MANAGER.reserved = 0u;
    OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset = 0u;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_LOAD_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_manager_load(void)
{
    void *stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(
        OPEN_CFW_COMPRESS_LOG_MANAGER_PATH,
        OPEN_CFW_COMPRESS_LOG_MODE_READ
    );

    if (stream == NULL) {
        open_cfw_compress_log_manager_reset();
        OPEN_CFW_COMPRESS_LOG_INITIALIZED = 1u;
        return 0;
    }
    if (OPEN_CFW_COMPRESS_LOG_FILE_READ(
            (void *)&OPEN_CFW_COMPRESS_LOG_MANAGER,
            sizeof(OPEN_CFW_COMPRESS_LOG_MANAGER), 1u, stream) != 1u) {
        open_cfw_compress_log_manager_reset();
    }
    (void)OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream);
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.magic !=
        OPEN_CFW_COMPRESS_LOG_MANAGER_MAGIC) {
        open_cfw_compress_log_manager_reset();
    }
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.active_file >=
        OPEN_CFW_COMPRESS_LOG_FILE_COUNT) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.active_file = 0u;
    }
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file >=
        OPEN_CFW_COMPRESS_LOG_FILE_COUNT) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file = 0u;
    }
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.file_count >
        OPEN_CFW_COMPRESS_LOG_FILE_COUNT) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.file_count = 0u;
    }
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset >
        OPEN_CFW_COMPRESS_LOG_MAX_FILE_BYTES) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset = 0u;
    }
    OPEN_CFW_COMPRESS_LOG_INITIALIZED = 1u;
    return open_cfw_compress_log_manager_reconcile();
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_SAVE_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_manager_save(void)
{
    void *stream;
    unsigned int written;

    OPEN_CFW_COMPRESS_LOG_MANAGER.magic = OPEN_CFW_COMPRESS_LOG_MANAGER_MAGIC;
    stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(
        OPEN_CFW_COMPRESS_LOG_MANAGER_PATH,
        OPEN_CFW_COMPRESS_LOG_MODE_WRITE
    );
    if (stream == NULL) {
        return -1;
    }
    written = OPEN_CFW_COMPRESS_LOG_FILE_WRITE(
        (const void *)&OPEN_CFW_COMPRESS_LOG_MANAGER,
        sizeof(OPEN_CFW_COMPRESS_LOG_MANAGER), 1u, stream
    );
    (void)OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream);
    return written == 1u ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_REMOVE_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_file_remove(uint8_t file_index)
{
    unsigned char path[OPEN_CFW_COMPRESS_LOG_PATH_CAPACITY];

    open_cfw_compress_log_path_format(file_index, path, sizeof(path));
    (void)OPEN_CFW_COMPRESS_LOG_FILE_REMOVE(path);
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_HEADER_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_write_file_version_header(void *stream)
{
    unsigned char header[40];
    int length;
    unsigned int written;

    if (stream == NULL) {
        return 0;
    }
    length = OPEN_CFW_COMPRESS_LOG_SNPRINTF(
        header, sizeof(header),
        OPEN_CFW_COMPRESS_LOG_VERSION_FORMAT,
        OPEN_CFW_COMPRESS_LOG_VERSION
    );
    if (length <= 0 || (unsigned int)length >= sizeof(header)) {
        return 0;
    }
    (void)OPEN_CFW_COMPRESS_LOG_FILE_SEEK(stream, 0, 0u);
    written = OPEN_CFW_COMPRESS_LOG_FILE_WRITE(
        header, 1u, (unsigned int)length, stream
    );
    return written == (unsigned int)length ? (int)written : 0;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_ROTATE_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_rotate_file(void)
{
    uint8_t next = (uint8_t)(
        (OPEN_CFW_COMPRESS_LOG_MANAGER.active_file + 1u) %
        OPEN_CFW_COMPRESS_LOG_FILE_COUNT
    );
    unsigned char path[OPEN_CFW_COMPRESS_LOG_PATH_CAPACITY];
    void *stream;
    int header_bytes;

    if (OPEN_CFW_COMPRESS_LOG_MANAGER.file_count <
        OPEN_CFW_COMPRESS_LOG_FILE_COUNT) {
        ++OPEN_CFW_COMPRESS_LOG_MANAGER.file_count;
    } else {
        open_cfw_compress_log_file_remove(
            OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file
        );
        OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file = (uint8_t)(
            (OPEN_CFW_COMPRESS_LOG_MANAGER.oldest_file + 1u) %
            OPEN_CFW_COMPRESS_LOG_FILE_COUNT
        );
    }
    OPEN_CFW_COMPRESS_LOG_MANAGER.active_file = next;
    OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset = 0u;
    open_cfw_compress_log_path_format(next, path, sizeof(path));
    stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(
        path, OPEN_CFW_COMPRESS_LOG_MODE_WRITE
    );
    if (stream != NULL) {
        header_bytes = open_cfw_compress_log_write_file_version_header(stream);
        if (header_bytes > 0) {
            OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset =
                (uint32_t)header_bytes;
        }
        (void)OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream);
    }
    (void)open_cfw_compress_log_manager_save();
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_SYNC_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_sync_to_files(
    const unsigned char *data,
    unsigned int size
)
{
    unsigned int total = 0u;

    if (data == NULL || size == 0u) {
        return;
    }
    if (OPEN_CFW_COMPRESS_LOG_INITIALIZED == 0u) {
        (void)open_cfw_compress_log_manager_load();
    }
    if (OPEN_CFW_COMPRESS_LOG_MANAGER.file_count == 0u) {
        OPEN_CFW_COMPRESS_LOG_MANAGER.file_count = 1u;
    }
    while (total < size) {
        unsigned int available = OPEN_CFW_COMPRESS_LOG_MAX_FILE_BYTES -
            OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset;
        unsigned int chunk;
        unsigned int written;
        unsigned char path[OPEN_CFW_COMPRESS_LOG_PATH_CAPACITY];
        void *stream;

        if (available == 0u) {
            open_cfw_compress_log_rotate_file();
            available = OPEN_CFW_COMPRESS_LOG_MAX_FILE_BYTES;
        }
        chunk = size - total;
        if (chunk > available) {
            chunk = available;
        }
        open_cfw_compress_log_path_format(
            OPEN_CFW_COMPRESS_LOG_MANAGER.active_file,
            path, sizeof(path)
        );
        stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(
            path, OPEN_CFW_COMPRESS_LOG_MODE_UPDATE
        );
        if (stream == NULL) {
            int header_bytes;
            stream = OPEN_CFW_COMPRESS_LOG_FILE_OPEN(
                path, OPEN_CFW_COMPRESS_LOG_MODE_UPDATE_CREATE
            );
            if (stream == NULL) {
                return;
            }
            OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset = 0u;
            header_bytes = open_cfw_compress_log_write_file_version_header(stream);
            if (header_bytes > 0) {
                OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset =
                    (uint32_t)header_bytes;
            }
            available = OPEN_CFW_COMPRESS_LOG_MAX_FILE_BYTES -
                OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset;
            if (chunk > available) {
                chunk = available;
            }
        }
        (void)OPEN_CFW_COMPRESS_LOG_FILE_SEEK(
            stream,
            (int)OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset,
            0u
        );
        written = OPEN_CFW_COMPRESS_LOG_FILE_WRITE(
            data + total, 1u, chunk, stream
        );
        (void)OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream);
        if (written != chunk) {
            break;
        }
        OPEN_CFW_COMPRESS_LOG_MANAGER.current_offset += chunk;
        total += chunk;
        (void)open_cfw_compress_log_manager_save();
    }
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_TIMEOUT_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_export_timeout_callback(void *argument)
{
    (void)argument;
    OPEN_CFW_COMPRESS_LOG_EXPORT_STATE = 0u;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_NOTIFY_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_export_notify(uint8_t active)
{
    (void)OPEN_CFW_COMPRESS_LOG_REMOVE_DELAYED(
        open_cfw_compress_log_export_timeout_callback
    );
    if (active == 1u) {
        OPEN_CFW_COMPRESS_LOG_PUSH_DELAYED(
            open_cfw_compress_log_export_timeout_callback,
            NULL,
            OPEN_CFW_COMPRESS_LOG_EXPORT_TIMEOUT_TICKS
        );
    }
    OPEN_CFW_COMPRESS_LOG_EXPORT_STATE = active;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_ACTIVE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_compress_log_export_active(void)
{
    return OPEN_CFW_COMPRESS_LOG_EXPORT_STATE;
}
#endif

#undef OPEN_CFW_COMPRESS_LOG_REMOVE_DELAYED
#undef OPEN_CFW_COMPRESS_LOG_PUSH_DELAYED
#undef OPEN_CFW_COMPRESS_LOG_SNPRINTF
#undef OPEN_CFW_COMPRESS_LOG_FILE_REMOVE
#undef OPEN_CFW_COMPRESS_LOG_FILE_SEEK
#undef OPEN_CFW_COMPRESS_LOG_FILE_WRITE
#undef OPEN_CFW_COMPRESS_LOG_FILE_READ
#undef OPEN_CFW_COMPRESS_LOG_FILE_CLOSE
#undef OPEN_CFW_COMPRESS_LOG_FILE_OPEN
#undef OPEN_CFW_COMPRESS_LOG_VERSION
#undef OPEN_CFW_COMPRESS_LOG_VERSION_FORMAT
#undef OPEN_CFW_COMPRESS_LOG_MODE_UPDATE_CREATE
#undef OPEN_CFW_COMPRESS_LOG_MODE_UPDATE
#undef OPEN_CFW_COMPRESS_LOG_MODE_WRITE
#undef OPEN_CFW_COMPRESS_LOG_MODE_READ
#undef OPEN_CFW_COMPRESS_LOG_MANAGER_PATH
#undef OPEN_CFW_COMPRESS_LOG_FILE_PATH_FORMAT
