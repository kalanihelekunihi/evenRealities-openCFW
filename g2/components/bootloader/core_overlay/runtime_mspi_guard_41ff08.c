/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the paired G2 bootloader MSPI guard entries.
 */

typedef __UINT8_TYPE__ open_cfw_mspi_guard_u8;
typedef __UINTPTR_TYPE__ open_cfw_mspi_guard_word;

enum {
    OPEN_CFW_MSPI_GUARD_BYPASS_ADDRESS = 0x200271C5U,
    OPEN_CFW_MSPI_GUARD_ACQUIRE_THUMB = 0x0041FE9DU,
    OPEN_CFW_MSPI_GUARD_RELEASE_THUMB = 0x0041FED5U,
    OPEN_CFW_MSPI_GUARD_ENABLE_THUMB = 0x0041FE29U,
    OPEN_CFW_MSPI_GUARD_DISABLE_THUMB = 0x0041FE49U
};

typedef void (*open_cfw_mspi_guard_fn)(void);

#if defined(OPEN_CFW_MSPI_GUARD_HOST)
open_cfw_mspi_guard_u8 *open_cfw_mspi_guard_host_bypass(void);
void open_cfw_mspi_guard_host_acquire(void);
void open_cfw_mspi_guard_host_release(void);
void open_cfw_mspi_guard_host_enable(void);
void open_cfw_mspi_guard_host_disable(void);
#endif

static __attribute__((always_inline)) inline open_cfw_mspi_guard_u8
open_cfw_mspi_guard_bypass(void)
{
#if defined(OPEN_CFW_MSPI_GUARD_HOST)
    return *open_cfw_mspi_guard_host_bypass();
#else
    return *(volatile open_cfw_mspi_guard_u8 *)(open_cfw_mspi_guard_word)
        OPEN_CFW_MSPI_GUARD_BYPASS_ADDRESS;
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_guard_enter_41ff08(void)
{
#if defined(OPEN_CFW_MSPI_GUARD_HOST)
    open_cfw_mspi_guard_host_acquire();
    if (open_cfw_mspi_guard_bypass() != 1U) {
        open_cfw_mspi_guard_host_disable();
    }
#else
    ((open_cfw_mspi_guard_fn)(open_cfw_mspi_guard_word)
        OPEN_CFW_MSPI_GUARD_ACQUIRE_THUMB)();
    if (open_cfw_mspi_guard_bypass() != 1U) {
        ((open_cfw_mspi_guard_fn)(open_cfw_mspi_guard_word)
            OPEN_CFW_MSPI_GUARD_DISABLE_THUMB)();
    }
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_guard_exit_41ff1e(void)
{
    if (open_cfw_mspi_guard_bypass() != 1U) {
#if defined(OPEN_CFW_MSPI_GUARD_HOST)
        open_cfw_mspi_guard_host_enable();
#else
        ((open_cfw_mspi_guard_fn)(open_cfw_mspi_guard_word)
            OPEN_CFW_MSPI_GUARD_ENABLE_THUMB)();
#endif
    }
#if defined(OPEN_CFW_MSPI_GUARD_HOST)
    open_cfw_mspi_guard_host_release();
#else
    ((open_cfw_mspi_guard_fn)(open_cfw_mspi_guard_word)
        OPEN_CFW_MSPI_GUARD_RELEASE_THUMB)();
#endif
}
