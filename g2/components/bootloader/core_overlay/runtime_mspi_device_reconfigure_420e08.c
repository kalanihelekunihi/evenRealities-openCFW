/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MSPI device reconfiguration service. */

typedef __UINT8_TYPE__ open_cfw_reconfigure_u8;
typedef __UINT32_TYPE__ open_cfw_reconfigure_u32;
typedef __UINTPTR_TYPE__ open_cfw_reconfigure_word;

enum {
    OPEN_CFW_RECONFIGURE_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_RECONFIGURE_STATE_ADDRESS = 0x200270D8U,
    OPEN_CFW_RECONFIGURE_DEVICE_OFFSET = 8U,
    OPEN_CFW_RECONFIGURE_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_RECONFIGURE_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_RECONFIGURE_LOG_FILE = 0x00431540U,
    OPEN_CFW_RECONFIGURE_LOG_FUNCTION = 0x00432DE4U,
    OPEN_CFW_RECONFIGURE_DISABLE_FORMAT = 0x00432E08U,
    OPEN_CFW_RECONFIGURE_CONFIGURE_FORMAT = 0x00432E2CU,
    OPEN_CFW_RECONFIGURE_DISABLE_LINE = 0x58AU,
    OPEN_CFW_RECONFIGURE_CONFIGURE_LINE = 0x592U,
    OPEN_CFW_RECONFIGURE_ENABLE_LINE = 0x59AU
};

typedef open_cfw_reconfigure_u32 (*open_cfw_reconfigure_handle_fn)(void *);
typedef open_cfw_reconfigure_u32 (*open_cfw_reconfigure_configure_fn)(
    void *, const void *);
typedef void (*open_cfw_reconfigure_log_fn)(open_cfw_reconfigure_u32,
    const void *, const void *, const void *, open_cfw_reconfigure_u32,
    const void *, ...);

void open_cfw_bootloader_pin_groups_41fadc(open_cfw_reconfigure_u32,
    open_cfw_reconfigure_u32);

#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
open_cfw_reconfigure_word open_cfw_reconfigure_host_handle(void);
open_cfw_reconfigure_word open_cfw_reconfigure_host_state(void);
open_cfw_reconfigure_u32 open_cfw_reconfigure_host_call(
    open_cfw_reconfigure_u32, open_cfw_reconfigure_word,
    open_cfw_reconfigure_word);
void open_cfw_reconfigure_host_pin_groups(open_cfw_reconfigure_u32,
    open_cfw_reconfigure_u32);
void open_cfw_reconfigure_host_log(open_cfw_reconfigure_u32,
    open_cfw_reconfigure_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_reconfigure_word
open_cfw_reconfigure_handle(void)
{
#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
    return open_cfw_reconfigure_host_handle();
#else
    return *(const volatile open_cfw_reconfigure_u32 *)
        (open_cfw_reconfigure_word)OPEN_CFW_RECONFIGURE_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_reconfigure_word
open_cfw_reconfigure_state(void)
{
#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
    return open_cfw_reconfigure_host_state();
#else
    return *(const volatile open_cfw_reconfigure_u32 *)
        (open_cfw_reconfigure_word)OPEN_CFW_RECONFIGURE_STATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_reconfigure_u32
open_cfw_reconfigure_call(open_cfw_reconfigure_u32 operation,
    open_cfw_reconfigure_word handle, open_cfw_reconfigure_word config)
{
#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
    return open_cfw_reconfigure_host_call(operation, handle, config);
#else
    if (operation == 0U) {
        return ((open_cfw_reconfigure_handle_fn)(open_cfw_reconfigure_word)
            0x004250F1U)((void *)handle);
    }
    if (operation == 1U) {
        return ((open_cfw_reconfigure_configure_fn)(open_cfw_reconfigure_word)
            0x00424BE5U)((void *)handle, (const void *)config);
    }
    return ((open_cfw_reconfigure_handle_fn)(open_cfw_reconfigure_word)
        0x00425067U)((void *)handle);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_reconfigure_log(
    open_cfw_reconfigure_u32 line, open_cfw_reconfigure_u32 format)
{
#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
    open_cfw_reconfigure_host_log(line, format);
#else
    ((open_cfw_reconfigure_log_fn)(open_cfw_reconfigure_word)
        OPEN_CFW_RECONFIGURE_LOG_THUMB)(2U,
            (const void *)(open_cfw_reconfigure_word)
                OPEN_CFW_RECONFIGURE_LOG_TAG,
            (const void *)(open_cfw_reconfigure_word)
                OPEN_CFW_RECONFIGURE_LOG_FILE,
            (const void *)(open_cfw_reconfigure_word)
                OPEN_CFW_RECONFIGURE_LOG_FUNCTION,
            line, (const void *)(open_cfw_reconfigure_word)format);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_reconfigure_pin_groups(open_cfw_reconfigure_u32 instance,
    open_cfw_reconfigure_u32 device)
{
#if defined(OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST)
    open_cfw_reconfigure_host_pin_groups(instance, device);
#else
    open_cfw_bootloader_pin_groups_41fadc(instance, device);
#endif
}

__attribute__((used, noinline))
open_cfw_reconfigure_u32
open_cfw_bootloader_mspi_device_reconfigure_420e08(
    const open_cfw_reconfigure_u8 *config)
{
    const open_cfw_reconfigure_word handle = open_cfw_reconfigure_handle();
    open_cfw_reconfigure_u32 status;

    status = open_cfw_reconfigure_call(0U, handle, 0U);
    if (status != 0U) {
        open_cfw_reconfigure_log(OPEN_CFW_RECONFIGURE_DISABLE_LINE,
            OPEN_CFW_RECONFIGURE_DISABLE_FORMAT);
        return 1U;
    }

    status = open_cfw_reconfigure_call(1U, handle,
        (open_cfw_reconfigure_word)config);
    if (status != 0U) {
        open_cfw_reconfigure_log(OPEN_CFW_RECONFIGURE_CONFIGURE_LINE,
            OPEN_CFW_RECONFIGURE_CONFIGURE_FORMAT);
        return 1U;
    }

    status = open_cfw_reconfigure_call(2U, handle, 0U);
    if (status != 0U) {
        open_cfw_reconfigure_log(OPEN_CFW_RECONFIGURE_ENABLE_LINE,
            OPEN_CFW_RECONFIGURE_CONFIGURE_FORMAT);
        return 1U;
    }

    open_cfw_reconfigure_pin_groups(
        *(const open_cfw_reconfigure_u32 *)open_cfw_reconfigure_state(),
        config[OPEN_CFW_RECONFIGURE_DEVICE_OFFSET]);
    return 0U;
}
