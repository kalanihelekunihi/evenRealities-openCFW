/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Onboarding-flag update matched to stock entry 0x0047E470.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_flag_update_uintptr;

typedef const volatile unsigned char *
(*open_cfw_onboarding_flag_update_get_function)(unsigned int);
typedef unsigned int (*open_cfw_onboarding_flag_update_set_function)(
    unsigned int,
    const unsigned int *
);
typedef unsigned int (*open_cfw_onboarding_flag_update_event_function)(
    void *,
    unsigned int
);

#ifndef OPEN_CFW_ONBOARDING_FLAG_UPDATE_GET
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_GET(index) \
    (((open_cfw_onboarding_flag_update_get_function) \
        (open_cfw_onboarding_flag_update_uintptr)0x004A7839U)(index))
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_UPDATE_SET
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_SET(index, value) \
    (((open_cfw_onboarding_flag_update_set_function) \
        (open_cfw_onboarding_flag_update_uintptr)0x004A777DU)( \
            index, \
            value \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_UPDATE_PENDING
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_PENDING \
    (*(volatile unsigned int *) \
        (open_cfw_onboarding_flag_update_uintptr)0x20074840U)
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_HANDLE
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_HANDLE \
    (*(void * volatile *) \
        (open_cfw_onboarding_flag_update_uintptr)0x20074570U)
#endif

#ifndef OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_SET
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_SET(handle, flags) \
    (((open_cfw_onboarding_flag_update_event_function) \
        (open_cfw_onboarding_flag_update_uintptr)0x004495E5U)( \
            handle, \
            flags \
        ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_onboarding_flag_update(unsigned int value)
{
    const volatile unsigned char *stored =
        OPEN_CFW_ONBOARDING_FLAG_UPDATE_GET(0U);
    unsigned int current = stored == (const volatile unsigned char *)0
        ? 0U
        : (unsigned int)*stored;

    if (current != (value & 0xFFU)) {
        (void)OPEN_CFW_ONBOARDING_FLAG_UPDATE_SET(0U, &value);
        OPEN_CFW_ONBOARDING_FLAG_UPDATE_PENDING = 1U;
        (void)OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_SET(
            OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_HANDLE,
            4U
        );
    }

    return value;
}

#undef OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_SET
#undef OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_HANDLE
#undef OPEN_CFW_ONBOARDING_FLAG_UPDATE_PENDING
#undef OPEN_CFW_ONBOARDING_FLAG_UPDATE_SET
#undef OPEN_CFW_ONBOARDING_FLAG_UPDATE_GET
