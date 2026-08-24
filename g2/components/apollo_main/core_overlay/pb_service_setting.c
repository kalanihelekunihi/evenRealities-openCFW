/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the eleven linked G2 pb_service_setting.c
 * entries. Diagnostic-only logging is deliberately omitted. Message layout,
 * duplicate suppression, role gates, status construction, nanopb status
 * mapping, and service-9 transport behavior follow the authenticated object.
 */

typedef unsigned char open_cfw_pb_setting_u8;
typedef unsigned short open_cfw_pb_setting_u16;
typedef unsigned int open_cfw_pb_setting_u32;

typedef struct {
    void *callback;
    void *state;
    open_cfw_pb_setting_u32 bytes_left;
    const char *error;
} open_cfw_pb_setting_input;

struct open_cfw_pb_setting_output;
typedef open_cfw_pb_setting_u32 (*open_cfw_pb_setting_write_fn)(
    struct open_cfw_pb_setting_output *, const void *, open_cfw_pb_setting_u32);

struct open_cfw_pb_setting_output {
    open_cfw_pb_setting_write_fn write;
    void *context;
    open_cfw_pb_setting_u32 capacity;
    open_cfw_pb_setting_u32 length;
    const char *error;
};

#if !defined(OPEN_CFW_PB_SETTING_HOST_ALL)
_Static_assert(sizeof(open_cfw_pb_setting_input) == 16U, "input ABI");
_Static_assert(sizeof(struct open_cfw_pb_setting_output) == 20U, "output ABI");
#endif

open_cfw_pb_setting_input open_cfw_nanopb_istream_from_buffer(
    const void *, open_cfw_pb_setting_u32);
open_cfw_pb_setting_u32 open_cfw_nanopb_decode(
    open_cfw_pb_setting_input *, const void *, void *);
open_cfw_pb_setting_u32 open_cfw_format_message_encode(
    void *, const void *, const void *);
int open_cfw_ble_msgtx_pb_send(
    open_cfw_pb_setting_u32, open_cfw_pb_setting_u32,
    const void *, open_cfw_pb_setting_u32);
int open_cfw_ble_msgtx_pb_notify(
    open_cfw_pb_setting_u32, open_cfw_pb_setting_u32,
    const void *, open_cfw_pb_setting_u32);

#ifndef OPEN_CFW_PB_SETTING_INPUT_FROM_BUFFER
#define OPEN_CFW_PB_SETTING_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_SETTING_DECODE
#define OPEN_CFW_PB_SETTING_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_SETTING_ENCODE
#define OPEN_CFW_PB_SETTING_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_SETTING_SEND
#define OPEN_CFW_PB_SETTING_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_SETTING_NOTIFY
#define OPEN_CFW_PB_SETTING_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#ifndef OPEN_CFW_PB_SETTING_ROLE
open_cfw_pb_setting_u32 open_cfw_pb_setting_role(void);
#define OPEN_CFW_PB_SETTING_ROLE() open_cfw_pb_setting_role()
#endif
#ifndef OPEN_CFW_PB_SETTING_CONFIG
void *open_cfw_pb_setting_config(void);
#define OPEN_CFW_PB_SETTING_CONFIG() open_cfw_pb_setting_config()
#endif
#ifndef OPEN_CFW_PB_SETTING_RUNTIME
void *open_cfw_pb_setting_runtime(void);
#define OPEN_CFW_PB_SETTING_RUNTIME() open_cfw_pb_setting_runtime()
#endif
#ifndef OPEN_CFW_PB_SETTING_REQUEST_LEFT_VERSION
void open_cfw_pb_setting_request_left_version(void);
#define OPEN_CFW_PB_SETTING_REQUEST_LEFT_VERSION() \
    open_cfw_pb_setting_request_left_version()
#endif
#ifndef OPEN_CFW_PB_SETTING_UNREAD_COUNT
open_cfw_pb_setting_u32 open_cfw_pb_setting_unread_count(void);
#define OPEN_CFW_PB_SETTING_UNREAD_COUNT() open_cfw_pb_setting_unread_count()
#endif

#ifndef OPEN_CFW_PB_SETTING_MESSAGE
#define OPEN_CFW_PB_SETTING_MESSAGE ((open_cfw_pb_setting_u8 *)0x200725A0U)
#endif
#ifndef OPEN_CFW_PB_SETTING_BUFFER
#define OPEN_CFW_PB_SETTING_BUFFER ((open_cfw_pb_setting_u8 *)0x200706ECU)
#endif
#ifndef OPEN_CFW_PB_SETTING_DESCRIPTOR
#define OPEN_CFW_PB_SETTING_DESCRIPTOR ((const void *)0x0077772CU)
#endif
#ifndef OPEN_CFW_PB_SETTING_LAST_COMMAND
#define OPEN_CFW_PB_SETTING_LAST_COMMAND \
    (*(volatile open_cfw_pb_setting_u32 *)0x20074860U)
#endif
#ifndef OPEN_CFW_PB_SETTING_LAST_MAGIC
#define OPEN_CFW_PB_SETTING_LAST_MAGIC \
    (*(volatile open_cfw_pb_setting_u32 *)0x20074864U)
#endif
#ifndef OPEN_CFW_PB_SETTING_DUPLICATE_MAGIC
#define OPEN_CFW_PB_SETTING_DUPLICATE_MAGIC \
    (*(volatile open_cfw_pb_setting_u32 *)0x20074868U)
#endif
#ifndef OPEN_CFW_PB_SETTING_NOTIFICATION_MAGIC
#define OPEN_CFW_PB_SETTING_NOTIFICATION_MAGIC \
    (*(volatile open_cfw_pb_setting_u32 *)0x2007486CU)
#endif
#ifndef OPEN_CFW_PB_SETTING_LOCAL_VERSION
#define OPEN_CFW_PB_SETTING_LOCAL_VERSION "2.2.6.10"
#endif

open_cfw_pb_setting_u32 setting_is_duplicate_message(open_cfw_pb_setting_u32);
open_cfw_pb_setting_u32 setting_build_full_status_package(void *);
open_cfw_pb_setting_u32 setting_respond_to_app(void *, open_cfw_pb_setting_u32 *);
open_cfw_pb_setting_u32 setting_respond_with_local_data(
    void *, open_cfw_pb_setting_u32 *);
open_cfw_pb_setting_u32 setting_notify_common(const void *);
void open_cfw_pb_service_setting_zero(void *, open_cfw_pb_setting_u32);
open_cfw_pb_setting_u32 open_cfw_pb_service_setting_buffer_write(
    struct open_cfw_pb_setting_output *, const void *, open_cfw_pb_setting_u32);

static __attribute__((always_inline, unused)) inline open_cfw_pb_setting_u32
open_cfw_pb_setting_load_u32(const open_cfw_pb_setting_u8 *data)
{
    return (open_cfw_pb_setting_u32)data[0] |
        ((open_cfw_pb_setting_u32)data[1] << 8) |
        ((open_cfw_pb_setting_u32)data[2] << 16) |
        ((open_cfw_pb_setting_u32)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_setting_store_u16(
    open_cfw_pb_setting_u8 *data, open_cfw_pb_setting_u32 value)
{
    data[0] = (open_cfw_pb_setting_u8)value;
    data[1] = (open_cfw_pb_setting_u8)(value >> 8);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_setting_store_u32(
    open_cfw_pb_setting_u8 *data, open_cfw_pb_setting_u32 value)
{
    data[0] = (open_cfw_pb_setting_u8)value;
    data[1] = (open_cfw_pb_setting_u8)(value >> 8);
    data[2] = (open_cfw_pb_setting_u8)(value >> 16);
    data[3] = (open_cfw_pb_setting_u8)(value >> 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_setting_copy_version(
    open_cfw_pb_setting_u8 *destination, const char *source)
{
    open_cfw_pb_setting_u32 index;
    for (index = 0U; index < 11U && source[index] != '\0'; ++index) {
        destination[index] = (open_cfw_pb_setting_u8)source[index];
    }
}

#if !defined(OPEN_CFW_PB_SETTING_HOST_ALL) && \
    !defined(OPEN_CFW_PB_SETTING_BUFFER_WRITE_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_ZERO_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_DUPLICATE_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_PARSE_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_RESPOND_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_BUILD_STATUS_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_RESPOND_LOCAL_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_RESPOND_SERIALIZE_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_RESPOND_LOCAL_SERIALIZE_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_NOTIFY_COMMON_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_NOTIFY_STATUS_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_NOTIFY_RECALIBRATION_ONLY) && \
    !defined(OPEN_CFW_PB_SETTING_NOTIFY_SILENT_ONLY)
#error "Select exactly one pb_service_setting leaf"
#endif

#if defined(OPEN_CFW_PB_SETTING_BUFFER_WRITE_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 open_cfw_pb_service_setting_buffer_write(
    struct open_cfw_pb_setting_output *output,
    const void *raw_data,
    open_cfw_pb_setting_u32 length)
{
    const open_cfw_pb_setting_u8 *data = raw_data;
    open_cfw_pb_setting_u8 *destination = output->context;
    open_cfw_pb_setting_u32 index;
    if (output->length > output->capacity ||
        length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = data[index];
    }
    return 1U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_ZERO_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
void open_cfw_pb_service_setting_zero(
    void *raw_data, open_cfw_pb_setting_u32 length)
{
    open_cfw_pb_setting_u8 *data = raw_data;
    open_cfw_pb_setting_u32 index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif
#if defined(OPEN_CFW_PB_SETTING_DUPLICATE_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_is_duplicate_message(
    open_cfw_pb_setting_u32 magic)
{
    if (magic == OPEN_CFW_PB_SETTING_DUPLICATE_MAGIC) {
        return 1U;
    }
    OPEN_CFW_PB_SETTING_DUPLICATE_MAGIC = magic;
    return 0U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_PARSE_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_parse_data_package(
    const void *data, open_cfw_pb_setting_u32 length, void *raw_message)
{
    open_cfw_pb_setting_u8 *message = raw_message;
    open_cfw_pb_setting_input input;
    if (data == (const void *)0 || message == (open_cfw_pb_setting_u8 *)0) {
        return 0U;
    }
    input = OPEN_CFW_PB_SETTING_INPUT_FROM_BUFFER(data, length);
    if (OPEN_CFW_PB_SETTING_DECODE(
            &input, OPEN_CFW_PB_SETTING_DESCRIPTOR, message) == 0U) {
        return 0U;
    }
    if (setting_is_duplicate_message(
            open_cfw_pb_setting_load_u32(message + 4U)) != 0U) {
        return 0U;
    }
    OPEN_CFW_PB_SETTING_LAST_COMMAND = message[0];
    OPEN_CFW_PB_SETTING_LAST_MAGIC =
        open_cfw_pb_setting_load_u32(message + 4U);
    return 1U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_RESPOND_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_respond_to_app(
    void *buffer, open_cfw_pb_setting_u32 *length)
{
    open_cfw_pb_setting_u8 *message = OPEN_CFW_PB_SETTING_MESSAGE;
    struct open_cfw_pb_setting_output output;
    if (buffer == (void *)0 || length == (open_cfw_pb_setting_u32 *)0 ||
        *length == 0U) {
        return 0U;
    }
    open_cfw_pb_service_setting_zero(message, 0x68U);
    message[0] = 1U;
    open_cfw_pb_setting_store_u32(message + 4U, OPEN_CFW_PB_SETTING_LAST_MAGIC);
    output.write = open_cfw_pb_service_setting_buffer_write;
    output.context = buffer;
    output.capacity = *length;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_SETTING_ENCODE(
            &output, OPEN_CFW_PB_SETTING_DESCRIPTOR, message) == 0U) {
        return 0U;
    }
    *length = output.length;
    return 1U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_BUILD_STATUS_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_build_full_status_package(void *raw_message)
{
    open_cfw_pb_setting_u8 *message = raw_message;
    const open_cfw_pb_setting_u8 *config;
    const open_cfw_pb_setting_u8 *runtime;
    const char *left_version;
    if (message == (open_cfw_pb_setting_u8 *)0) {
        return 0U;
    }
    open_cfw_pb_service_setting_zero(message, 0x68U);
    message[0] = 2U;
    open_cfw_pb_setting_store_u16(message + 8U, 4U);
    message[0x0CU] = 0U;
    config = OPEN_CFW_PB_SETTING_CONFIG();
    if (config == (const open_cfw_pb_setting_u8 *)0) {
        return 0U;
    }
    message[0x60U] = config[2U];
    message[0x10U] = config[1U];
    message[0x14U] = config[8U];
    message[0x18U] = config[9U];
    open_cfw_pb_setting_copy_version(
        message + 0x28U, OPEN_CFW_PB_SETTING_LOCAL_VERSION);
    runtime = OPEN_CFW_PB_SETTING_RUNTIME();
    left_version = runtime == (const open_cfw_pb_setting_u8 *)0 ?
        (const char *)0 : (const char *)runtime;
    if (left_version == (const char *)0 || left_version[0] == '\0') {
        OPEN_CFW_PB_SETTING_REQUEST_LEFT_VERSION();
    } else {
        open_cfw_pb_setting_copy_version(message + 0x1CU, left_version);
    }
    message[0x34U] = config[10U];
    open_cfw_pb_setting_store_u32(
        message + 0x38U, open_cfw_pb_setting_load_u32(config + 0x0CU));
    message[0x40U] = config[0x14U];
    if (runtime != (const open_cfw_pb_setting_u8 *)0) {
        open_cfw_pb_setting_store_u32(
            message + 0x44U, open_cfw_pb_setting_load_u32(runtime + 0x34U));
        open_cfw_pb_setting_store_u32(
            message + 0x48U, open_cfw_pb_setting_load_u32(runtime + 0x38U));
        open_cfw_pb_setting_store_u32(
            message + 0x4CU, open_cfw_pb_setting_load_u32(runtime + 0x3CU));
        message[0x50U] = runtime[0x15U];
        message[0x54U] = runtime[0x16U];
        message[0x58U] = runtime[0x17U];
        open_cfw_pb_setting_store_u32(
            message + 0x5CU, open_cfw_pb_setting_load_u32(runtime + 0x40U));
    }
    open_cfw_pb_setting_store_u32(
        message + 0x64U, OPEN_CFW_PB_SETTING_UNREAD_COUNT());
    return 1U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_RESPOND_LOCAL_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_respond_with_local_data(
    void *buffer, open_cfw_pb_setting_u32 *length)
{
    open_cfw_pb_setting_u8 *message = OPEN_CFW_PB_SETTING_MESSAGE;
    struct open_cfw_pb_setting_output output;
    if (buffer == (void *)0 || length == (open_cfw_pb_setting_u32 *)0 ||
        *length == 0U || setting_build_full_status_package(message) == 0U) {
        return 0U;
    }
    open_cfw_pb_setting_store_u32(message + 4U, OPEN_CFW_PB_SETTING_LAST_MAGIC);
    output.write = open_cfw_pb_service_setting_buffer_write;
    output.context = buffer;
    output.capacity = *length;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_SETTING_ENCODE(
            &output, OPEN_CFW_PB_SETTING_DESCRIPTOR, message) == 0U) {
        return 0U;
    }
    *length = output.length;
    return 1U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_RESPOND_SERIALIZE_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_respond_to_app_serialize(void)
{
    open_cfw_pb_setting_u32 length = 0x100U;
    if (OPEN_CFW_PB_SETTING_ROLE() != 1U) {
        return 0U;
    }
    if (OPEN_CFW_PB_SETTING_LAST_COMMAND == 0U) {
        return 1U;
    }
    open_cfw_pb_service_setting_zero(OPEN_CFW_PB_SETTING_BUFFER, 0x100U);
    if (setting_respond_to_app(OPEN_CFW_PB_SETTING_BUFFER, &length) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_SETTING_SEND(
        1U, 9U, OPEN_CFW_PB_SETTING_BUFFER, (open_cfw_pb_setting_u16)length);
    return 0U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_RESPOND_LOCAL_SERIALIZE_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_respond_with_local_data_serialize(void)
{
    open_cfw_pb_setting_u32 length = 0x100U;
    if (OPEN_CFW_PB_SETTING_ROLE() != 1U) {
        return 0U;
    }
    if (OPEN_CFW_PB_SETTING_LAST_COMMAND == 0U) {
        return 1U;
    }
    open_cfw_pb_service_setting_zero(OPEN_CFW_PB_SETTING_BUFFER, 0x100U);
    if (setting_respond_with_local_data(
            OPEN_CFW_PB_SETTING_BUFFER, &length) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_SETTING_SEND(
        1U, 9U, OPEN_CFW_PB_SETTING_BUFFER, (open_cfw_pb_setting_u16)length);
    return 0U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_NOTIFY_COMMON_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_notify_common(const void *raw_message)
{
    open_cfw_pb_setting_u8 *message = OPEN_CFW_PB_SETTING_MESSAGE;
    struct open_cfw_pb_setting_output output;
    if (OPEN_CFW_PB_SETTING_ROLE() != 1U) {
        return 0U;
    }
    if (raw_message == (const void *)0) {
        return 1U;
    }
    open_cfw_pb_service_setting_zero(message, 0x68U);
    {
        const open_cfw_pb_setting_u8 *source = raw_message;
        open_cfw_pb_setting_u32 index;
        for (index = 0U; index < 0x68U; ++index) {
            message[index] = source[index];
        }
    }
    OPEN_CFW_PB_SETTING_NOTIFICATION_MAGIC += 1U;
    open_cfw_pb_setting_store_u32(
        message + 4U, OPEN_CFW_PB_SETTING_NOTIFICATION_MAGIC);
    output.write = open_cfw_pb_service_setting_buffer_write;
    output.context = OPEN_CFW_PB_SETTING_BUFFER;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_SETTING_ENCODE(
            &output, OPEN_CFW_PB_SETTING_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_SETTING_NOTIFY(
        1U, 9U, OPEN_CFW_PB_SETTING_BUFFER,
        (open_cfw_pb_setting_u16)output.length);
    return 0U;
}
#endif
#if defined(OPEN_CFW_PB_SETTING_NOTIFY_STATUS_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
open_cfw_pb_setting_u32 setting_notify_device_status_to_app(void)
{
    open_cfw_pb_setting_u8 message[0x68U];
    if (OPEN_CFW_PB_SETTING_ROLE() != 1U) {
        return 0U;
    }
    open_cfw_pb_service_setting_zero(message, sizeof(message));
    if (setting_build_full_status_package(message) == 0U) {
        return 0x2BU;
    }
    return setting_notify_common(message);
}
#endif
#if defined(OPEN_CFW_PB_SETTING_NOTIFY_RECALIBRATION_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
void setting_notify_recalibration_status_to_app(open_cfw_pb_setting_u32 status)
{
    open_cfw_pb_setting_u8 message[0x68U];
    open_cfw_pb_service_setting_zero(message, sizeof(message));
    message[0] = 3U;
    open_cfw_pb_setting_store_u16(message + 8U, 5U);
    open_cfw_pb_setting_store_u16(message + 12U, 1U);
    open_cfw_pb_setting_store_u32(message + 16U, status);
    (void)setting_notify_common(message);
}
#endif
#if defined(OPEN_CFW_PB_SETTING_NOTIFY_SILENT_ONLY) || \
    defined(OPEN_CFW_PB_SETTING_HOST_ALL)
__attribute__((used, noinline))
void notify_silent_mode_to_app(open_cfw_pb_setting_u8 status)
{
    open_cfw_pb_setting_u8 message[0x68U];
    open_cfw_pb_service_setting_zero(message, sizeof(message));
    message[0] = 3U;
    open_cfw_pb_setting_store_u16(message + 8U, 5U);
    open_cfw_pb_setting_store_u16(message + 12U, 2U);
    open_cfw_pb_setting_store_u32(message + 16U, status);
    (void)setting_notify_common(message);
}
#endif
