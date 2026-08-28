/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader event-flags
 * service initializer, acquire, and release entries.
 */

typedef __UINT32_TYPE__ open_cfw_event_u32;
typedef __UINTPTR_TYPE__ open_cfw_event_word;

enum {
    OPEN_CFW_EVENT_HANDLE_ADDRESS = 0x200270E0U,
    OPEN_CFW_EVENT_CONFIG_ADDRESS = 0x00433CF8U,
    OPEN_CFW_EVENT_CREATE_THUMB = 0x00416611U,
    OPEN_CFW_EVENT_ACQUIRE_THUMB = 0x004166ABU,
    OPEN_CFW_EVENT_RELEASE_THUMB = 0x00416711U,
    OPEN_CFW_EVENT_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_EVENT_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_EVENT_LOG_FILE = 0x00431540U,
    OPEN_CFW_EVENT_INIT_FUNCTION = 0x0043376CU,
    OPEN_CFW_EVENT_ACQUIRE_FUNCTION = 0x00433784U,
    OPEN_CFW_EVENT_RELEASE_FUNCTION = 0x0043379CU,
    OPEN_CFW_EVENT_INIT_FORMAT = 0x004329FCU,
    OPEN_CFW_EVENT_ACQUIRE_FORMAT = 0x00432CA0U,
    OPEN_CFW_EVENT_RELEASE_FORMAT = 0x00432A24U,
    OPEN_CFW_EVENT_INIT_LINE = 0xBAU,
    OPEN_CFW_EVENT_ACQUIRE_LINE = 0xC3U,
    OPEN_CFW_EVENT_RELEASE_LINE = 0xCCU,
    OPEN_CFW_EVENT_WAIT_FOREVER = 0xFFFFFFFFU
};

typedef open_cfw_event_word (*open_cfw_event_create_fn)(const void *);
typedef open_cfw_event_u32 (*open_cfw_event_acquire_fn)(
    open_cfw_event_word,
    open_cfw_event_u32);
typedef open_cfw_event_u32 (*open_cfw_event_release_fn)(open_cfw_event_word);
typedef void (*open_cfw_event_log_fn)(
    open_cfw_event_u32,
    const void *,
    const void *,
    const void *,
    open_cfw_event_u32,
    const void *);

#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
open_cfw_event_word *open_cfw_event_flags_host_handle(void);
const void *open_cfw_event_flags_host_config(void);
open_cfw_event_word open_cfw_event_flags_host_create(const void *);
open_cfw_event_u32 open_cfw_event_flags_host_acquire(
    open_cfw_event_word,
    open_cfw_event_u32);
open_cfw_event_u32 open_cfw_event_flags_host_release(open_cfw_event_word);
void open_cfw_event_flags_host_log(
    open_cfw_event_u32,
    open_cfw_event_word,
    open_cfw_event_word,
    open_cfw_event_word,
    open_cfw_event_u32,
    open_cfw_event_word);
#endif

static __attribute__((always_inline)) inline open_cfw_event_word *
open_cfw_event_handle_slot(void)
{
#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
    return open_cfw_event_flags_host_handle();
#else
    return (open_cfw_event_word *)(open_cfw_event_word)
        OPEN_CFW_EVENT_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_event_log(
    open_cfw_event_word function,
    open_cfw_event_u32 line,
    open_cfw_event_word format)
{
#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
    open_cfw_event_flags_host_log(
        1U,
        OPEN_CFW_EVENT_LOG_TAG,
        OPEN_CFW_EVENT_LOG_FILE,
        function,
        line,
        format);
#else
    ((open_cfw_event_log_fn)(open_cfw_event_word)OPEN_CFW_EVENT_LOG_THUMB)(
        1U,
        (const void *)(open_cfw_event_word)OPEN_CFW_EVENT_LOG_TAG,
        (const void *)(open_cfw_event_word)OPEN_CFW_EVENT_LOG_FILE,
        (const void *)function,
        line,
        (const void *)format);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_event_flags_init_41fe62(void)
{
    open_cfw_event_word *const slot = open_cfw_event_handle_slot();

    if (*slot != 0U) {
        return;
    }
#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
    *slot = open_cfw_event_flags_host_create(
        open_cfw_event_flags_host_config());
#else
    *slot = ((open_cfw_event_create_fn)(open_cfw_event_word)
        OPEN_CFW_EVENT_CREATE_THUMB)(
            (const void *)(open_cfw_event_word)OPEN_CFW_EVENT_CONFIG_ADDRESS);
#endif
    if (*slot == 0U) {
        open_cfw_event_log(
            OPEN_CFW_EVENT_INIT_FUNCTION,
            OPEN_CFW_EVENT_INIT_LINE,
            OPEN_CFW_EVENT_INIT_FORMAT);
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_event_flags_acquire_41fe9c(void)
{
    const open_cfw_event_word handle = *open_cfw_event_handle_slot();
    open_cfw_event_u32 status;

    if (handle == 0U) {
        return;
    }
#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
    status = open_cfw_event_flags_host_acquire(
        handle, OPEN_CFW_EVENT_WAIT_FOREVER);
#else
    status = ((open_cfw_event_acquire_fn)(open_cfw_event_word)
        OPEN_CFW_EVENT_ACQUIRE_THUMB)(
            handle, OPEN_CFW_EVENT_WAIT_FOREVER);
#endif
    if (status != 0U) {
        open_cfw_event_log(
            OPEN_CFW_EVENT_ACQUIRE_FUNCTION,
            OPEN_CFW_EVENT_ACQUIRE_LINE,
            OPEN_CFW_EVENT_ACQUIRE_FORMAT);
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_event_flags_release_41fed4(void)
{
    const open_cfw_event_word handle = *open_cfw_event_handle_slot();
    open_cfw_event_u32 status;

    if (handle == 0U) {
        return;
    }
#if defined(OPEN_CFW_EVENT_FLAGS_SERVICE_HOST)
    status = open_cfw_event_flags_host_release(handle);
#else
    status = ((open_cfw_event_release_fn)(open_cfw_event_word)
        OPEN_CFW_EVENT_RELEASE_THUMB)(handle);
#endif
    if (status != 0U) {
        open_cfw_event_log(
            OPEN_CFW_EVENT_RELEASE_FUNCTION,
            OPEN_CFW_EVENT_RELEASE_LINE,
            OPEN_CFW_EVENT_RELEASE_FORMAT);
    }
}
