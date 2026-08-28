/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the authenticated G2 bootloader guarded
 * teardown entry. Fixed ROM/SRAM seams are isolated for host execution.
 */

typedef __UINT8_TYPE__ open_cfw_teardown_u8;
typedef __UINT32_TYPE__ open_cfw_teardown_u32;
typedef __UINTPTR_TYPE__ open_cfw_teardown_uintptr;

enum {
    OPEN_CFW_TEARDOWN_ACTIVE = 1U,
    OPEN_CFW_TEARDOWN_PIN = 0x1CU,
    OPEN_CFW_TEARDOWN_GUARD = 0x20027198U,
    OPEN_CFW_TEARDOWN_PIN_CONFIG = 0x00434154U,
    OPEN_CFW_TEARDOWN_STAGE_ONE_THUMB = 0x00423D21U,
    OPEN_CFW_TEARDOWN_STAGE_TWO_THUMB = 0x00423DD1U,
    OPEN_CFW_TEARDOWN_STORE_STATE_THUMB = 0x0041583DU,
    OPEN_CFW_TEARDOWN_PIN_CONFIGURE_THUMB = 0x0041D92DU
};

typedef open_cfw_teardown_u32 (*open_cfw_teardown_status_fn)(void);
typedef void (*open_cfw_teardown_store_fn)(open_cfw_teardown_u32);
typedef open_cfw_teardown_u32 (*open_cfw_teardown_pin_fn)(
    open_cfw_teardown_u32,
    open_cfw_teardown_u32);

#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
open_cfw_teardown_u8 *open_cfw_guarded_teardown_host_guard(void);
const open_cfw_teardown_u32 *open_cfw_guarded_teardown_host_pin_config(void);
open_cfw_teardown_u32 open_cfw_guarded_teardown_host_stage_one(void);
open_cfw_teardown_u32 open_cfw_guarded_teardown_host_stage_two(void);
void open_cfw_guarded_teardown_host_store_state(open_cfw_teardown_u32 value);
open_cfw_teardown_u32 open_cfw_guarded_teardown_host_configure_pin(
    open_cfw_teardown_u32 pin,
    open_cfw_teardown_u32 configuration);
void open_cfw_guarded_teardown_host_fail_stop(open_cfw_teardown_u32 stage);
#endif

static __attribute__((always_inline)) inline open_cfw_teardown_u8 *
open_cfw_teardown_guard(void)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    return open_cfw_guarded_teardown_host_guard();
#else
    return (open_cfw_teardown_u8 *)(open_cfw_teardown_uintptr)
        OPEN_CFW_TEARDOWN_GUARD;
#endif
}

static __attribute__((always_inline)) inline open_cfw_teardown_u32
open_cfw_teardown_pin_configuration(void)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    return *open_cfw_guarded_teardown_host_pin_config();
#else
    return *(const volatile open_cfw_teardown_u32 *)
        (open_cfw_teardown_uintptr)OPEN_CFW_TEARDOWN_PIN_CONFIG;
#endif
}

static __attribute__((always_inline)) inline open_cfw_teardown_u32
open_cfw_teardown_stage_one(void)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    return open_cfw_guarded_teardown_host_stage_one();
#else
    return ((open_cfw_teardown_status_fn)(open_cfw_teardown_uintptr)
        OPEN_CFW_TEARDOWN_STAGE_ONE_THUMB)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_teardown_u32
open_cfw_teardown_stage_two(void)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    return open_cfw_guarded_teardown_host_stage_two();
#else
    return ((open_cfw_teardown_status_fn)(open_cfw_teardown_uintptr)
        OPEN_CFW_TEARDOWN_STAGE_TWO_THUMB)();
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_teardown_store_state(open_cfw_teardown_u32 value)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    open_cfw_guarded_teardown_host_store_state(value);
#else
    ((open_cfw_teardown_store_fn)(open_cfw_teardown_uintptr)
        OPEN_CFW_TEARDOWN_STORE_STATE_THUMB)(value);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_teardown_configure_pin(
    open_cfw_teardown_u32 pin,
    open_cfw_teardown_u32 configuration)
{
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
    (void)open_cfw_guarded_teardown_host_configure_pin(pin, configuration);
#else
    (void)((open_cfw_teardown_pin_fn)(open_cfw_teardown_uintptr)
        OPEN_CFW_TEARDOWN_PIN_CONFIGURE_THUMB)(pin, configuration);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_guarded_teardown_41fa98(void)
{
    open_cfw_teardown_u8 *const guard = open_cfw_teardown_guard();

    if (*guard != OPEN_CFW_TEARDOWN_ACTIVE) {
        return;
    }

    if (open_cfw_teardown_stage_one() != 0U) {
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
        open_cfw_guarded_teardown_host_fail_stop(1U);
        return;
#else
        for (;;) {
        }
#endif
    }

    if (open_cfw_teardown_stage_two() != 0U) {
#if defined(OPEN_CFW_GUARDED_TEARDOWN_HOST)
        open_cfw_guarded_teardown_host_fail_stop(2U);
        return;
#else
        for (;;) {
        }
#endif
    }

    open_cfw_teardown_store_state(0U);
    open_cfw_teardown_configure_pin(
        OPEN_CFW_TEARDOWN_PIN,
        open_cfw_teardown_pin_configuration());
    *guard = 0U;
}
