/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room reconstruction of the authenticated G2 bootloader platform
 * setup entry. Fixed ROM/configuration seams are isolated for host tests.
 */

typedef __UINT8_TYPE__ open_cfw_platform_u8;
typedef __UINT32_TYPE__ open_cfw_platform_u32;
typedef __UINTPTR_TYPE__ open_cfw_platform_uintptr;

enum {
    OPEN_CFW_PLATFORM_CONFIG_SIZE = 20U,
    OPEN_CFW_PLATFORM_CONFIG = 0x00433A9CU,
    OPEN_CFW_PLATFORM_GUARDED_TEARDOWN_THUMB = 0x0041FA99U,
    OPEN_CFW_PLATFORM_RESET_THUMB = 0x0041C4B5U,
    OPEN_CFW_PLATFORM_MODE_THUMB = 0x0041C86DU,
    OPEN_CFW_PLATFORM_DERIVE_THUMB = 0x0041CA2DU,
    OPEN_CFW_PLATFORM_COPY_THUMB = 0x004156ADU,
    OPEN_CFW_PLATFORM_SUBMIT_THUMB = 0x00422417U,
    OPEN_CFW_PLATFORM_CHANNEL_THUMB = 0x004222A1U
};

typedef void (*open_cfw_platform_void_fn)(void);
typedef void (*open_cfw_platform_pair_fn)(
    open_cfw_platform_u32,
    open_cfw_platform_u32);
typedef void *(*open_cfw_platform_copy_fn)(
    void *,
    const void *,
    open_cfw_platform_u32);
typedef void (*open_cfw_platform_pointer_fn)(void *);
typedef void (*open_cfw_platform_channel_fn)(
    open_cfw_platform_u32,
    open_cfw_platform_u32,
    open_cfw_platform_u32);

#if defined(__arm__) || defined(__thumb__)
typedef void (__attribute__((pcs("aapcs-vfp"))) *open_cfw_platform_derive_fn)(
    open_cfw_platform_u32 *,
    float);
#else
typedef void (*open_cfw_platform_derive_fn)(open_cfw_platform_u32 *, float);
#endif

#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
const open_cfw_platform_u8 *open_cfw_platform_setup_host_config(void);
void open_cfw_platform_setup_host_guarded_teardown(void);
void open_cfw_platform_setup_host_reset(void);
void open_cfw_platform_setup_host_mode(
    open_cfw_platform_u32 first,
    open_cfw_platform_u32 second);
void open_cfw_platform_setup_host_derive(
    open_cfw_platform_u32 *output,
    float input);
void *open_cfw_platform_setup_host_copy(
    void *destination,
    const void *source,
    open_cfw_platform_u32 size);
void open_cfw_platform_setup_host_submit(void *configuration);
void open_cfw_platform_setup_host_channel(
    open_cfw_platform_u32 channel,
    open_cfw_platform_u32 first,
    open_cfw_platform_u32 second);
#endif

static __attribute__((always_inline)) inline const open_cfw_platform_u8 *
open_cfw_platform_configuration(void)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    return open_cfw_platform_setup_host_config();
#else
    return (const open_cfw_platform_u8 *)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_CONFIG;
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_platform_guarded_teardown(void)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_guarded_teardown();
#else
    ((open_cfw_platform_void_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_GUARDED_TEARDOWN_THUMB)();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_reset(void)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_reset();
#else
    ((open_cfw_platform_void_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_RESET_THUMB)();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_mode(void)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_mode(0U, 0U);
#else
    ((open_cfw_platform_pair_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_MODE_THUMB)(0U, 0U);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_derive(
    open_cfw_platform_u32 *output)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_derive(output, 25.0F);
#else
    ((open_cfw_platform_derive_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_DERIVE_THUMB)(output, 25.0F);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_copy(
    void *destination,
    const void *source)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    (void)open_cfw_platform_setup_host_copy(
        destination, source, OPEN_CFW_PLATFORM_CONFIG_SIZE);
#else
    (void)((open_cfw_platform_copy_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_COPY_THUMB)(
            destination, source, OPEN_CFW_PLATFORM_CONFIG_SIZE);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_submit(
    void *configuration)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_submit(configuration);
#else
    ((open_cfw_platform_pointer_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_SUBMIT_THUMB)(configuration);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_platform_channel(
    open_cfw_platform_u32 channel)
{
#if defined(OPEN_CFW_PLATFORM_SETUP_HOST)
    open_cfw_platform_setup_host_channel(channel, 0U, 0U);
#else
    ((open_cfw_platform_channel_fn)(open_cfw_platform_uintptr)
        OPEN_CFW_PLATFORM_CHANNEL_THUMB)(channel, 0U, 0U);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_platform_setup_41fa50(void)
{
    open_cfw_platform_u32 derived;
    open_cfw_platform_u8 configuration[OPEN_CFW_PLATFORM_CONFIG_SIZE];

    open_cfw_platform_guarded_teardown();
    open_cfw_platform_reset();
    open_cfw_platform_mode();
    open_cfw_platform_derive(&derived);
    open_cfw_platform_copy(configuration, open_cfw_platform_configuration());
    open_cfw_platform_submit(configuration);
    open_cfw_platform_channel(4U);
    open_cfw_platform_channel(5U);
}
