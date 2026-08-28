/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the two authenticated G2 bootloader output
 * transport entries.  The implementation preserves the observed channel
 * table, 56-byte descriptor, lower-driver, and wait seams without claiming
 * upstream identity for this G2-specific service layer.
 */

typedef __UINT8_TYPE__ open_cfw_bootloader_elog_transport_u8;
typedef __UINT32_TYPE__ open_cfw_bootloader_elog_transport_u32;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_elog_transport_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_CHANNEL_COUNT = 4U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_CHANNEL_STRIDE = 28U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_HANDLE_OFFSET = 4U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_INITIALIZED_OFFSET = 24U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_COMPLETION_OFFSET = 25U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_TABLE_ADDRESS = 0x20000454U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_SIZE = 56U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_LENGTH_OFFSET = 4U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_FIELD_C_OFFSET = 12U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_FIELD_10_OFFSET = 16U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_OPERATION_OFFSET = 52U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ZERO_THUMB = 0x00415FF5U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_WRITE_THUMB = 0x0041F919U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_LOWER_START_THUMB = 0x004233E9U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_WAIT_THUMB = 0x0041F9E7U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_LOG_CHANNEL = 1U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_POLL_LIMIT = 1000U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_POLL_WAIT = 10U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_SUCCESS = 0U,
    OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ERROR = 1U
};

typedef void (*open_cfw_bootloader_elog_transport_zero_fn)(
    void *destination,
    open_cfw_bootloader_elog_transport_u32 size);
typedef open_cfw_bootloader_elog_transport_u32
(*open_cfw_bootloader_elog_transport_write_fn)(
    open_cfw_bootloader_elog_transport_u8 channel,
    const void *buffer,
    open_cfw_bootloader_elog_transport_u32 length);
typedef open_cfw_bootloader_elog_transport_u32
(*open_cfw_bootloader_elog_transport_start_fn)(
    void *handle,
    void *descriptor);
typedef void (*open_cfw_bootloader_elog_transport_wait_fn)(
    open_cfw_bootloader_elog_transport_u32 duration);

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
void open_cfw_bootloader_easylogger_transport_host_zero(
    void *destination,
    open_cfw_bootloader_elog_transport_u32 size);
open_cfw_bootloader_elog_transport_u8
open_cfw_bootloader_easylogger_transport_host_initialized(
    open_cfw_bootloader_elog_transport_u8 channel);
void open_cfw_bootloader_easylogger_transport_host_set_completion(
    open_cfw_bootloader_elog_transport_u8 channel,
    open_cfw_bootloader_elog_transport_u8 value);
open_cfw_bootloader_elog_transport_u8
open_cfw_bootloader_easylogger_transport_host_completion(
    open_cfw_bootloader_elog_transport_u8 channel);
open_cfw_bootloader_elog_transport_u32
open_cfw_bootloader_easylogger_transport_host_start(
    open_cfw_bootloader_elog_transport_u8 channel,
    const void *buffer,
    open_cfw_bootloader_elog_transport_u32 length,
    void *descriptor);
void open_cfw_bootloader_easylogger_transport_host_wait(
    open_cfw_bootloader_elog_transport_u32 duration);
#endif

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_transport_zero(
    void *destination,
    open_cfw_bootloader_elog_transport_u32 size)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    open_cfw_bootloader_easylogger_transport_host_zero(destination, size);
#else
    ((open_cfw_bootloader_elog_transport_zero_fn)
        (open_cfw_bootloader_elog_transport_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ZERO_THUMB)(destination, size);
#endif
}

static __attribute__((always_inline)) inline volatile
open_cfw_bootloader_elog_transport_u8 *
open_cfw_bootloader_easylogger_transport_channel(
    open_cfw_bootloader_elog_transport_u8 channel)
{
    return (volatile open_cfw_bootloader_elog_transport_u8 *)
        (open_cfw_bootloader_elog_transport_uintptr)(
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_TABLE_ADDRESS +
            (open_cfw_bootloader_elog_transport_u32)channel *
                OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_CHANNEL_STRIDE);
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_transport_u8
open_cfw_bootloader_easylogger_transport_initialized(
    open_cfw_bootloader_elog_transport_u8 channel)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    return open_cfw_bootloader_easylogger_transport_host_initialized(channel);
#else
    return open_cfw_bootloader_easylogger_transport_channel(channel)
        [OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_INITIALIZED_OFFSET];
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_transport_set_completion(
    open_cfw_bootloader_elog_transport_u8 channel,
    open_cfw_bootloader_elog_transport_u8 value)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    open_cfw_bootloader_easylogger_transport_host_set_completion(
        channel, value);
#else
    open_cfw_bootloader_easylogger_transport_channel(channel)
        [OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_COMPLETION_OFFSET] = value;
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_transport_u8
open_cfw_bootloader_easylogger_transport_completion(
    open_cfw_bootloader_elog_transport_u8 channel)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    return open_cfw_bootloader_easylogger_transport_host_completion(channel);
#else
    return open_cfw_bootloader_easylogger_transport_channel(channel)
        [OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_COMPLETION_OFFSET];
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_transport_u32
open_cfw_bootloader_easylogger_transport_start(
    open_cfw_bootloader_elog_transport_u8 channel,
    const void *buffer,
    open_cfw_bootloader_elog_transport_u32 length,
    void *descriptor)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    return open_cfw_bootloader_easylogger_transport_host_start(
        channel, buffer, length, descriptor);
#else
    volatile open_cfw_bootloader_elog_transport_u8 *const record =
        open_cfw_bootloader_easylogger_transport_channel(channel);
    void *const handle = *(void *volatile *)(void *)(
        record + OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_HANDLE_OFFSET);
    (void)buffer;
    (void)length;
    return ((open_cfw_bootloader_elog_transport_start_fn)
        (open_cfw_bootloader_elog_transport_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_LOWER_START_THUMB)(
                handle, descriptor);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_transport_wait(
    open_cfw_bootloader_elog_transport_u32 duration)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    open_cfw_bootloader_easylogger_transport_host_wait(duration);
#else
    ((open_cfw_bootloader_elog_transport_wait_fn)
        (open_cfw_bootloader_elog_transport_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_WAIT_THUMB)(duration);
#endif
}

__attribute__((used, noinline))
open_cfw_bootloader_elog_transport_u32
open_cfw_bootloader_easylogger_channel_write_41f918(
    open_cfw_bootloader_elog_transport_u8 channel,
    const void *buffer,
    open_cfw_bootloader_elog_transport_u32 length)
{
    open_cfw_bootloader_elog_transport_u8 descriptor[
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_SIZE];
    open_cfw_bootloader_elog_transport_u32 start_status;
    open_cfw_bootloader_elog_transport_u32 poll_count;

    open_cfw_bootloader_easylogger_transport_zero(
        descriptor, OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_SIZE);

    if (channel >= OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_CHANNEL_COUNT) {
        return OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ERROR;
    }
    if (open_cfw_bootloader_easylogger_transport_initialized(channel) != 1U) {
        return OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ERROR;
    }

    *(const void **)(void *)&descriptor[0] = buffer;
    *(open_cfw_bootloader_elog_transport_u32 *)(void *)&descriptor[
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_LENGTH_OFFSET] = length;
    descriptor[OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_OPERATION_OFFSET]
        = 0U;
    *(open_cfw_bootloader_elog_transport_u32 *)(void *)&descriptor[
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_FIELD_C_OFFSET] = 0U;
    *(open_cfw_bootloader_elog_transport_u32 *)(void *)&descriptor[
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_DESCRIPTOR_FIELD_10_OFFSET] = 0U;

    open_cfw_bootloader_easylogger_transport_set_completion(channel, 0U);
    start_status = open_cfw_bootloader_easylogger_transport_start(
        channel, buffer, length, descriptor);

    poll_count = 0U;
    while (poll_count < OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_POLL_LIMIT &&
           open_cfw_bootloader_easylogger_transport_completion(channel) != 1U) {
        open_cfw_bootloader_easylogger_transport_wait(
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_POLL_WAIT);
        ++poll_count;
    }

    return start_status == 0U ? OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_SUCCESS
                              : OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_ERROR;
}

__attribute__((used, noinline))
open_cfw_bootloader_elog_transport_u32
open_cfw_bootloader_easylogger_driver_output_41b854(
    const void *buffer,
    open_cfw_bootloader_elog_transport_u32 length,
    open_cfw_bootloader_elog_transport_u32 level)
{
    (void)level;
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST)
    return open_cfw_bootloader_easylogger_channel_write_41f918(
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_LOG_CHANNEL, buffer, length);
#else
    return ((open_cfw_bootloader_elog_transport_write_fn)
        (open_cfw_bootloader_elog_transport_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_WRITE_THUMB)(
                OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_LOG_CHANNEL,
                buffer,
                length);
#endif
}
