/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Deferred onboarding-flag persistence matched to stock entry 0x0047E3E6.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_flag_uintptr;

typedef int (*open_cfw_onboarding_flag_save_function)(void);
typedef unsigned int (*open_cfw_onboarding_flag_log_level_function)(void);
typedef void (*open_cfw_onboarding_flag_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_onboarding_flag_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_ONBOARDING_FLAG_PENDING
#define OPEN_CFW_ONBOARDING_FLAG_PENDING \
    (*(volatile unsigned int *) \
        (open_cfw_onboarding_flag_uintptr)0x20074840U)
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_SAVE
#define OPEN_CFW_ONBOARDING_FLAG_SAVE() \
    (((open_cfw_onboarding_flag_save_function) \
        (open_cfw_onboarding_flag_uintptr)0x004A77D3U)())
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL
#define OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL() \
    (((open_cfw_onboarding_flag_log_level_function) \
        (open_cfw_onboarding_flag_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_LOG
#define OPEN_CFW_ONBOARDING_FLAG_LOG(...) \
    (((open_cfw_onboarding_flag_log_function) \
        (open_cfw_onboarding_flag_uintptr)0x0043D575U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_TRACE
#define OPEN_CFW_ONBOARDING_FLAG_TRACE(...) \
    (((open_cfw_onboarding_flag_trace_function) \
        (open_cfw_onboarding_flag_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_flag_pointer(open_cfw_onboarding_flag_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_onboarding_flag_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_onboarding_flag_save_to_flash(void)
{
    const void *module =
        open_cfw_onboarding_flag_pointer(0x00781570U);
    const void *file =
        open_cfw_onboarding_flag_pointer(0x006E8ECCU);
    const void *function =
        open_cfw_onboarding_flag_pointer(0x0076E964U);
    int result;

    if (OPEN_CFW_ONBOARDING_FLAG_PENDING != 1U) {
        return;
    }

    if ((OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_FLAG_LOG(
            4U,
            module,
            file,
            function,
            0x5CU,
            open_cfw_onboarding_flag_pointer(0x0076E980U)
        );
    }
    if (open_cfw_onboarding_flag_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_flag_pointer(0x007361C4U);

        OPEN_CFW_ONBOARDING_FLAG_TRACE(
            0x10000000U,
            message,
            message
        );
    }

    result = OPEN_CFW_ONBOARDING_FLAG_SAVE();
    if (result == 0) {
        OPEN_CFW_ONBOARDING_FLAG_PENDING = 0U;
        return;
    }

    if ((OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_FLAG_LOG(
            1U,
            module,
            file,
            function,
            0x61U,
            open_cfw_onboarding_flag_pointer(0x0075732CU)
        );
    }
    if (open_cfw_onboarding_flag_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_flag_pointer(0x00720DE0U);

        OPEN_CFW_ONBOARDING_FLAG_TRACE(
            0x04000000U,
            message,
            message
        );
    }
}

#undef OPEN_CFW_ONBOARDING_FLAG_TRACE
#undef OPEN_CFW_ONBOARDING_FLAG_LOG
#undef OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL
#undef OPEN_CFW_ONBOARDING_FLAG_SAVE
#undef OPEN_CFW_ONBOARDING_FLAG_PENDING
