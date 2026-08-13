/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 transition-descriptor
 * initializer at 0x00482950...0x0048297B.
 *
 * The descriptor is the firmware's five-word LVGL transition description.
 * The stock routine clears all 20 bytes before installing the properties,
 * user context, path callback, duration, and delay. A null path selects the
 * retained linear-path callback at Thumb address 0x00450635.
 */

typedef unsigned int open_cfw_runtime_transition_word;
typedef unsigned int open_cfw_runtime_transition_pointer;

struct open_cfw_runtime_transition_descriptor {
    open_cfw_runtime_transition_pointer properties;
    open_cfw_runtime_transition_pointer user_data;
    open_cfw_runtime_transition_pointer path_callback;
    open_cfw_runtime_transition_word duration;
    open_cfw_runtime_transition_word delay;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_transition_descriptor) == 20U,
    "transition descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_transition_descriptor,
        properties
    ) == 0x00U,
    "transition properties offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_transition_descriptor,
        user_data
    ) == 0x04U,
    "transition user-data offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_transition_descriptor,
        path_callback
    ) == 0x08U,
    "transition path-callback offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_transition_descriptor,
        duration
    ) == 0x0cU,
    "transition duration offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_transition_descriptor,
        delay
    ) == 0x10U,
    "transition delay offset changed"
);

#ifndef OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO
void *open_cfw_runtime_memory_zero(void *destination, unsigned int size);
#define OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO(destination, size) \
    open_cfw_runtime_memory_zero((destination), (size))
#endif

#ifndef OPEN_CFW_RUNTIME_TRANSITION_LINEAR_PATH
#define OPEN_CFW_RUNTIME_TRANSITION_LINEAR_PATH 0x00450635U
#endif

/*
 * AAPCS arguments:
 *   r0 descriptor, r1 properties, r2 path callback, r3 duration,
 *   stack[0] delay, stack[1] user data.
 *
 * The public LVGL operation is initializer-style. The stock epilogue also
 * restores the original r3 into r0; returning duration explicitly preserves
 * that observable register result for binary callers.
 */
__attribute__((used, noinline))
open_cfw_runtime_transition_word
open_cfw_runtime_transition_descriptor_init(
    struct open_cfw_runtime_transition_descriptor *descriptor,
    open_cfw_runtime_transition_pointer properties,
    open_cfw_runtime_transition_pointer path_callback,
    open_cfw_runtime_transition_word duration,
    open_cfw_runtime_transition_word delay,
    open_cfw_runtime_transition_pointer user_data
)
{
    OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO(
        descriptor,
        sizeof(*descriptor)
    );

    descriptor->properties = properties;
    if (path_callback == 0U) {
        path_callback = OPEN_CFW_RUNTIME_TRANSITION_LINEAR_PATH;
    }
    descriptor->path_callback = path_callback;
    descriptor->duration = duration;
    descriptor->delay = delay;
    descriptor->user_data = user_data;

    return duration;
}

#undef OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO
#undef OPEN_CFW_RUNTIME_TRANSITION_LINEAR_PATH
