/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 LVGL display-buffer lock,
 * unlock, mutex initialization, and port initialization cluster at
 * 0x0047381E...0x00473933.
 */

typedef int (*open_cfw_lv_display_lock_take_fn)(
    void *mutex,
    unsigned int timeout
);
typedef int (*open_cfw_lv_display_lock_context_fn)(void);
typedef void (*open_cfw_lv_display_lock_give_task_fn)(
    void *mutex,
    unsigned int first,
    unsigned int second,
    unsigned int third
);
typedef void (*open_cfw_lv_display_lock_give_irq_fn)(
    void *mutex,
    unsigned int value
);
typedef void *(*open_cfw_lv_display_lock_create_fn)(
    unsigned int count,
    unsigned int flags,
    unsigned int kind
);
typedef void (*open_cfw_lv_display_lock_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_MUTEX
#define OPEN_CFW_LV_DISPLAY_LOCK_MUTEX \
    (*(void * volatile *)(void *)0x200746BCU)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_TAKE
#define OPEN_CFW_LV_DISPLAY_LOCK_TAKE(mutex, timeout) \
    (((open_cfw_lv_display_lock_take_fn)0x00441C45U)( \
        (mutex), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_CONTEXT
#define OPEN_CFW_LV_DISPLAY_LOCK_CONTEXT() \
    (((open_cfw_lv_display_lock_context_fn)0x00442229U)())
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK
#define OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK(mutex, first, second, third) \
    (((open_cfw_lv_display_lock_give_task_fn)0x004417EFU)( \
        (mutex), \
        (first), \
        (second), \
        (third) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_GIVE_IRQ
#define OPEN_CFW_LV_DISPLAY_LOCK_GIVE_IRQ(mutex, value) \
    (((open_cfw_lv_display_lock_give_irq_fn)0x00441A43U)( \
        (mutex), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_CREATE
#define OPEN_CFW_LV_DISPLAY_LOCK_CREATE(count, flags, kind) \
    (((open_cfw_lv_display_lock_create_fn)0x00441637U)( \
        (count), \
        (flags), \
        (kind) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_LOG
#define OPEN_CFW_LV_DISPLAY_LOCK_LOG \
    ((open_cfw_lv_display_lock_log_fn)0x0044D25DU)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_LOCK_SETUP
#define OPEN_CFW_LV_DISPLAY_LOCK_SETUP() open_cfw_lv_display_setup()
#endif

#define OPEN_CFW_LV_DISPLAY_LOCK_FILE ((const void *)0x006DD7D4U)
#define OPEN_CFW_LV_DISPLAY_LOCK_NAME ((const void *)0x0077F964U)
#define OPEN_CFW_LV_DISPLAY_LOCK_UNLOCK_NAME ((const void *)0x00777E04U)
#define OPEN_CFW_LV_DISPLAY_LOCK_INIT_NAME ((const void *)0x0076C514U)
#define OPEN_CFW_LV_DISPLAY_LOCK_MISSING ((const void *)0x00734DB4U)
#define OPEN_CFW_LV_DISPLAY_LOCK_TIMEOUT ((const void *)0x007550B8U)
#define OPEN_CFW_LV_DISPLAY_LOCK_CREATE_FAILED ((const void *)0x0073F3F4U)

__attribute__((used, noinline))
void open_cfw_lv_display_lock(void)
{
    void *mutex = OPEN_CFW_LV_DISPLAY_LOCK_MUTEX;

    if (mutex == (void *)0) {
        OPEN_CFW_LV_DISPLAY_LOCK_LOG(
            3U,
            OPEN_CFW_LV_DISPLAY_LOCK_FILE,
            0x124U,
            OPEN_CFW_LV_DISPLAY_LOCK_NAME,
            OPEN_CFW_LV_DISPLAY_LOCK_MISSING
        );
        return;
    }
    if (OPEN_CFW_LV_DISPLAY_LOCK_TAKE(mutex, 1000U) == 0) {
        OPEN_CFW_LV_DISPLAY_LOCK_LOG(
            3U,
            OPEN_CFW_LV_DISPLAY_LOCK_FILE,
            0x12AU,
            OPEN_CFW_LV_DISPLAY_LOCK_NAME,
            OPEN_CFW_LV_DISPLAY_LOCK_TIMEOUT
        );
    }
}

__attribute__((used, noinline))
void open_cfw_lv_display_unlock(void)
{
    void *mutex = OPEN_CFW_LV_DISPLAY_LOCK_MUTEX;

    if (mutex == (void *)0) {
        OPEN_CFW_LV_DISPLAY_LOCK_LOG(
            3U,
            OPEN_CFW_LV_DISPLAY_LOCK_FILE,
            0x131U,
            OPEN_CFW_LV_DISPLAY_LOCK_UNLOCK_NAME,
            OPEN_CFW_LV_DISPLAY_LOCK_MISSING
        );
        return;
    }
    if (OPEN_CFW_LV_DISPLAY_LOCK_CONTEXT() == 0) {
        OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK(mutex, 0U, 0U, 0U);
    }
    else {
        OPEN_CFW_LV_DISPLAY_LOCK_GIVE_IRQ(mutex, 0U);
    }
}

__attribute__((used, noinline))
void open_cfw_lv_display_lock_initialize(void)
{
    void *mutex = OPEN_CFW_LV_DISPLAY_LOCK_CREATE(1U, 0U, 3U);

    OPEN_CFW_LV_DISPLAY_LOCK_MUTEX = mutex;
    if (mutex == (void *)0) {
        OPEN_CFW_LV_DISPLAY_LOCK_LOG(
            3U,
            OPEN_CFW_LV_DISPLAY_LOCK_FILE,
            0x140U,
            OPEN_CFW_LV_DISPLAY_LOCK_INIT_NAME,
            OPEN_CFW_LV_DISPLAY_LOCK_CREATE_FAILED
        );
    }
    OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK(mutex, 0U, 0U, 0U);
}

__attribute__((used, noinline))
void open_cfw_lv_display_port_initialize(void)
{
    open_cfw_lv_display_lock_initialize();
    OPEN_CFW_LV_DISPLAY_LOCK_SETUP();
}

#undef OPEN_CFW_LV_DISPLAY_LOCK_CREATE_FAILED
#undef OPEN_CFW_LV_DISPLAY_LOCK_TIMEOUT
#undef OPEN_CFW_LV_DISPLAY_LOCK_MISSING
#undef OPEN_CFW_LV_DISPLAY_LOCK_INIT_NAME
#undef OPEN_CFW_LV_DISPLAY_LOCK_UNLOCK_NAME
#undef OPEN_CFW_LV_DISPLAY_LOCK_NAME
#undef OPEN_CFW_LV_DISPLAY_LOCK_FILE
#undef OPEN_CFW_LV_DISPLAY_LOCK_SETUP
#undef OPEN_CFW_LV_DISPLAY_LOCK_LOG
#undef OPEN_CFW_LV_DISPLAY_LOCK_CREATE
#undef OPEN_CFW_LV_DISPLAY_LOCK_GIVE_IRQ
#undef OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK
#undef OPEN_CFW_LV_DISPLAY_LOCK_CONTEXT
#undef OPEN_CFW_LV_DISPLAY_LOCK_TAKE
#undef OPEN_CFW_LV_DISPLAY_LOCK_MUTEX
