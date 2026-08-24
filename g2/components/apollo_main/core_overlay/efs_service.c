/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the G2 EFS import/export service.  It keeps
 * the recovered C4/C5/C6/C7 control ABI, 120-byte transfer record, bounded
 * Android-message buffer, whitelist write/read verification, CRC-32C state,
 * 4 KiB export chunks, registered service callback, and cancellation policy.
 * Diagnostic-only logging is intentionally omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL 0xC4U
#define OPEN_CFW_EFS_SERVICE_IMPORT_DATA 0xC5U
#define OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL 0xC6U
#define OPEN_CFW_EFS_SERVICE_EXPORT_DATA 0xC7U
#define OPEN_CFW_EFS_SERVICE_CHUNK_BYTES 0x1000U
#define OPEN_CFW_EFS_SERVICE_ANDROID_BYTES 0x2137U
#define OPEN_CFW_EFS_SERVICE_PATH_BYTES 80U
#define OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST 0U
#define OPEN_CFW_EFS_SERVICE_TYPE_ANDROID 1U
#define OPEN_CFW_EFS_SERVICE_TYPE_LOGGER 2U
#define OPEN_CFW_EFS_SERVICE_TYPE_TRACEPOINT 3U
#define OPEN_CFW_EFS_SERVICE_TYPE_OTHER 0xAAU
#define OPEN_CFW_EFS_SERVICE_OK 0U
#define OPEN_CFW_EFS_SERVICE_INVALID 1U
#define OPEN_CFW_EFS_SERVICE_CRC_ERROR 2U
#define OPEN_CFW_EFS_SERVICE_IO_ERROR 3U
#define OPEN_CFW_EFS_SERVICE_SIZE_ERROR 6U

typedef struct {
    uint32_t handle;
    uint8_t open;
    uint8_t path[OPEN_CFW_EFS_SERVICE_PATH_BYTES];
    uint8_t reserved0[3];
    uint32_t file_type;
    uint32_t file_size;
    uint32_t received_crc;
    uint32_t calculated_crc;
    uint32_t chunk_length;
    uint32_t transferred;
    uint32_t remaining;
    uint8_t progress;
    uint8_t is_start;
    uint8_t reserved1[2];
} open_cfw_efs_transfer;

_Static_assert(sizeof(open_cfw_efs_transfer) == 0x78U,
    "G2 EFS transfer ABI must remain 120 bytes");

#ifndef OPEN_CFW_EFS_SERVICE_TRANSFER
#define OPEN_CFW_EFS_SERVICE_TRANSFER \
    (*(open_cfw_efs_transfer *)(uintptr_t)0x20071CC8U)
#endif
#ifndef OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER
#define OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER \
    (*(uint8_t *volatile *)(uintptr_t)0x20074554U)
#endif
#ifndef OPEN_CFW_EFS_SERVICE_EXPORT_BUFFER
#define OPEN_CFW_EFS_SERVICE_EXPORT_BUFFER \
    ((uint8_t *)(uintptr_t)0x2035ADF8U)
#endif
#ifndef OPEN_CFW_EFS_SERVICE_IMPORT_VERIFY_BUFFER
#define OPEN_CFW_EFS_SERVICE_IMPORT_VERIFY_BUFFER \
    ((uint8_t *)(uintptr_t)0x2035BE08U)
#endif
#ifndef OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE
#define OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE \
    (*(volatile uint8_t *)(uintptr_t)0x20074FBCU)
#endif
#ifndef OPEN_CFW_EFS_SERVICE_WHITELIST_PATH
#define OPEN_CFW_EFS_SERVICE_WHITELIST_PATH \
    ((const uint8_t *)(uintptr_t)0x0076B538U)
#endif

#ifndef OPEN_CFW_EFS_SERVICE_SEND
int8_t open_cfw_efs_service_send(uint8_t response, uint8_t command,
    const uint8_t *payload, uint16_t length);
#define OPEN_CFW_EFS_SERVICE_SEND(response, command, payload, length) \
    open_cfw_efs_service_send((response), (command), (payload), (length))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_SEND_RAW
int8_t open_cfw_efs_service_send_raw(uint8_t response, uint8_t command,
    const uint8_t *payload, uint16_t length);
#define OPEN_CFW_EFS_SERVICE_SEND_RAW(response, command, payload, length) \
    open_cfw_efs_service_send_raw((response), (command), (payload), (length))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_MODE
uint32_t open_cfw_efs_file_mode(uint32_t selector);
#define OPEN_CFW_EFS_SERVICE_FILE_MODE(selector) \
    open_cfw_efs_file_mode((selector))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_OPEN
uint32_t open_cfw_file_open(const uint8_t *path, uint32_t mode);
#define OPEN_CFW_EFS_SERVICE_FILE_OPEN(path, mode) \
    open_cfw_file_open((path), (mode))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_CLOSE
int32_t open_cfw_file_close(uint32_t handle);
#define OPEN_CFW_EFS_SERVICE_FILE_CLOSE(handle) open_cfw_file_close((handle))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_READ
uint32_t open_cfw_file_read(
    void *data, uint32_t item_size, uint32_t count, uint32_t handle);
#define OPEN_CFW_EFS_SERVICE_FILE_READ(data, item_size, count, handle) \
    open_cfw_file_read((data), (item_size), (count), (handle))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_WRITE
uint32_t open_cfw_file_write(
    const void *data, uint32_t item_size, uint32_t count, uint32_t handle);
#define OPEN_CFW_EFS_SERVICE_FILE_WRITE(data, item_size, count, handle) \
    open_cfw_file_write((data), (item_size), (count), (handle))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_SEEK
int32_t open_cfw_file_seek(uint32_t handle, int32_t offset, uint32_t origin);
#define OPEN_CFW_EFS_SERVICE_FILE_SEEK(handle, offset, origin) \
    open_cfw_file_seek((handle), (offset), (origin))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_SIZE
int32_t open_cfw_file_size(uint32_t handle);
#define OPEN_CFW_EFS_SERVICE_FILE_SIZE(handle) open_cfw_file_size((handle))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_FILE_REMOVE
int32_t open_cfw_file_remove(const uint8_t *path);
#define OPEN_CFW_EFS_SERVICE_FILE_REMOVE(path) open_cfw_file_remove((path))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_CRC32C
void open_cfw_crc32c_update(
    const uint8_t *data, uint32_t length, uint32_t *crc);
#define OPEN_CFW_EFS_SERVICE_CRC32C(data, length, crc) \
    open_cfw_crc32c_update((data), (length), (crc))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER_PROVIDER
uint8_t *open_cfw_efs_android_buffer(void);
#define OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER_PROVIDER() \
    open_cfw_efs_android_buffer()
#endif
#ifndef OPEN_CFW_EFS_SERVICE_ANDROID_CONSUME
void open_cfw_efs_android_consume(const uint8_t *data);
#define OPEN_CFW_EFS_SERVICE_ANDROID_CONSUME(data) \
    open_cfw_efs_android_consume((data))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_WHITELIST_RELOAD
void open_cfw_efs_whitelist_reload(uint32_t reason);
#define OPEN_CFW_EFS_SERVICE_WHITELIST_RELOAD(reason) \
    open_cfw_efs_whitelist_reload((reason))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_EXPORT_PATH_VALID
uint8_t open_cfw_efs_export_path_valid(const uint8_t *path);
#define OPEN_CFW_EFS_SERVICE_EXPORT_PATH_VALID(path) \
    open_cfw_efs_export_path_valid((path))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_LOGGER_PATH_VALID
uint8_t open_cfw_efs_logger_path_valid(const uint8_t *path);
#define OPEN_CFW_EFS_SERVICE_LOGGER_PATH_VALID(path) \
    open_cfw_efs_logger_path_valid((path))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_TRACE_PATH_VALID
uint8_t open_cfw_efs_trace_path_valid(const uint8_t *path);
#define OPEN_CFW_EFS_SERVICE_TRACE_PATH_VALID(path) \
    open_cfw_efs_trace_path_valid((path))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_TRACE_PREPARE
int32_t open_cfw_efs_trace_prepare(void);
#define OPEN_CFW_EFS_SERVICE_TRACE_PREPARE() open_cfw_efs_trace_prepare()
#endif
#ifndef OPEN_CFW_EFS_SERVICE_EXPORT_MODE
void open_cfw_efs_export_mode(uint8_t enabled);
#define OPEN_CFW_EFS_SERVICE_EXPORT_MODE(enabled) \
    open_cfw_efs_export_mode((enabled))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_ACTIVITY_BEGIN
void open_cfw_efs_activity_begin(void);
#define OPEN_CFW_EFS_SERVICE_ACTIVITY_BEGIN() open_cfw_efs_activity_begin()
#endif
#ifndef OPEN_CFW_EFS_SERVICE_ACTIVITY_END
void open_cfw_efs_activity_end(uint32_t milliseconds);
#define OPEN_CFW_EFS_SERVICE_ACTIVITY_END(milliseconds) \
    open_cfw_efs_activity_end((milliseconds))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_REGISTER
typedef int (*open_cfw_efs_service_callback)(
    uint8_t command, const uint8_t *payload, uint16_t length);
void open_cfw_efs_service_register(
    uint32_t service, open_cfw_efs_service_callback callback, uint8_t enabled);
#define OPEN_CFW_EFS_SERVICE_REGISTER(service, callback, enabled) \
    open_cfw_efs_service_register((service), (callback), (enabled))
#endif
#ifndef OPEN_CFW_EFS_SERVICE_DISPATCH_CALLBACK
#define OPEN_CFW_EFS_SERVICE_DISPATCH_CALLBACK \
    ((open_cfw_efs_service_callback)(uintptr_t)0x00458B61U)
#endif

void _evenEfsReplyToAPP(
    uint8_t command, uint8_t subcommand, uint8_t status, uint32_t reserved);
uint32_t _fileCaculateCRC(uint32_t *handle, const uint8_t *path,
    uint32_t *file_size, uint32_t *crc);
void _efsFileCmdParse(uint8_t subcommand, const uint8_t *data,
    uint16_t length, uint32_t reserved);
void _efsFileRawDataParse(const uint8_t *data, uint16_t length);
void _efsExportFileParse(
    uint8_t subcommand, const uint8_t *data, uint16_t length);
int EFS_FrameDispatch(
    uint8_t command, const uint8_t *payload, uint16_t length);
uint32_t EFS_NotifyStatus4(uint8_t command);
uint32_t EFS_NotifyStatus2(uint8_t command);
uint32_t EFS_NotifyStatus5(uint8_t command);
uint8_t EFS_TransferActive(void);
void EFS_ServiceInit(void);
void EFS_CancelExport(
    int32_t reason, const uint8_t *source, uint32_t detail0, uint32_t detail1);

#if defined(OPEN_CFW_EFS_SERVICE_REPLY_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_REPLY 1
#elif defined(OPEN_CFW_EFS_SERVICE_CRC_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_CRC 1
#elif defined(OPEN_CFW_EFS_SERVICE_COMMAND_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_COMMAND 1
#elif defined(OPEN_CFW_EFS_SERVICE_RAW_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_RAW 1
#elif defined(OPEN_CFW_EFS_SERVICE_EXPORT_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_EXPORT 1
#elif defined(OPEN_CFW_EFS_SERVICE_DISPATCH_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_DISPATCH 1
#elif defined(OPEN_CFW_EFS_SERVICE_STATUS4_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS4 1
#elif defined(OPEN_CFW_EFS_SERVICE_STATUS2_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS2 1
#elif defined(OPEN_CFW_EFS_SERVICE_STATUS5_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS5 1
#elif defined(OPEN_CFW_EFS_SERVICE_ACTIVE_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_ACTIVE 1
#elif defined(OPEN_CFW_EFS_SERVICE_INIT_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_INIT 1
#elif defined(OPEN_CFW_EFS_SERVICE_CANCEL_ONLY)
#define OPEN_CFW_EFS_SERVICE_INCLUDE_CANCEL 1
#else
#define OPEN_CFW_EFS_SERVICE_INCLUDE_REPLY 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_CRC 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_COMMAND 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_RAW 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_EXPORT 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_DISPATCH 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS4 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS2 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS5 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_ACTIVE 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_INIT 1
#define OPEN_CFW_EFS_SERVICE_INCLUDE_CANCEL 1
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_zero(void *raw, uint32_t length)
{
    uint8_t *data = raw;
    uint32_t index;
    for (index = 0U; index < length; ++index) data[index] = 0U;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_copy(
    void *raw_destination, const void *raw_source, uint32_t length)
{
    uint8_t *destination = raw_destination;
    const uint8_t *source = raw_source;
    uint32_t index;
    for (index = 0U; index < length; ++index) destination[index] = source[index];
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_efs_service_load32(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_store32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_reply(
    uint8_t command, uint8_t subcommand, uint8_t status)
{
    uint8_t payload[2];
    payload[0] = subcommand;
    payload[1] = status;
    (void)OPEN_CFW_EFS_SERVICE_SEND(1U, command, payload, 2U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_close(open_cfw_efs_transfer *transfer)
{
    if (transfer->handle != 0U) {
        (void)OPEN_CFW_EFS_SERVICE_FILE_CLOSE(transfer->handle);
        transfer->handle = 0U;
    }
    transfer->open = 0U;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_reset(open_cfw_efs_transfer *transfer)
{
    open_cfw_efs_service_close(transfer);
    open_cfw_efs_service_zero(transfer, sizeof(*transfer));
    OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE = 0U;
    OPEN_CFW_EFS_SERVICE_EXPORT_MODE(0U);
    OPEN_CFW_EFS_SERVICE_ACTIVITY_END(2000U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_efs_service_update_progress(open_cfw_efs_transfer *transfer)
{
    if (transfer->file_size == 0U) transfer->progress = 0U;
    else {
        uint32_t value = (transfer->transferred * 100U) / transfer->file_size;
        transfer->progress = (uint8_t)(value > 100U ? 100U : value);
    }
}

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_REPLY)
__attribute__((used, noinline))
void _evenEfsReplyToAPP(
    uint8_t command, uint8_t subcommand, uint8_t status, uint32_t reserved)
{
    (void)reserved;
    open_cfw_efs_service_reply(command, subcommand, status);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_CRC)
__attribute__((used, noinline))
uint32_t _fileCaculateCRC(uint32_t *handle, const uint8_t *path,
    uint32_t *file_size, uint32_t *crc)
{
    uint8_t *buffer = OPEN_CFW_EFS_SERVICE_IMPORT_VERIFY_BUFFER;
    int32_t size;
    uint32_t remaining;
    uint32_t amount;
    uint32_t read;

    if (handle == 0 || path == 0 || file_size == 0 || crc == 0 || buffer == 0)
        return 0U;
    *handle = OPEN_CFW_EFS_SERVICE_FILE_OPEN(
        path, OPEN_CFW_EFS_SERVICE_FILE_MODE(1U));
    if (*handle == 0U) return 0U;
    size = OPEN_CFW_EFS_SERVICE_FILE_SIZE(*handle);
    if (size < 0) {
        (void)OPEN_CFW_EFS_SERVICE_FILE_CLOSE(*handle);
        *handle = 0U;
        return 0U;
    }
    *file_size = (uint32_t)size;
    *crc = 0U;
    remaining = *file_size;
    while (remaining != 0U) {
        amount = remaining > OPEN_CFW_EFS_SERVICE_CHUNK_BYTES ?
            OPEN_CFW_EFS_SERVICE_CHUNK_BYTES : remaining;
        read = OPEN_CFW_EFS_SERVICE_FILE_READ(buffer, 1U, amount, *handle);
        if (read != amount) {
            (void)OPEN_CFW_EFS_SERVICE_FILE_CLOSE(*handle);
            *handle = 0U;
            return 0U;
        }
        OPEN_CFW_EFS_SERVICE_CRC32C(buffer, amount, crc);
        remaining -= amount;
    }
    (void)OPEN_CFW_EFS_SERVICE_FILE_CLOSE(*handle);
    *handle = 0U;
    return 1U;
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_COMMAND)
__attribute__((used, noinline))
void _efsFileCmdParse(uint8_t subcommand, const uint8_t *data,
    uint16_t length, uint32_t reserved)
{
    open_cfw_efs_transfer *transfer = &OPEN_CFW_EFS_SERVICE_TRANSFER;
    const uint8_t *path = 0;
    uint8_t *android;
    uint32_t mode;
    int32_t remove_result;
    uint8_t valid;
    (void)reserved;

    if (subcommand == 0U) {
        if (data == 0 || length < 92U) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_INVALID);
            return;
        }
        OPEN_CFW_EFS_SERVICE_ACTIVITY_BEGIN();
        open_cfw_efs_service_reset(transfer);
        transfer->file_type = open_cfw_efs_service_load32(data);
        transfer->file_size = open_cfw_efs_service_load32(data + 4U);
        transfer->received_crc = open_cfw_efs_service_load32(data + 8U);
        open_cfw_efs_service_copy(
            transfer->path, data + 12U, OPEN_CFW_EFS_SERVICE_PATH_BYTES);
        transfer->path[OPEN_CFW_EFS_SERVICE_PATH_BYTES - 1U] = 0U;
        transfer->remaining = transfer->file_size;

        if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST) {
            path = OPEN_CFW_EFS_SERVICE_WHITELIST_PATH;
            open_cfw_efs_service_zero(
                transfer->path, OPEN_CFW_EFS_SERVICE_PATH_BYTES);
            for (mode = 0U; mode + 1U < OPEN_CFW_EFS_SERVICE_PATH_BYTES &&
                    path[mode] != 0U; ++mode)
                transfer->path[mode] = path[mode];
        } else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_ANDROID) {
            if (transfer->file_size >= OPEN_CFW_EFS_SERVICE_ANDROID_BYTES) {
                open_cfw_efs_service_reply(
                    OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                    OPEN_CFW_EFS_SERVICE_INVALID);
                open_cfw_efs_service_reset(transfer);
                return;
            }
            android = OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER;
            if (android == 0) {
                android = OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER_PROVIDER();
                OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER = android;
            }
            if (android == 0) {
                open_cfw_efs_service_reply(
                    OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                    OPEN_CFW_EFS_SERVICE_IO_ERROR);
                open_cfw_efs_service_reset(transfer);
                return;
            }
            open_cfw_efs_service_zero(
                android, OPEN_CFW_EFS_SERVICE_ANDROID_BYTES);
            transfer->is_start = 0U;
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_OK);
            return;
        } else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_LOGGER ||
                transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_TRACEPOINT) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_INVALID);
            open_cfw_efs_service_reset(transfer);
            return;
        } else if (transfer->file_type != OPEN_CFW_EFS_SERVICE_TYPE_OTHER) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_INVALID);
            open_cfw_efs_service_reset(transfer);
            return;
        }

        remove_result = OPEN_CFW_EFS_SERVICE_FILE_REMOVE(transfer->path);
        if (remove_result < 0 && remove_result != -2) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_IO_ERROR);
            open_cfw_efs_service_reset(transfer);
            return;
        }
        mode = OPEN_CFW_EFS_SERVICE_FILE_MODE(0x103U);
        transfer->handle = OPEN_CFW_EFS_SERVICE_FILE_OPEN(transfer->path, mode);
        if (transfer->handle == 0U) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_IO_ERROR);
            open_cfw_efs_service_reset(transfer);
            return;
        }
        transfer->open = 1U;
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 0U,
            OPEN_CFW_EFS_SERVICE_OK);
        return;
    }

    if (subcommand == 1U) {
        transfer->is_start = 1U;
        return;
    }
    if (subcommand != 2U) return;

    valid = (uint8_t)(transfer->transferred == transfer->file_size &&
        transfer->calculated_crc == transfer->received_crc);
    if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST ||
            transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_OTHER)
        open_cfw_efs_service_close(transfer);
    if (valid != 0U) {
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 2U,
            OPEN_CFW_EFS_SERVICE_OK);
        if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST)
            OPEN_CFW_EFS_SERVICE_WHITELIST_RELOAD(2U);
        else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_ANDROID)
            OPEN_CFW_EFS_SERVICE_ANDROID_CONSUME(
                OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER);
    } else {
        if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST ||
                transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_OTHER)
            (void)OPEN_CFW_EFS_SERVICE_FILE_REMOVE(transfer->path);
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL, 2U,
            OPEN_CFW_EFS_SERVICE_SIZE_ERROR);
    }
    open_cfw_efs_service_reset(transfer);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_RAW)
__attribute__((used, noinline))
void _efsFileRawDataParse(const uint8_t *data, uint16_t length)
{
    open_cfw_efs_transfer *transfer = &OPEN_CFW_EFS_SERVICE_TRANSFER;
    uint8_t *android;
    uint8_t *verify;
    uint32_t written;
    uint32_t read;
    uint32_t index;
    uint8_t success = 0U;

    if (data == 0 || length == 0U || transfer->is_start == 0U ||
            transfer->transferred + length > transfer->file_size) {
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_IMPORT_DATA, 1U,
            OPEN_CFW_EFS_SERVICE_INVALID);
        return;
    }
    if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_ANDROID) {
        android = OPEN_CFW_EFS_SERVICE_ANDROID_BUFFER;
        if (android != 0 && transfer->transferred + length <
                OPEN_CFW_EFS_SERVICE_ANDROID_BYTES) {
            open_cfw_efs_service_copy(
                android + transfer->transferred, data, length);
            success = 1U;
        }
    } else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST ||
            transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_OTHER) {
        if (transfer->open != 0U && transfer->handle != 0U) {
            written = OPEN_CFW_EFS_SERVICE_FILE_WRITE(
                data, 1U, length, transfer->handle);
            if (written == length) {
                if (transfer->file_type ==
                        OPEN_CFW_EFS_SERVICE_TYPE_WHITELIST) {
                    verify = OPEN_CFW_EFS_SERVICE_IMPORT_VERIFY_BUFFER;
                    if (verify != 0 &&
                            OPEN_CFW_EFS_SERVICE_FILE_SEEK(transfer->handle,
                                (int32_t)transfer->transferred, 0U) >= 0) {
                        read = OPEN_CFW_EFS_SERVICE_FILE_READ(
                            verify, 1U, length, transfer->handle);
                        success = (uint8_t)(read == length);
                        for (index = 0U; success != 0U && index < length;
                                ++index)
                            if (verify[index] != data[index]) success = 0U;
                        (void)OPEN_CFW_EFS_SERVICE_FILE_SEEK(transfer->handle,
                            (int32_t)(transfer->transferred + length), 0U);
                    }
                } else success = 1U;
            }
        }
    }
    if (success == 0U) {
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_IMPORT_DATA, 1U,
            OPEN_CFW_EFS_SERVICE_IO_ERROR);
        return;
    }
    OPEN_CFW_EFS_SERVICE_CRC32C(
        data, length, &transfer->calculated_crc);
    transfer->chunk_length = length;
    transfer->transferred += length;
    transfer->remaining = transfer->file_size - transfer->transferred;
    open_cfw_efs_service_update_progress(transfer);
    open_cfw_efs_service_reply(
        OPEN_CFW_EFS_SERVICE_IMPORT_DATA, 1U, OPEN_CFW_EFS_SERVICE_OK);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_EXPORT)
__attribute__((used, noinline))
void _efsExportFileParse(
    uint8_t subcommand, const uint8_t *data, uint16_t length)
{
    open_cfw_efs_transfer *transfer = &OPEN_CFW_EFS_SERVICE_TRANSFER;
    uint8_t metadata[10];
    uint8_t *buffer = OPEN_CFW_EFS_SERVICE_EXPORT_BUFFER;
    uint32_t amount;
    uint32_t read;
    uint8_t valid;

    if (subcommand == 0U) {
        if (data == 0 || length < 84U || buffer == 0) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_INVALID);
            return;
        }
        OPEN_CFW_EFS_SERVICE_ACTIVITY_BEGIN();
        open_cfw_efs_service_reset(transfer);
        transfer->file_type = open_cfw_efs_service_load32(data);
        open_cfw_efs_service_copy(
            transfer->path, data + 4U, OPEN_CFW_EFS_SERVICE_PATH_BYTES);
        transfer->path[OPEN_CFW_EFS_SERVICE_PATH_BYTES - 1U] = 0U;
        valid = 0U;
        if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_LOGGER)
            valid = OPEN_CFW_EFS_SERVICE_LOGGER_PATH_VALID(transfer->path);
        else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_TRACEPOINT) {
            valid = OPEN_CFW_EFS_SERVICE_TRACE_PATH_VALID(transfer->path);
            if (valid != 0U && OPEN_CFW_EFS_SERVICE_TRACE_PREPARE() != 0)
                valid = 0U;
        } else if (transfer->file_type == OPEN_CFW_EFS_SERVICE_TYPE_OTHER)
            valid = OPEN_CFW_EFS_SERVICE_EXPORT_PATH_VALID(transfer->path);
        if (valid == 0U) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_INVALID);
            open_cfw_efs_service_reset(transfer);
            return;
        }
        if (_fileCaculateCRC(&transfer->handle, transfer->path,
                &transfer->file_size, &transfer->calculated_crc) == 0U) {
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, 0U,
                OPEN_CFW_EFS_SERVICE_CRC_ERROR);
            open_cfw_efs_service_reset(transfer);
            return;
        }
        open_cfw_efs_service_zero(metadata, sizeof(metadata));
        open_cfw_efs_service_store32(metadata + 2U, transfer->file_size);
        open_cfw_efs_service_store32(metadata + 6U, transfer->calculated_crc);
        transfer->remaining = transfer->file_size;
        (void)OPEN_CFW_EFS_SERVICE_SEND(1U,
            OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, metadata, sizeof(metadata));
        transfer->handle = OPEN_CFW_EFS_SERVICE_FILE_OPEN(
            transfer->path, OPEN_CFW_EFS_SERVICE_FILE_MODE(1U));
        if (transfer->handle == 0U) {
            open_cfw_efs_service_reset(transfer);
            return;
        }
        transfer->open = 1U;
        transfer->is_start = 1U;
        OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE = 1U;
        OPEN_CFW_EFS_SERVICE_EXPORT_MODE(1U);
    } else if (subcommand == 2U || subcommand == 3U) {
        if (subcommand == 3U)
            open_cfw_efs_service_reply(
                OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, 3U,
                OPEN_CFW_EFS_SERVICE_OK);
        open_cfw_efs_service_reset(transfer);
        return;
    } else if (subcommand != 1U) return;

    if (transfer->is_start == 0U || transfer->open == 0U) return;
    amount = transfer->remaining > OPEN_CFW_EFS_SERVICE_CHUNK_BYTES ?
        OPEN_CFW_EFS_SERVICE_CHUNK_BYTES : transfer->remaining;
    if (amount == 0U) {
        open_cfw_efs_service_reset(transfer);
        return;
    }
    open_cfw_efs_service_zero(buffer, OPEN_CFW_EFS_SERVICE_CHUNK_BYTES);
    read = OPEN_CFW_EFS_SERVICE_FILE_READ(
        buffer, 1U, amount, transfer->handle);
    if (read != amount || OPEN_CFW_EFS_SERVICE_SEND_RAW(1U,
            OPEN_CFW_EFS_SERVICE_EXPORT_DATA, buffer,
            (uint16_t)read) != 0) {
        open_cfw_efs_service_reset(transfer);
        return;
    }
    transfer->chunk_length = read;
    transfer->transferred += read;
    transfer->remaining = transfer->file_size - transfer->transferred;
    open_cfw_efs_service_update_progress(transfer);
    if (transfer->remaining == 0U) open_cfw_efs_service_reset(transfer);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_DISPATCH)
__attribute__((used, noinline))
int EFS_FrameDispatch(
    uint8_t command, const uint8_t *payload, uint16_t length)
{
    if (payload == 0 || length == 0U) return 11;
    if (command == OPEN_CFW_EFS_SERVICE_IMPORT_CONTROL)
        _efsFileCmdParse(payload[0], payload + 1U,
            (uint16_t)(length - 1U), 0U);
    else if (command == OPEN_CFW_EFS_SERVICE_IMPORT_DATA)
        _efsFileRawDataParse(payload, length);
    else if (command == OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL ||
            command == OPEN_CFW_EFS_SERVICE_EXPORT_DATA)
        _efsExportFileParse(payload[0], payload + 1U,
            (uint16_t)(length - 1U));
    return 0;
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS4)
__attribute__((used, noinline))
uint32_t EFS_NotifyStatus4(uint8_t command)
{
    if (command == OPEN_CFW_EFS_SERVICE_IMPORT_DATA)
        open_cfw_efs_service_reply(command, 1U, 4U);
    return 0x401U;
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS2)
__attribute__((used, noinline))
uint32_t EFS_NotifyStatus2(uint8_t command)
{
    if (command == OPEN_CFW_EFS_SERVICE_IMPORT_DATA)
        open_cfw_efs_service_reply(command, 1U, 2U);
    return 0x201U;
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_STATUS5)
__attribute__((used, noinline))
uint32_t EFS_NotifyStatus5(uint8_t command)
{
    if (command == OPEN_CFW_EFS_SERVICE_IMPORT_DATA)
        open_cfw_efs_service_reply(command, 1U, 5U);
    return 0x501U;
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_ACTIVE)
__attribute__((used, noinline))
uint8_t EFS_TransferActive(void)
{
    return (uint8_t)(OPEN_CFW_EFS_SERVICE_TRANSFER.is_start == 1U);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_INIT)
__attribute__((used, noinline))
void EFS_ServiceInit(void)
{
    OPEN_CFW_EFS_SERVICE_REGISTER(
        0x400U, OPEN_CFW_EFS_SERVICE_DISPATCH_CALLBACK, 1U);
}
#endif

#if defined(OPEN_CFW_EFS_SERVICE_INCLUDE_CANCEL)
__attribute__((used, noinline))
void EFS_CancelExport(
    int32_t reason, const uint8_t *source, uint32_t detail0, uint32_t detail1)
{
    open_cfw_efs_transfer *transfer = &OPEN_CFW_EFS_SERVICE_TRANSFER;
    (void)reason;
    (void)source;
    (void)detail0;
    (void)detail1;
    if (OPEN_CFW_EFS_SERVICE_EXPORT_ACTIVE != 0U) {
        open_cfw_efs_service_reply(
            OPEN_CFW_EFS_SERVICE_EXPORT_CONTROL, 3U, 8U);
        open_cfw_efs_service_reset(transfer);
    }
}
#endif
