/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G ready polling wrappers. */

typedef __UINT32_TYPE__ open_cfw_wait_ready_u32;
typedef __UINTPTR_TYPE__ open_cfw_wait_ready_word;

enum {
    OPEN_CFW_WAIT_READY_FAST_POLLS = 200U,
    OPEN_CFW_WAIT_READY_FAST_DELAY = 5U,
    OPEN_CFW_WAIT_READY_SLOW_DELAY = 1000U,
    OPEN_CFW_WAIT_READY_DEFAULT_POLLS = 500U,
    OPEN_CFW_WAIT_READY_CONTEXT_THREAD = 2U,
    OPEN_CFW_WAIT_READY_NOTIFY_VALUE = 1U
};

typedef open_cfw_wait_ready_u32 (*open_cfw_wait_ready_status_fn)(void);
typedef open_cfw_wait_ready_u32 (*open_cfw_wait_ready_value_fn)(
    open_cfw_wait_ready_u32);
typedef open_cfw_wait_ready_u32 (*open_cfw_wait_ready_context_fn)(void);

#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
open_cfw_wait_ready_u32 open_cfw_wait_ready_host_status(void);
open_cfw_wait_ready_u32 open_cfw_wait_ready_host_context(void);
void open_cfw_wait_ready_host_delay(open_cfw_wait_ready_u32);
void open_cfw_wait_ready_host_notify(open_cfw_wait_ready_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_wait_ready_u32
open_cfw_wait_ready_status(void)
{
#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
    return open_cfw_wait_ready_host_status();
#else
    return ((open_cfw_wait_ready_status_fn)(open_cfw_wait_ready_word)
        0x0042074FU)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_wait_ready_u32
open_cfw_wait_ready_context(void)
{
#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
    return open_cfw_wait_ready_host_context();
#else
    return ((open_cfw_wait_ready_context_fn)(open_cfw_wait_ready_word)
        0x00416089U)();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_wait_ready_delay(
    open_cfw_wait_ready_u32 duration)
{
#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
    open_cfw_wait_ready_host_delay(duration);
#else
    (void)((open_cfw_wait_ready_value_fn)(open_cfw_wait_ready_word)
        0x0041F9E7U)(duration);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_wait_ready_notify(
    open_cfw_wait_ready_u32 value)
{
#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
    open_cfw_wait_ready_host_notify(value);
#else
    (void)((open_cfw_wait_ready_value_fn)(open_cfw_wait_ready_word)
        0x00416379U)(value);
#endif
}

__attribute__((used, noinline))
open_cfw_wait_ready_u32 open_cfw_bootloader_mspi_wait_ready_4207a2(
    open_cfw_wait_ready_u32 slow_poll_limit)
{
    open_cfw_wait_ready_u32 count;

    for (count = 0U; count < OPEN_CFW_WAIT_READY_FAST_POLLS; ++count) {
        if (open_cfw_wait_ready_status() == 0U) {
            return 0U;
        }
        open_cfw_wait_ready_delay(OPEN_CFW_WAIT_READY_FAST_DELAY);
    }

    for (count = 0U; count < slow_poll_limit; ++count) {
        if (open_cfw_wait_ready_context() ==
            OPEN_CFW_WAIT_READY_CONTEXT_THREAD) {
            open_cfw_wait_ready_notify(OPEN_CFW_WAIT_READY_NOTIFY_VALUE);
        } else {
            open_cfw_wait_ready_delay(OPEN_CFW_WAIT_READY_SLOW_DELAY);
        }
        if (open_cfw_wait_ready_status() == 0U) {
            return 0U;
        }
    }
    return 1U;
}

__attribute__((used, noinline))
open_cfw_wait_ready_u32 open_cfw_bootloader_mspi_wait_ready_default_4207f4(void)
{
#if defined(OPEN_CFW_MSPI_WAIT_READY_HOST)
    return open_cfw_bootloader_mspi_wait_ready_4207a2(
        OPEN_CFW_WAIT_READY_DEFAULT_POLLS);
#else
    return ((open_cfw_wait_ready_value_fn)(open_cfw_wait_ready_word)
        0x004207A3U)(OPEN_CFW_WAIT_READY_DEFAULT_POLLS);
#endif
}
