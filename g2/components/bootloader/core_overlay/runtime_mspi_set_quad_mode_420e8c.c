/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G quad-mode selector. */

typedef __UINT8_TYPE__ open_cfw_quad_u8;
typedef __UINT32_TYPE__ open_cfw_quad_u32;
typedef __UINTPTR_TYPE__ open_cfw_quad_word;

enum {
    OPEN_CFW_QUAD_TEMPLATE_ADDRESS = 0x20000224U,
    OPEN_CFW_QUAD_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_QUAD_CONFIG_SIZE = 24U,
    OPEN_CFW_QUAD_TURNAROUND_OFFSET = 0U,
    OPEN_CFW_QUAD_READ_INSTRUCTION_OFFSET = 4U,
    OPEN_CFW_QUAD_DEVICE_OFFSET = 8U,
    OPEN_CFW_QUAD_TURNAROUND_ENABLE_OFFSET = 15U,
    OPEN_CFW_QUAD_TURNAROUND = 8U,
    OPEN_CFW_QUAD_READ_INSTRUCTION = 0x006CU,
    OPEN_CFW_QUAD_DEVICE = 0x10U,
    OPEN_CFW_QUAD_CONTROL_REQUEST = 0x18U,
    OPEN_CFW_QUAD_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_QUAD_CONTROL_THUMB = 0x004251C1U,
    OPEN_CFW_QUAD_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_QUAD_LOG_FILE = 0x00431540U,
    OPEN_CFW_QUAD_LOG_FUNCTION = 0x00433578U,
    OPEN_CFW_QUAD_RECONFIGURE_FORMAT = 0x00432E50U,
    OPEN_CFW_QUAD_CONTROL_FORMAT = 0x00433240U,
    OPEN_CFW_QUAD_RECONFIGURE_LINE = 0x5AEU,
    OPEN_CFW_QUAD_CONTROL_LINE = 0x5B5U
};

typedef open_cfw_quad_u32 (*open_cfw_quad_control_fn)(
    void *, open_cfw_quad_u32, void *);
typedef void (*open_cfw_quad_log_fn)(open_cfw_quad_u32, const void *,
    const void *, const void *, open_cfw_quad_u32, const void *, ...);

#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
const open_cfw_quad_u8 *open_cfw_quad_host_template(void);
open_cfw_quad_word open_cfw_quad_host_handle(void);
void open_cfw_quad_host_copy(void *, const void *, open_cfw_quad_u32);
open_cfw_quad_u32 open_cfw_quad_host_reconfigure(const open_cfw_quad_u8 *);
void open_cfw_quad_host_xip(open_cfw_quad_u32);
open_cfw_quad_u32 open_cfw_quad_host_control(void *, open_cfw_quad_u32,
    void *);
void open_cfw_quad_host_log(open_cfw_quad_u32, open_cfw_quad_u32);
#else
void open_cfw_bootloader_aeabi_memcpy(void *, const void *, open_cfw_quad_u32);
open_cfw_quad_u32 open_cfw_bootloader_mspi_device_reconfigure_420e08(
    const open_cfw_quad_u8 *);
void open_cfw_bootloader_mspi_xip_config_41ff34(open_cfw_quad_u32);
#endif

static __attribute__((always_inline)) inline const open_cfw_quad_u8 *
open_cfw_quad_template(void)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    return open_cfw_quad_host_template();
#else
    return (const open_cfw_quad_u8 *)(open_cfw_quad_word)
        OPEN_CFW_QUAD_TEMPLATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_word
open_cfw_quad_handle(void)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    return open_cfw_quad_host_handle();
#else
    return *(const volatile open_cfw_quad_u32 *)(open_cfw_quad_word)
        OPEN_CFW_QUAD_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void open_cfw_quad_copy(
    void *destination, const void *source)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    open_cfw_quad_host_copy(destination, source, OPEN_CFW_QUAD_CONFIG_SIZE);
#else
    open_cfw_bootloader_aeabi_memcpy(destination, source,
        OPEN_CFW_QUAD_CONFIG_SIZE);
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_reconfigure(const open_cfw_quad_u8 *config)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    return open_cfw_quad_host_reconfigure(config);
#else
    return open_cfw_bootloader_mspi_device_reconfigure_420e08(config);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_quad_xip(void)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    open_cfw_quad_host_xip(1U);
#else
    open_cfw_bootloader_mspi_xip_config_41ff34(1U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_control(open_cfw_quad_u8 *mode)
{
    void *handle = (void *)open_cfw_quad_handle();
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    return open_cfw_quad_host_control(handle, OPEN_CFW_QUAD_CONTROL_REQUEST,
        mode);
#else
    return ((open_cfw_quad_control_fn)(open_cfw_quad_word)
        OPEN_CFW_QUAD_CONTROL_THUMB)(handle, OPEN_CFW_QUAD_CONTROL_REQUEST,
            mode);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_quad_log(
    open_cfw_quad_u32 line, open_cfw_quad_u32 format)
{
#if defined(OPEN_CFW_MSPI_SET_QUAD_MODE_HOST)
    open_cfw_quad_host_log(line, format);
#else
    ((open_cfw_quad_log_fn)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_THUMB)(2U,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_TAG,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_FILE,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_FUNCTION,
        line, (const void *)(open_cfw_quad_word)format);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_set_quad_mode_420e8c(void)
{
    open_cfw_quad_u8 config[OPEN_CFW_QUAD_CONFIG_SIZE];
    open_cfw_quad_u8 mode;

    open_cfw_quad_copy(config, open_cfw_quad_template());
    config[OPEN_CFW_QUAD_DEVICE_OFFSET] = OPEN_CFW_QUAD_DEVICE;
    config[OPEN_CFW_QUAD_READ_INSTRUCTION_OFFSET] =
        (open_cfw_quad_u8)OPEN_CFW_QUAD_READ_INSTRUCTION;
    config[OPEN_CFW_QUAD_READ_INSTRUCTION_OFFSET + 1U] =
        (open_cfw_quad_u8)(OPEN_CFW_QUAD_READ_INSTRUCTION >> 8U);
    config[OPEN_CFW_QUAD_TURNAROUND_OFFSET] = OPEN_CFW_QUAD_TURNAROUND;
    config[OPEN_CFW_QUAD_TURNAROUND_ENABLE_OFFSET] = 1U;

    if (open_cfw_quad_reconfigure(config) != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_RECONFIGURE_LINE,
            OPEN_CFW_QUAD_RECONFIGURE_FORMAT);
        return;
    }

    open_cfw_quad_xip();
    mode = OPEN_CFW_QUAD_DEVICE;
    if (open_cfw_quad_control(&mode) != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_CONTROL_LINE,
            OPEN_CFW_QUAD_CONTROL_FORMAT);
    }
}
