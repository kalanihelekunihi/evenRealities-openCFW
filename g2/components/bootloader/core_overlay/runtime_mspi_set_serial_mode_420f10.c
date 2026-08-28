/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G serial-mode selector. */

typedef __UINT8_TYPE__ open_cfw_serial_u8;
typedef __UINT32_TYPE__ open_cfw_serial_u32;
typedef __UINTPTR_TYPE__ open_cfw_serial_word;

enum {
    OPEN_CFW_SERIAL_TEMPLATE_ADDRESS = 0x2000020CU,
    OPEN_CFW_SERIAL_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_SERIAL_CONTROL_REQUEST = 0x18U,
    OPEN_CFW_SERIAL_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_SERIAL_CONTROL_THUMB = 0x004251C1U,
    OPEN_CFW_SERIAL_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_SERIAL_LOG_FILE = 0x00431540U,
    OPEN_CFW_SERIAL_LOG_FUNCTION = 0x00433594U,
    OPEN_CFW_SERIAL_RECONFIGURE_FORMAT = 0x00432E74U,
    OPEN_CFW_SERIAL_CONTROL_FORMAT = 0x00433260U,
    OPEN_CFW_SERIAL_RECONFIGURE_LINE = 0x5C0U,
    OPEN_CFW_SERIAL_CONTROL_LINE = 0x5C7U
};

typedef open_cfw_serial_u32 (*open_cfw_serial_control_fn)(
    void *, open_cfw_serial_u32, void *);
typedef void (*open_cfw_serial_log_fn)(open_cfw_serial_u32, const void *,
    const void *, const void *, open_cfw_serial_u32, const void *, ...);

#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
const open_cfw_serial_u8 *open_cfw_serial_host_template(void);
open_cfw_serial_word open_cfw_serial_host_handle(void);
open_cfw_serial_u32 open_cfw_serial_host_reconfigure(
    const open_cfw_serial_u8 *);
void open_cfw_serial_host_xip(open_cfw_serial_u32);
open_cfw_serial_u32 open_cfw_serial_host_control(void *, open_cfw_serial_u32,
    void *);
void open_cfw_serial_host_log(open_cfw_serial_u32, open_cfw_serial_u32);
#else
open_cfw_serial_u32 open_cfw_bootloader_mspi_device_reconfigure_420e08(
    const open_cfw_serial_u8 *);
void open_cfw_bootloader_mspi_xip_config_41ff34(open_cfw_serial_u32);
#endif

static __attribute__((always_inline)) inline const open_cfw_serial_u8 *
open_cfw_serial_template(void)
{
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    return open_cfw_serial_host_template();
#else
    return (const open_cfw_serial_u8 *)(open_cfw_serial_word)
        OPEN_CFW_SERIAL_TEMPLATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_serial_word
open_cfw_serial_handle(void)
{
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    return open_cfw_serial_host_handle();
#else
    return *(const volatile open_cfw_serial_u32 *)(open_cfw_serial_word)
        OPEN_CFW_SERIAL_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_serial_u32
open_cfw_serial_reconfigure(const open_cfw_serial_u8 *config)
{
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    return open_cfw_serial_host_reconfigure(config);
#else
    return open_cfw_bootloader_mspi_device_reconfigure_420e08(config);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_serial_xip(void)
{
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    open_cfw_serial_host_xip(0U);
#else
    open_cfw_bootloader_mspi_xip_config_41ff34(0U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_serial_u32
open_cfw_serial_control(open_cfw_serial_u8 *mode)
{
    void *handle = (void *)open_cfw_serial_handle();
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    return open_cfw_serial_host_control(handle, OPEN_CFW_SERIAL_CONTROL_REQUEST,
        mode);
#else
    return ((open_cfw_serial_control_fn)(open_cfw_serial_word)
        OPEN_CFW_SERIAL_CONTROL_THUMB)(handle, OPEN_CFW_SERIAL_CONTROL_REQUEST,
            mode);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_serial_log(
    open_cfw_serial_u32 line, open_cfw_serial_u32 format)
{
#if defined(OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST)
    open_cfw_serial_host_log(line, format);
#else
    ((open_cfw_serial_log_fn)(open_cfw_serial_word)OPEN_CFW_SERIAL_LOG_THUMB)(
        2U, (const void *)(open_cfw_serial_word)OPEN_CFW_SERIAL_LOG_TAG,
        (const void *)(open_cfw_serial_word)OPEN_CFW_SERIAL_LOG_FILE,
        (const void *)(open_cfw_serial_word)OPEN_CFW_SERIAL_LOG_FUNCTION,
        line, (const void *)(open_cfw_serial_word)format);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_set_serial_mode_420f10(void)
{
    open_cfw_serial_u8 mode;

    if (open_cfw_serial_reconfigure(open_cfw_serial_template()) != 0U) {
        open_cfw_serial_log(OPEN_CFW_SERIAL_RECONFIGURE_LINE,
            OPEN_CFW_SERIAL_RECONFIGURE_FORMAT);
        return;
    }
    open_cfw_serial_xip();
    mode = 0U;
    if (open_cfw_serial_control(&mode) != 0U) {
        open_cfw_serial_log(OPEN_CFW_SERIAL_CONTROL_LINE,
            OPEN_CFW_SERIAL_CONTROL_FORMAT);
    }
}
