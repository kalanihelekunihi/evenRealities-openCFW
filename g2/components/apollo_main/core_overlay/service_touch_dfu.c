/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/input/touchDFU/service_touch_dfu.c. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_TOUCH_DFU_SELECTOR
#define OPEN_CFW_TOUCH_DFU_SELECTOR 0
#endif

enum {
    OPEN_CFW_TOUCH_OK = 0,
    OPEN_CFW_TOUCH_ERROR = -1,
    OPEN_CFW_TOUCH_NO_UPGRADE = 1,
    OPEN_CFW_TOUCH_FRAME_START = 0x01,
    OPEN_CFW_TOUCH_FRAME_TERMINATOR = 0x17,
    OPEN_CFW_TOUCH_FRAME_OVERHEAD = 7,
    OPEN_CFW_TOUCH_PAYLOAD_MAX = 32,
    OPEN_CFW_TOUCH_REPLY_MAX = 15,
    OPEN_CFW_TOUCH_REPLY_RETRIES = 100,
    OPEN_CFW_TOUCH_PACKET_BYTES = 32,
    OPEN_CFW_TOUCH_PROGRAM_BYTES = 128,
    OPEN_CFW_TOUCH_PACKAGE_HEADER_BYTES = 16,
    OPEN_CFW_TOUCH_RECORD_BYTES = 16,
    OPEN_CFW_TOUCH_RECORD_TYPE = 3,
    OPEN_CFW_TOUCH_PACKAGE_MAGIC = 0x4b505746u,
    OPEN_CFW_TOUCH_COMMAND_ENTER = 0x38,
    OPEN_CFW_TOUCH_COMMAND_META = 0x4c,
    OPEN_CFW_TOUCH_COMMAND_PACKET = 0x37,
    OPEN_CFW_TOUCH_COMMAND_PROGRAM = 0x49,
    OPEN_CFW_TOUCH_COMMAND_VERIFY = 0x31,
    OPEN_CFW_TOUCH_COMMAND_EXIT = 0x3b
};

typedef int32_t (*open_cfw_touch_register_write_fn)(
    uint8_t command, const void *data, uint16_t size);
typedef int32_t (*open_cfw_touch_register_read_fn)(
    uint8_t command, void *data, uint16_t size);
typedef int32_t (*open_cfw_touch_raw_write_fn)(
    const void *data, uint16_t size);
typedef int32_t (*open_cfw_touch_raw_read_fn)(void *data, uint16_t size);

typedef struct {
    open_cfw_touch_register_write_fn register_write;
    open_cfw_touch_register_read_fn register_read;
    open_cfw_touch_raw_write_fn raw_write;
    open_cfw_touch_raw_read_fn raw_read;
} open_cfw_touch_ops_t;

typedef struct {
    uint32_t type;
    uint32_t size;
    uint32_t file_offset;
    uint32_t crc32c;
} open_cfw_touch_record_t;

#ifndef OPEN_CFW_TOUCH_OPS
#define OPEN_CFW_TOUCH_OPS \
    ((open_cfw_touch_ops_t *)(uintptr_t)0x20073e24u)
#endif
#ifndef OPEN_CFW_TOUCH_FILE_HANDLE
#define OPEN_CFW_TOUCH_FILE_HANDLE (*(uintptr_t *)(uintptr_t)0x20074998u)
#endif
#ifndef OPEN_CFW_TOUCH_FIRMWARE_BUFFER
#define OPEN_CFW_TOUCH_FIRMWARE_BUFFER \
    (*(uint8_t **)(uintptr_t)0x2007499cu)
#endif
#ifndef OPEN_CFW_TOUCH_FIRMWARE_SIZE
#define OPEN_CFW_TOUCH_FIRMWARE_SIZE (*(uint32_t *)(uintptr_t)0x200749a0u)
#endif
#ifndef OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE
#define OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE \
    (*(uint32_t *)(uintptr_t)0x200739bcu)
#endif

#ifndef OPEN_CFW_TOUCH_FILE_OPEN
uintptr_t open_cfw_file_open(const char *path, const char *mode);
#define OPEN_CFW_TOUCH_FILE_OPEN(path, mode) open_cfw_file_open((path), (mode))
#endif
#ifndef OPEN_CFW_TOUCH_FILE_READ
uint32_t open_cfw_file_read(void *data, uint32_t element_size,
    uint32_t element_count, uintptr_t file);
#define OPEN_CFW_TOUCH_FILE_READ(data, size, file) \
    open_cfw_file_read((data), 1u, (size), (file))
#endif
#ifndef OPEN_CFW_TOUCH_FILE_SEEK
int32_t open_cfw_file_seek(uintptr_t file, int32_t offset, uint32_t origin);
#define OPEN_CFW_TOUCH_FILE_SEEK(file, offset) \
    open_cfw_file_seek((file), (int32_t)(offset), 0u)
#endif
#ifndef OPEN_CFW_TOUCH_FILE_CLOSE
void open_cfw_file_close(uintptr_t file);
#define OPEN_CFW_TOUCH_FILE_CLOSE(file) open_cfw_file_close((file))
#endif
#ifndef OPEN_CFW_TOUCH_ALLOCATE
void *open_cfw_tlsf_malloc(uint32_t size);
#define OPEN_CFW_TOUCH_ALLOCATE(size) open_cfw_tlsf_malloc((size))
#endif
#ifndef OPEN_CFW_TOUCH_FREE
void open_cfw_tlsf_free(void *pointer);
#define OPEN_CFW_TOUCH_FREE(pointer) open_cfw_tlsf_free((pointer))
#endif
#ifndef OPEN_CFW_TOUCH_DELAY
uint32_t open_cfw_cmsis_delay(uint32_t ticks);
#define OPEN_CFW_TOUCH_DELAY(ticks) ((void)open_cfw_cmsis_delay((ticks)))
#endif
#ifndef OPEN_CFW_TOUCH_RESET
void open_cfw_cy8c_reset(void);
#define OPEN_CFW_TOUCH_RESET() open_cfw_cy8c_reset()
#endif
#ifndef OPEN_CFW_TOUCH_SWITCH_TO_DFU
int32_t open_cfw_cy8c_switch_to_dfu(void);
#define OPEN_CFW_TOUCH_SWITCH_TO_DFU() open_cfw_cy8c_switch_to_dfu()
#endif
#ifndef OPEN_CFW_TOUCH_READ_CURRENT_VERSION
int32_t open_cfw_cy8c_prepare_proximity_baseline(uint32_t *version);
#define OPEN_CFW_TOUCH_READ_CURRENT_VERSION(version) \
    open_cfw_cy8c_prepare_proximity_baseline((version))
#endif

uint16_t open_cfw_touch_frame_read_u16(const uint8_t *source);
void open_cfw_touch_frame_write_u16(uint8_t *destination, uint16_t value);
uint8_t *open_cfw_touch_frame_payload(uint8_t *frame);
uint8_t *open_cfw_touch_frame_terminator(uint8_t *frame,
    uint16_t payload_size);
uint8_t open_cfw_touch_frame_command(const uint8_t *frame);
uint16_t open_cfw_touch_frame_payload_length(const uint8_t *frame);
uint16_t open_cfw_touch_frame_checksum(const uint8_t *frame,
    uint16_t payload_size);
bool open_cfw_touch_frame_has_terminator(const uint8_t *frame,
    uint16_t payload_size);
void open_cfw_touch_frame_init(uint8_t *frame);
void open_cfw_touch_frame_set_command(uint8_t *frame, uint8_t command);
void open_cfw_touch_frame_set_payload_length(uint8_t *frame,
    uint16_t payload_size);
void open_cfw_touch_frame_set_checksum(uint8_t *frame,
    uint16_t payload_size, uint16_t checksum);
void open_cfw_touch_frame_set_terminator(uint8_t *frame,
    uint16_t payload_size);
uint16_t open_cfw_touch_frame_checksum16(const uint8_t *frame,
    uint16_t payload_size);
uint8_t open_cfw_touch_validate_reply(uint16_t received_size,
    const uint8_t *frame, bool *valid);
int32_t open_cfw_touch_receive_reply_retry(open_cfw_touch_ops_t *ops,
    uint8_t *reply, uint16_t capacity);
uint32_t open_cfw_touch_crc32c(const uint8_t *data, uint32_t size);
int32_t open_cfw_touch_build_and_send_frame(open_cfw_touch_ops_t *ops,
    uint8_t command, const uint8_t *payload, uint16_t payload_size);
int32_t open_cfw_touch_enter_dfu(void);
int32_t open_cfw_touch_set_app_meta(uint32_t application_size);
int32_t open_cfw_touch_send_one_packet(const uint8_t *data, uint16_t size);
int32_t open_cfw_touch_program_data(uint32_t offset, uint32_t crc32c);
int32_t open_cfw_touch_verify_app(void);
int32_t open_cfw_touch_exit_dfu(void);
int32_t open_cfw_touch_send_app_file(const uint8_t *data, uint32_t size);
void open_cfw_touch_free_firmware_memory(void);
int32_t open_cfw_touch_get_package_version(uint32_t *version);
int32_t open_cfw_touch_load_package(void);
int32_t open_cfw_touch_format_version(uint32_t version, char *output,
    uint32_t capacity);
int32_t open_cfw_touch_is_upgrade_needed(uint32_t current,
    uint32_t package);
int32_t open_cfw_touch_log_current_version(uint32_t *version);
int32_t open_cfw_touch_update_firmware_check(bool force);

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_touch_read_u32(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_touch_write_u32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static __attribute__((always_inline, unused)) inline void open_cfw_touch_copy(
    uint8_t *destination, const uint8_t *source, uint32_t size)
{
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline, unused)) inline void open_cfw_touch_fill(
    uint8_t *destination, uint8_t value, uint32_t size)
{
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        destination[index] = value;
    }
}

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 1
__attribute__((used, noinline))
uint16_t open_cfw_touch_frame_read_u16(const uint8_t *source)
{
    if (source == NULL) return 0u;
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8));
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 2
__attribute__((used, noinline))
void open_cfw_touch_frame_write_u16(uint8_t *destination, uint16_t value)
{
    if (destination != NULL) {
        destination[0] = (uint8_t)value;
        destination[1] = (uint8_t)(value >> 8);
    }
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 3
__attribute__((used, noinline))
uint8_t *open_cfw_touch_frame_payload(uint8_t *frame)
{
    return frame == NULL ? NULL : frame + 4;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 4
__attribute__((used, noinline))
uint8_t *open_cfw_touch_frame_terminator(uint8_t *frame,
    uint16_t payload_size)
{
    return frame == NULL ? NULL : frame + payload_size + 6u;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 5
__attribute__((used, noinline))
uint8_t open_cfw_touch_frame_command(const uint8_t *frame)
{
    return frame == NULL ? 0u : frame[1];
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 6
__attribute__((used, noinline))
uint16_t open_cfw_touch_frame_payload_length(const uint8_t *frame)
{
    return frame == NULL ? 0u : open_cfw_touch_frame_read_u16(frame + 2);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 7
__attribute__((used, noinline))
uint16_t open_cfw_touch_frame_checksum(const uint8_t *frame,
    uint16_t payload_size)
{
    return frame == NULL ? 0u :
        open_cfw_touch_frame_read_u16(frame + payload_size + 4u);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 8
__attribute__((used, noinline))
bool open_cfw_touch_frame_has_terminator(const uint8_t *frame,
    uint16_t payload_size)
{
    return frame != NULL && frame[payload_size + 6u] ==
        OPEN_CFW_TOUCH_FRAME_TERMINATOR;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 9
__attribute__((used, noinline))
void open_cfw_touch_frame_init(uint8_t *frame)
{
    if (frame != NULL) frame[0] = OPEN_CFW_TOUCH_FRAME_START;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 10
__attribute__((used, noinline))
void open_cfw_touch_frame_set_command(uint8_t *frame, uint8_t command)
{
    if (frame != NULL) frame[1] = command;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 11
__attribute__((used, noinline))
void open_cfw_touch_frame_set_payload_length(uint8_t *frame,
    uint16_t payload_size)
{
    if (frame != NULL) open_cfw_touch_frame_write_u16(frame + 2, payload_size);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 12
__attribute__((used, noinline))
void open_cfw_touch_frame_set_checksum(uint8_t *frame,
    uint16_t payload_size, uint16_t checksum)
{
    if (frame != NULL) {
        open_cfw_touch_frame_write_u16(frame + payload_size + 4u, checksum);
    }
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 13
__attribute__((used, noinline))
void open_cfw_touch_frame_set_terminator(uint8_t *frame,
    uint16_t payload_size)
{
    if (frame != NULL) {
        frame[payload_size + 6u] = OPEN_CFW_TOUCH_FRAME_TERMINATOR;
    }
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 14
__attribute__((used, noinline))
uint16_t open_cfw_touch_frame_checksum16(const uint8_t *frame,
    uint16_t payload_size)
{
    uint16_t sum = 0u;
    uint32_t count = (uint32_t)payload_size + 4u;
    uint32_t index;
    if (frame == NULL) return 0u;
    for (index = 0u; index < count; ++index) sum = (uint16_t)(sum + frame[index]);
    return (uint16_t)(0u - sum);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 15
__attribute__((used, noinline))
uint8_t open_cfw_touch_validate_reply(uint16_t received_size,
    const uint8_t *frame, bool *valid)
{
    uint16_t payload_size;
    if (valid != NULL) *valid = false;
    if (frame == NULL || valid == NULL || received_size < 7u ||
        frame[0] != OPEN_CFW_TOUCH_FRAME_START) return 0xaau;
    payload_size = open_cfw_touch_frame_payload_length(frame);
    if ((uint32_t)payload_size + 7u > received_size ||
        (uint32_t)payload_size + 7u > OPEN_CFW_TOUCH_REPLY_MAX) return 3u;
    if (!open_cfw_touch_frame_has_terminator(frame, payload_size)) return 4u;
    if (open_cfw_touch_frame_checksum(frame, payload_size) !=
        open_cfw_touch_frame_checksum16(frame, payload_size)) return 8u;
    *valid = true;
    return open_cfw_touch_frame_command(frame);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 16
__attribute__((used, noinline))
int32_t open_cfw_touch_receive_reply_retry(open_cfw_touch_ops_t *ops,
    uint8_t *reply, uint16_t capacity)
{
    uint32_t attempt;
    if (ops == NULL || ops->raw_read == NULL || reply == NULL ||
        capacity < OPEN_CFW_TOUCH_REPLY_MAX) return OPEN_CFW_TOUCH_ERROR;
    for (attempt = 0u; attempt < OPEN_CFW_TOUCH_REPLY_RETRIES; ++attempt) {
        bool valid = false;
        int32_t status;
        OPEN_CFW_TOUCH_DELAY(1u);
        status = ops->raw_read(reply, OPEN_CFW_TOUCH_REPLY_MAX);
        if (status == 0) {
            (void)open_cfw_touch_validate_reply(
                OPEN_CFW_TOUCH_REPLY_MAX, reply, &valid);
            if (valid) return OPEN_CFW_TOUCH_OK;
        }
    }
    return OPEN_CFW_TOUCH_ERROR;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 17
__attribute__((used, noinline))
uint32_t open_cfw_touch_crc32c(const uint8_t *data, uint32_t size)
{
    uint32_t crc = 0xffffffffu;
    uint32_t index;
    uint32_t bit;
    if (data == NULL && size != 0u) return 0u;
    for (index = 0u; index < size; ++index) {
        crc ^= data[index];
        for (bit = 0u; bit < 8u; ++bit) {
            crc = (crc >> 1) ^ ((0u - (crc & 1u)) & 0x82f63b78u);
        }
    }
    return ~crc;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 18
__attribute__((used, noinline))
int32_t open_cfw_touch_build_and_send_frame(open_cfw_touch_ops_t *ops,
    uint8_t command, const uint8_t *payload, uint16_t payload_size)
{
    uint8_t frame[OPEN_CFW_TOUCH_PAYLOAD_MAX + OPEN_CFW_TOUCH_FRAME_OVERHEAD];
    uint16_t checksum;
    if (ops == NULL || ops->raw_write == NULL ||
        payload_size > OPEN_CFW_TOUCH_PAYLOAD_MAX ||
        (payload_size != 0u && payload == NULL)) return OPEN_CFW_TOUCH_ERROR;
    open_cfw_touch_fill(frame, 0u, sizeof(frame));
    open_cfw_touch_frame_init(frame);
    open_cfw_touch_frame_set_command(frame, command);
    open_cfw_touch_frame_set_payload_length(frame, payload_size);
    if (payload_size != 0u) {
        open_cfw_touch_copy(open_cfw_touch_frame_payload(frame), payload,
            payload_size);
    }
    checksum = open_cfw_touch_frame_checksum16(frame, payload_size);
    open_cfw_touch_frame_set_checksum(frame, payload_size, checksum);
    open_cfw_touch_frame_set_terminator(frame, payload_size);
    return ops->raw_write(frame,
        (uint16_t)(payload_size + OPEN_CFW_TOUCH_FRAME_OVERHEAD));
}
#endif

static __attribute__((always_inline, unused)) inline int32_t
open_cfw_touch_send_and_receive(uint8_t command, const uint8_t *payload,
    uint16_t payload_size)
{
    uint8_t reply[OPEN_CFW_TOUCH_REPLY_MAX];
    int32_t status;
    open_cfw_touch_fill(reply, 0u, sizeof(reply));
    status = open_cfw_touch_build_and_send_frame(
        OPEN_CFW_TOUCH_OPS, command, payload, payload_size);
    if (status != 0) return status;
    return open_cfw_touch_receive_reply_retry(
        OPEN_CFW_TOUCH_OPS, reply, sizeof(reply));
}

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 19
__attribute__((used, noinline))
int32_t open_cfw_touch_enter_dfu(void)
{
    uint8_t payload[4];
    open_cfw_touch_write_u32(payload, 0x01020304u);
    return open_cfw_touch_send_and_receive(
        OPEN_CFW_TOUCH_COMMAND_ENTER, payload, sizeof(payload));
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 20
__attribute__((used, noinline))
int32_t open_cfw_touch_set_app_meta(uint32_t application_size)
{
    uint8_t payload[9];
    payload[0] = 1u;
    payload[1] = 0u;
    payload[2] = 0x33u;
    payload[3] = 0u;
    payload[4] = 0u;
    open_cfw_touch_write_u32(payload + 5, application_size);
    return open_cfw_touch_send_and_receive(
        OPEN_CFW_TOUCH_COMMAND_META, payload, sizeof(payload));
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 21
__attribute__((used, noinline))
int32_t open_cfw_touch_send_one_packet(const uint8_t *data, uint16_t size)
{
    if (data == NULL || size > OPEN_CFW_TOUCH_PACKET_BYTES) return 3;
    return open_cfw_touch_send_and_receive(
        OPEN_CFW_TOUCH_COMMAND_PACKET, data, size);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 22
__attribute__((used, noinline))
int32_t open_cfw_touch_program_data(uint32_t offset, uint32_t crc32c)
{
    uint8_t payload[8];
    open_cfw_touch_write_u32(payload, offset + 0x3300u);
    open_cfw_touch_write_u32(payload + 4, crc32c);
    return open_cfw_touch_send_and_receive(
        OPEN_CFW_TOUCH_COMMAND_PROGRAM, payload, sizeof(payload));
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 23
__attribute__((used, noinline))
int32_t open_cfw_touch_verify_app(void)
{
    uint8_t payload = 1u;
    return open_cfw_touch_send_and_receive(
        OPEN_CFW_TOUCH_COMMAND_VERIFY, &payload, 1u);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 24
__attribute__((used, noinline))
int32_t open_cfw_touch_exit_dfu(void)
{
    return open_cfw_touch_build_and_send_frame(
        OPEN_CFW_TOUCH_OPS, OPEN_CFW_TOUCH_COMMAND_EXIT, NULL, 0u);
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 25
__attribute__((used, noinline))
int32_t open_cfw_touch_send_app_file(const uint8_t *data, uint32_t size)
{
    uint8_t block[OPEN_CFW_TOUCH_PROGRAM_BYTES];
    uint32_t block_count;
    uint32_t block_index;
    if (data == NULL || size == 0u || size > 0xffff80u) return OPEN_CFW_TOUCH_ERROR;
    block_count = (size + OPEN_CFW_TOUCH_PROGRAM_BYTES - 1u) /
        OPEN_CFW_TOUCH_PROGRAM_BYTES;
    for (block_index = 0u; block_index < block_count; ++block_index) {
        uint32_t block_offset = block_index * OPEN_CFW_TOUCH_PROGRAM_BYTES;
        uint32_t remaining = size - block_offset;
        uint32_t used = remaining < OPEN_CFW_TOUCH_PROGRAM_BYTES ? remaining :
            OPEN_CFW_TOUCH_PROGRAM_BYTES;
        uint32_t packet;
        int32_t status;
        open_cfw_touch_fill(block, 0xffu, sizeof(block));
        open_cfw_touch_copy(block, data + block_offset, used);
        for (packet = 0u; packet < 4u; ++packet) {
            status = open_cfw_touch_send_one_packet(
                block + packet * OPEN_CFW_TOUCH_PACKET_BYTES,
                OPEN_CFW_TOUCH_PACKET_BYTES);
            if (status != 0) return status;
        }
        status = open_cfw_touch_program_data(block_offset,
            open_cfw_touch_crc32c(block, sizeof(block)));
        if (status != 0) return status;
    }
    return OPEN_CFW_TOUCH_OK;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 26
__attribute__((used, noinline))
void open_cfw_touch_free_firmware_memory(void)
{
    if (OPEN_CFW_TOUCH_FIRMWARE_BUFFER != NULL) {
        OPEN_CFW_TOUCH_FREE(OPEN_CFW_TOUCH_FIRMWARE_BUFFER);
        OPEN_CFW_TOUCH_FIRMWARE_BUFFER = NULL;
        OPEN_CFW_TOUCH_FIRMWARE_SIZE = 0u;
    }
}
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_touch_package_path(char path[20], char mode[3])
{
    path[0]='/'; path[1]='f'; path[2]='i'; path[3]='r'; path[4]='m';
    path[5]='w'; path[6]='a'; path[7]='r'; path[8]='e'; path[9]='/';
    path[10]='t'; path[11]='o'; path[12]='u'; path[13]='c'; path[14]='h';
    path[15]='.'; path[16]='b'; path[17]='i'; path[18]='n'; path[19]=0;
    mode[0]='r'; mode[1]='b'; mode[2]=0;
}

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 27
__attribute__((used, noinline))
int32_t open_cfw_touch_get_package_version(uint32_t *version)
{
    char path[20];
    char mode[3];
    uint8_t header[OPEN_CFW_TOUCH_PACKAGE_HEADER_BYTES];
    uintptr_t file;
    int32_t status = OPEN_CFW_TOUCH_ERROR;
    if (version == NULL) return OPEN_CFW_TOUCH_ERROR;
    open_cfw_touch_package_path(path, mode);
    file = OPEN_CFW_TOUCH_FILE_OPEN(path, mode);
    if (file == 0u) return OPEN_CFW_TOUCH_ERROR;
    if (OPEN_CFW_TOUCH_FILE_READ(header, sizeof(header), file) ==
            (uint32_t)sizeof(header) &&
        open_cfw_touch_read_u32(header) == OPEN_CFW_TOUCH_PACKAGE_MAGIC) {
        *version = open_cfw_touch_read_u32(header + 4);
        status = OPEN_CFW_TOUCH_OK;
    }
    OPEN_CFW_TOUCH_FILE_CLOSE(file);
    return status;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 28
__attribute__((used, noinline))
int32_t open_cfw_touch_load_package(void)
{
    char path[20];
    char mode[3];
    uint8_t header[OPEN_CFW_TOUCH_PACKAGE_HEADER_BYTES];
    uint8_t raw_record[OPEN_CFW_TOUCH_RECORD_BYTES];
    open_cfw_touch_record_t firmware = {0u, 0u, 0u, 0u};
    uint32_t count;
    uint32_t index;
    int32_t status = OPEN_CFW_TOUCH_ERROR;
    open_cfw_touch_free_firmware_memory();
    if (OPEN_CFW_TOUCH_FILE_HANDLE != 0u) {
        OPEN_CFW_TOUCH_FILE_CLOSE(OPEN_CFW_TOUCH_FILE_HANDLE);
        OPEN_CFW_TOUCH_FILE_HANDLE = 0u;
    }
    open_cfw_touch_package_path(path, mode);
    OPEN_CFW_TOUCH_FILE_HANDLE = OPEN_CFW_TOUCH_FILE_OPEN(path, mode);
    if (OPEN_CFW_TOUCH_FILE_HANDLE == 0u ||
        OPEN_CFW_TOUCH_FILE_READ(header, sizeof(header),
            OPEN_CFW_TOUCH_FILE_HANDLE) != (uint32_t)sizeof(header) ||
        open_cfw_touch_read_u32(header) != OPEN_CFW_TOUCH_PACKAGE_MAGIC) goto done;
    count = open_cfw_touch_read_u32(header + 8);
    if (count == 0u || count > 64u) goto done;
    for (index = 0u; index < count; ++index) {
        open_cfw_touch_record_t record;
        if (OPEN_CFW_TOUCH_FILE_READ(raw_record, sizeof(raw_record),
                OPEN_CFW_TOUCH_FILE_HANDLE) != (uint32_t)sizeof(raw_record)) goto done;
        record.type = open_cfw_touch_read_u32(raw_record);
        record.size = open_cfw_touch_read_u32(raw_record + 4);
        record.file_offset = open_cfw_touch_read_u32(raw_record + 8);
        record.crc32c = open_cfw_touch_read_u32(raw_record + 12);
        if (record.type == OPEN_CFW_TOUCH_RECORD_TYPE) firmware = record;
    }
    if (firmware.type != OPEN_CFW_TOUCH_RECORD_TYPE || firmware.size <= 4u ||
        firmware.file_offset < OPEN_CFW_TOUCH_PACKAGE_HEADER_BYTES) goto done;
    OPEN_CFW_TOUCH_FIRMWARE_BUFFER =
        (uint8_t *)OPEN_CFW_TOUCH_ALLOCATE(firmware.size);
    if (OPEN_CFW_TOUCH_FIRMWARE_BUFFER == NULL) goto done;
    if (OPEN_CFW_TOUCH_FILE_SEEK(OPEN_CFW_TOUCH_FILE_HANDLE,
            firmware.file_offset) != 0 ||
        OPEN_CFW_TOUCH_FILE_READ(OPEN_CFW_TOUCH_FIRMWARE_BUFFER,
            firmware.size, OPEN_CFW_TOUCH_FILE_HANDLE) != firmware.size ||
        open_cfw_touch_crc32c(OPEN_CFW_TOUCH_FIRMWARE_BUFFER,
            firmware.size) != firmware.crc32c) goto done;
    OPEN_CFW_TOUCH_FIRMWARE_SIZE = firmware.size - 4u;
    status = OPEN_CFW_TOUCH_OK;
done:
    if (OPEN_CFW_TOUCH_FILE_HANDLE != 0u) {
        OPEN_CFW_TOUCH_FILE_CLOSE(OPEN_CFW_TOUCH_FILE_HANDLE);
        OPEN_CFW_TOUCH_FILE_HANDLE = 0u;
    }
    if (status != OPEN_CFW_TOUCH_OK) open_cfw_touch_free_firmware_memory();
    return status;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 29
__attribute__((used, noinline))
int32_t open_cfw_touch_format_version(uint32_t version, char *output,
    uint32_t capacity)
{
    uint8_t parts[4];
    uint32_t position = 0u;
    uint32_t part;
    if (output == NULL || capacity < 16u) return OPEN_CFW_TOUCH_ERROR;
    parts[0]=(uint8_t)(version>>24); parts[1]=(uint8_t)(version>>16);
    parts[2]=(uint8_t)(version>>8); parts[3]=(uint8_t)version;
    for (part=0u; part<4u; ++part) {
        uint8_t value=parts[part];
        if (value>=100u) output[position++]=(char)('0'+value/100u);
        if (value>=10u) output[position++]=(char)('0'+(value/10u)%10u);
        output[position++]=(char)('0'+value%10u);
        if (part!=3u) output[position++]='.';
    }
    output[position]=0;
    return (int32_t)position;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 30
__attribute__((used, noinline))
int32_t open_cfw_touch_is_upgrade_needed(uint32_t current, uint32_t package)
{
    return current == package ? 0 : 1;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 31
__attribute__((used, noinline))
int32_t open_cfw_touch_log_current_version(uint32_t *version)
{
    uint32_t current = 0u;
    int32_t status;
    OPEN_CFW_TOUCH_RESET();
    status = OPEN_CFW_TOUCH_READ_CURRENT_VERSION(&current);
    if (status == 0) OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE = current;
    if (version != NULL) *version = current;
    return status;
}
#endif

#if OPEN_CFW_TOUCH_DFU_SELECTOR == 0 || OPEN_CFW_TOUCH_DFU_SELECTOR == 32
__attribute__((used, noinline))
int32_t open_cfw_touch_update_firmware_check(bool force)
{
    uint32_t current = 0u;
    uint32_t package = 0u;
    int32_t status;
    OPEN_CFW_TOUCH_RESET();
    if (OPEN_CFW_TOUCH_READ_CURRENT_VERSION(&current) != 0) force = true;
    else OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE = current;
    if (open_cfw_touch_get_package_version(&package) != 0)
        return OPEN_CFW_TOUCH_ERROR;
    if (!force && open_cfw_touch_is_upgrade_needed(current, package) == 0)
        return OPEN_CFW_TOUCH_NO_UPGRADE;
    if (open_cfw_touch_load_package() != 0) return OPEN_CFW_TOUCH_ERROR;
    status = OPEN_CFW_TOUCH_SWITCH_TO_DFU();
    if (status == 0) {
        OPEN_CFW_TOUCH_DELAY(50u);
        status = open_cfw_touch_enter_dfu();
    }
    if (status == 0) status = open_cfw_touch_set_app_meta(
        OPEN_CFW_TOUCH_FIRMWARE_SIZE);
    if (status == 0) status = open_cfw_touch_send_app_file(
        OPEN_CFW_TOUCH_FIRMWARE_BUFFER, OPEN_CFW_TOUCH_FIRMWARE_SIZE);
    if (status == 0) status = open_cfw_touch_verify_app();
    if (status == 0) status = open_cfw_touch_exit_dfu();
    if (status == 0) {
        OPEN_CFW_TOUCH_DELAY(500u);
        OPEN_CFW_TOUCH_RESET();
        if (OPEN_CFW_TOUCH_READ_CURRENT_VERSION(&current) == 0)
            OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE = current;
    }
    open_cfw_touch_free_firmware_memory();
    return status;
}
#endif
