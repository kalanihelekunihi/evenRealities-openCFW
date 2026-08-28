/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader MSPI XIP
 * configuration-byte updater.
 */

typedef __UINT8_TYPE__ open_cfw_mspi_xip_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_xip_u32;
typedef __UINTPTR_TYPE__ open_cfw_mspi_xip_word;

enum {
    OPEN_CFW_MSPI_XIP_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_MSPI_XIP_CONFIG_ADDRESS = 0x2000023CU,
    OPEN_CFW_MSPI_XIP_MODE_OFFSET = 5U,
    OPEN_CFW_MSPI_XIP_ENABLED_MODE = 8U,
    OPEN_CFW_MSPI_XIP_CONTROL_REQUEST = 16U,
    OPEN_CFW_MSPI_XIP_CONTROL_THUMB = 0x004251C1U
};

typedef open_cfw_mspi_xip_u32 (*open_cfw_mspi_xip_control_fn)(
    void *, open_cfw_mspi_xip_u32, void *);

#if defined(OPEN_CFW_MSPI_XIP_CONFIG_HOST)
open_cfw_mspi_xip_u8 *open_cfw_mspi_xip_host_config(void);
void *open_cfw_mspi_xip_host_handle(void);
open_cfw_mspi_xip_u32 open_cfw_mspi_xip_host_control(
    void *, open_cfw_mspi_xip_u32, void *);
#endif

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_xip_config_41ff34(open_cfw_mspi_xip_u32 enabled)
{
    open_cfw_mspi_xip_u8 *config;
    void *handle;

#if defined(OPEN_CFW_MSPI_XIP_CONFIG_HOST)
    config = open_cfw_mspi_xip_host_config();
    handle = open_cfw_mspi_xip_host_handle();
#else
    config = (open_cfw_mspi_xip_u8 *)(open_cfw_mspi_xip_word)
        OPEN_CFW_MSPI_XIP_CONFIG_ADDRESS;
    handle = *(void **)(open_cfw_mspi_xip_word)
        OPEN_CFW_MSPI_XIP_HANDLE_ADDRESS;
#endif

    config[OPEN_CFW_MSPI_XIP_MODE_OFFSET] =
        (open_cfw_mspi_xip_u8)enabled == 1U
            ? OPEN_CFW_MSPI_XIP_ENABLED_MODE
            : 0U;

#if defined(OPEN_CFW_MSPI_XIP_CONFIG_HOST)
    (void)open_cfw_mspi_xip_host_control(
        handle, OPEN_CFW_MSPI_XIP_CONTROL_REQUEST, config);
#else
    (void)((open_cfw_mspi_xip_control_fn)(open_cfw_mspi_xip_word)
        OPEN_CFW_MSPI_XIP_CONTROL_THUMB)(
            handle, OPEN_CFW_MSPI_XIP_CONTROL_REQUEST, config);
#endif
}
