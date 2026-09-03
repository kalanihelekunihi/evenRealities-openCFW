/* SPDX-License-Identifier: MIT */
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct host_file {
    char path[48];
    unsigned char *data;
    size_t size;
    size_t capacity;
    size_t position;
    int present;
};

static struct host_file host_files[6];
static struct open_cfw_compress_log_manager host_manager;
static uint8_t host_initialized;
static uint8_t host_export_state;
static void (*host_delayed_callback)(void *);
static void *host_delayed_argument;
static unsigned int host_delayed_ticks;
static unsigned int host_remove_calls;

static struct host_file *host_find(const char *path)
{
    unsigned int index;
    for (index = 0u; index < 6u; ++index) {
        if (host_files[index].present != 0 &&
            strcmp(host_files[index].path, path) == 0) {
            return &host_files[index];
        }
    }
    return NULL;
}

static struct host_file *host_open(const void *raw_path, const char *mode)
{
    const char *path = raw_path;
    struct host_file *file = host_find(path);
    unsigned int index;
    if (file == NULL && strchr(mode, 'w') == NULL) return NULL;
    if (file == NULL) {
        for (index = 0u; index < 6u; ++index) {
            if (host_files[index].present == 0) {
                file = &host_files[index];
                memset(file, 0, sizeof(*file));
                file->present = 1;
                (void)snprintf(file->path, sizeof(file->path), "%s", path);
                break;
            }
        }
    }
    if (file == NULL) return NULL;
    if (mode[0] == 'w') file->size = 0u;
    file->position = 0u;
    return file;
}

static int host_close(void *stream) { return stream == NULL ? -1 : 0; }

static unsigned int host_read(
    void *buffer, unsigned int size, unsigned int count, void *stream)
{
    struct host_file *file = stream;
    size_t bytes = (size_t)size * count;
    if (file == NULL || file->position + bytes > file->size) return 0u;
    memcpy(buffer, file->data + file->position, bytes);
    file->position += bytes;
    return count;
}

static unsigned int host_write(
    const void *buffer, unsigned int size, unsigned int count, void *stream)
{
    struct host_file *file = stream;
    size_t bytes = (size_t)size * count;
    size_t needed;
    unsigned char *next;
    if (file == NULL) return 0u;
    needed = file->position + bytes;
    if (needed > file->capacity) {
        size_t capacity = needed < 64u ? 64u : needed;
        next = realloc(file->data, capacity);
        if (next == NULL) return 0u;
        file->data = next;
        file->capacity = capacity;
    }
    memcpy(file->data + file->position, buffer, bytes);
    file->position += bytes;
    if (file->position > file->size) file->size = file->position;
    return count;
}

static int host_seek(void *stream, int offset, unsigned int origin)
{
    struct host_file *file = stream;
    if (file == NULL || origin != 0u || offset < 0) return -1;
    file->position = (size_t)offset;
    return 0;
}

static int host_remove(const void *raw_path)
{
    struct host_file *file = host_find(raw_path);
    if (file == NULL) return -1;
    file->present = 0;
    file->size = 0u;
    return 0;
}

static int host_snprintf(
    unsigned char *buffer, unsigned int count,
    const unsigned char *format, ...
)
{
    int result;
    va_list arguments;
    va_start(arguments, format);
    result = vsnprintf((char *)buffer, count, (const char *)format, arguments);
    va_end(arguments);
    return result;
}

static void host_push_delayed(
    void (*callback)(void *), void *argument, unsigned int ticks
)
{
    host_delayed_callback = callback;
    host_delayed_argument = argument;
    host_delayed_ticks = ticks;
}

static unsigned char host_remove_delayed(void (*callback)(void *))
{
    ++host_remove_calls;
    if (host_delayed_callback == callback) {
        host_delayed_callback = NULL;
        host_delayed_argument = NULL;
        host_delayed_ticks = 0u;
        return 1u;
    }
    return 0u;
}

#define OPEN_CFW_COMPRESS_LOG_MANAGER host_manager
#define OPEN_CFW_COMPRESS_LOG_INITIALIZED host_initialized
#define OPEN_CFW_COMPRESS_LOG_EXPORT_STATE host_export_state
#define OPEN_CFW_COMPRESS_LOG_FILE_PATH_FORMAT \
    ((const unsigned char *)"/log/compress_log_%d.bin")
#define OPEN_CFW_COMPRESS_LOG_MANAGER_PATH \
    ((const unsigned char *)"/log/compress_manager.bin")
#define OPEN_CFW_COMPRESS_LOG_MODE_READ "rb"
#define OPEN_CFW_COMPRESS_LOG_MODE_WRITE "wb"
#define OPEN_CFW_COMPRESS_LOG_MODE_UPDATE "r+b"
#define OPEN_CFW_COMPRESS_LOG_MODE_UPDATE_CREATE "w+b"
#define OPEN_CFW_COMPRESS_LOG_VERSION_FORMAT \
    ((const unsigned char *)"Software_Version: %s\n")
#define OPEN_CFW_COMPRESS_LOG_VERSION "2.2.6.10"
#define OPEN_CFW_COMPRESS_LOG_FILE_OPEN(path, mode) host_open((path), (mode))
#define OPEN_CFW_COMPRESS_LOG_FILE_CLOSE(stream) host_close(stream)
#define OPEN_CFW_COMPRESS_LOG_FILE_READ(...) host_read(__VA_ARGS__)
#define OPEN_CFW_COMPRESS_LOG_FILE_WRITE(...) host_write(__VA_ARGS__)
#define OPEN_CFW_COMPRESS_LOG_FILE_SEEK(...) host_seek(__VA_ARGS__)
#define OPEN_CFW_COMPRESS_LOG_FILE_REMOVE(path) host_remove(path)
#define OPEN_CFW_COMPRESS_LOG_SNPRINTF(...) host_snprintf(__VA_ARGS__)
#define OPEN_CFW_COMPRESS_LOG_PUSH_DELAYED(...) host_push_delayed(__VA_ARGS__)
#define OPEN_CFW_COMPRESS_LOG_REMOVE_DELAYED(callback) \
    host_remove_delayed(callback)
#include "../../components/apollo_main/core_overlay/compress_log_port.c"

#define CHECK(condition) do { if (!(condition)) return __LINE__; } while (0)

static void host_reset(void)
{
    unsigned int index;
    for (index = 0u; index < 6u; ++index) {
        free(host_files[index].data);
    }
    memset(host_files, 0, sizeof(host_files));
    memset(&host_manager, 0, sizeof(host_manager));
    host_initialized = 0u;
    host_export_state = 0u;
    host_delayed_callback = NULL;
    host_delayed_argument = NULL;
    host_delayed_ticks = 0u;
    host_remove_calls = 0u;
}

static int test_initial_write_and_reload(void)
{
    const unsigned char payload[] = {1u, 2u, 3u, 4u};
    struct host_file *log;
    struct host_file *manager;
    host_reset();
    open_cfw_compress_log_sync_to_files(payload, sizeof(payload));
    log = host_find("/log/compress_log_0.bin");
    manager = host_find("/log/compress_manager.bin");
    CHECK(log != NULL && manager != NULL);
    CHECK(log->size == 31u);
    CHECK(memcmp(log->data, "Software_Version: 2.2.6.10\n", 27u) == 0);
    CHECK(memcmp(log->data + 27u, payload, sizeof(payload)) == 0);
    CHECK(host_manager.magic == 0x4c4d4752u);
    CHECK(host_manager.file_count == 1u);
    CHECK(host_manager.current_offset == 31u);
    memset(&host_manager, 0xff, sizeof(host_manager));
    host_initialized = 0u;
    CHECK(open_cfw_compress_log_manager_load() == 0);
    CHECK(host_manager.active_file == 0u);
    CHECK(host_manager.oldest_file == 0u);
    CHECK(host_manager.file_count == 1u);
    CHECK(host_manager.current_offset == 31u);
    return 0;
}

static int test_rotation_and_reconcile(void)
{
    const unsigned char bytes[] = {9u, 8u, 7u, 6u};
    unsigned int index;
    host_reset();
    host_manager.magic = 0x4c4d4752u;
    host_manager.active_file = 0u;
    host_manager.oldest_file = 1u;
    host_manager.file_count = 5u;
    host_manager.current_offset = 512000u;
    host_initialized = 1u;
    for (index = 0u; index < 5u; ++index) {
        char path[48];
        (void)snprintf(path, sizeof(path), "/log/compress_log_%u.bin", index);
        CHECK(host_open(path, "wb") != NULL);
    }
    open_cfw_compress_log_sync_to_files(bytes, sizeof(bytes));
    CHECK(host_manager.active_file == 1u);
    CHECK(host_manager.oldest_file == 2u);
    CHECK(host_manager.file_count == 5u);
    CHECK(host_manager.current_offset == 31u);
    CHECK(host_find("/log/compress_log_0.bin") != NULL);
    CHECK(host_find("/log/compress_log_1.bin") != NULL);
    CHECK(host_remove("/log/compress_log_3.bin") == 0);
    CHECK(open_cfw_compress_log_manager_reconcile() == 0);
    CHECK(host_manager.file_count == 4u);
    CHECK(host_manager.oldest_file == 2u);
    return 0;
}

static int test_invalid_manager_and_export_timeout(void)
{
    struct open_cfw_compress_log_manager invalid = {
        0u, 9u, 8u, 7u, 0u, 512001u
    };
    struct host_file *manager;
    host_reset();
    manager = host_open("/log/compress_manager.bin", "wb");
    CHECK(manager != NULL);
    CHECK(host_write(&invalid, sizeof(invalid), 1u, manager) == 1u);
    CHECK(open_cfw_compress_log_manager_load() == 0);
    CHECK(host_manager.magic == 0x4c4d4752u);
    CHECK(host_manager.active_file == 0u);
    CHECK(host_manager.oldest_file == 0u);
    CHECK(host_manager.file_count == 0u);
    CHECK(host_manager.current_offset == 0u);
    open_cfw_compress_log_export_notify(1u);
    CHECK(open_cfw_compress_log_export_active() == 1u);
    CHECK(host_delayed_callback ==
        open_cfw_compress_log_export_timeout_callback);
    CHECK(host_delayed_argument == NULL);
    CHECK(host_delayed_ticks == 120000u);
    host_delayed_callback(host_delayed_argument);
    CHECK(open_cfw_compress_log_export_active() == 0u);
    open_cfw_compress_log_export_notify(0u);
    CHECK(host_delayed_callback == NULL);
    CHECK(host_remove_calls == 2u);
    return 0;
}

int main(void)
{
    int result = test_initial_write_and_reload();
    if (result != 0) return result;
    result = test_rotation_and_reconcile();
    if (result != 0) return result;
    return test_invalid_manager_and_export_timeout();
}
