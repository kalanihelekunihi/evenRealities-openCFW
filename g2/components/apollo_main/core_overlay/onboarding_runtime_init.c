/*
 * SPDX-License-Identifier: MIT
 *
 * Onboarding runtime initialization matched to stock entry 0x0047E674.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_runtime_init_uintptr;

typedef void (*open_cfw_onboarding_runtime_init_attributes_function)(
    unsigned int *,
    unsigned int *,
    unsigned int *
);
typedef unsigned int (*open_cfw_onboarding_runtime_init_thread_function)(
    const void *,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_onboarding_runtime_init_lock_function)(void);

void open_cfw_rtos_timer_runtime_initialize(void);

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_CORE
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_CORE() \
    open_cfw_rtos_timer_runtime_initialize()
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_ATTRIBUTES
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_ATTRIBUTES(...) \
    (((open_cfw_onboarding_runtime_init_attributes_function) \
        (open_cfw_onboarding_runtime_init_uintptr)0x004D3611U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD(...) \
    (((open_cfw_onboarding_runtime_init_thread_function) \
        (open_cfw_onboarding_runtime_init_uintptr)0x00454821U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_PREREQUISITE
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_PREREQUISITE() \
    (*(volatile unsigned int *) \
        (open_cfw_onboarding_runtime_init_uintptr)0x20074AB0U)
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_STORE
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_STORE(value) \
    (*(volatile unsigned int *) \
        (open_cfw_onboarding_runtime_init_uintptr)0x20074AB4U = (value))
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_LOAD
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_LOAD() \
    (*(volatile unsigned int *) \
        (open_cfw_onboarding_runtime_init_uintptr)0x20074AB4U)
#endif

#ifndef OPEN_CFW_ONBOARDING_RUNTIME_INIT_FAIL_STOP
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_FAIL_STOP() \
    do { \
        ((open_cfw_onboarding_runtime_init_lock_function) \
            (open_cfw_onboarding_runtime_init_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_onboarding_runtime_init_uintptr) \
            (~(open_cfw_onboarding_runtime_init_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_runtime_init_pointer(
    open_cfw_onboarding_runtime_init_uintptr address
)
{
    return (const void *)address;
}

__attribute__((used, noinline))
int open_cfw_onboarding_runtime_initialize(void)
{
    unsigned int control_block = 0U;
    unsigned int stack_memory = 0U;
    unsigned int attribute_bits = 0U;
    unsigned int thread = 0U;

    OPEN_CFW_ONBOARDING_RUNTIME_INIT_CORE();
    if (OPEN_CFW_ONBOARDING_RUNTIME_INIT_PREREQUISITE() != 0U) {
        OPEN_CFW_ONBOARDING_RUNTIME_INIT_ATTRIBUTES(
            &control_block,
            &stack_memory,
            &attribute_bits
        );
        thread = OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD(
            open_cfw_onboarding_runtime_init_pointer(0x0047E879U),
            open_cfw_onboarding_runtime_init_pointer(0x0078EBCCU),
            attribute_bits,
            0U,
            0x36U,
            stack_memory,
            control_block
        );
        OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_STORE(thread);
        if (OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_LOAD() != 0U) {
            return 1;
        }
    }

    OPEN_CFW_ONBOARDING_RUNTIME_INIT_FAIL_STOP();
    return 0;
}

#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_FAIL_STOP
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_LOAD
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_STORE
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_PREREQUISITE
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_ATTRIBUTES
#undef OPEN_CFW_ONBOARDING_RUNTIME_INIT_CORE
