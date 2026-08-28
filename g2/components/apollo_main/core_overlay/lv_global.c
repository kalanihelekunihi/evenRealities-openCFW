/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 LVGL global-state initializer at
 * 0x004734CC.
 */

typedef void (*open_cfw_lv_global_list_initialize_fn)(
    void *list,
    unsigned int node_size
);
typedef void (*open_cfw_lv_global_finalize_fn)(unsigned int cookie);
typedef void (*open_cfw_lv_global_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);

extern void open_cfw_lv_memory_zero(void *destination, unsigned int size);

#ifndef OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE
#define OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE(list, node_size) \
    (((open_cfw_lv_global_list_initialize_fn)0x00482B01U)( \
        (list), \
        (node_size) \
    ))
#endif

#ifndef OPEN_CFW_LV_GLOBAL_FINALIZE
#define OPEN_CFW_LV_GLOBAL_FINALIZE(cookie) \
    (((open_cfw_lv_global_finalize_fn)0x004888F7U)(cookie))
#endif

#ifndef OPEN_CFW_LV_GLOBAL_LOG
#define OPEN_CFW_LV_GLOBAL_LOG \
    ((open_cfw_lv_global_log_fn)0x0044D25DU)
#endif

#ifndef OPEN_CFW_LV_GLOBAL_FATAL
#define OPEN_CFW_LV_GLOBAL_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(void *)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

#define OPEN_CFW_LV_GLOBAL_FILE ((const void *)0x006EE148U)
#define OPEN_CFW_LV_GLOBAL_FUNCTION ((const void *)0x007874E0U)
#define OPEN_CFW_LV_GLOBAL_ASSERTED ((const void *)0x00761B70U)
#define OPEN_CFW_LV_GLOBAL_EXPRESSION ((const void *)0x007874F0U)
#define OPEN_CFW_LV_GLOBAL_NULL_POINTER ((const void *)0x00787500U)

__attribute__((used, noinline))
void open_cfw_lv_global_initialize(void *global)
{
    unsigned char *bytes = (unsigned char *)global;

    if (global == (void *)0) {
        OPEN_CFW_LV_GLOBAL_LOG(
            3U,
            OPEN_CFW_LV_GLOBAL_FILE,
            0x7CU,
            OPEN_CFW_LV_GLOBAL_FUNCTION,
            OPEN_CFW_LV_GLOBAL_ASSERTED,
            OPEN_CFW_LV_GLOBAL_EXPRESSION,
            OPEN_CFW_LV_GLOBAL_NULL_POINTER,
            (const void *)0
        );
        OPEN_CFW_LV_GLOBAL_FATAL();
        return;
    }

    open_cfw_lv_memory_zero(global, 0x1ECU);
    OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE(bytes + 4U, 0x31CU);
    OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE(bytes + 0x44U, 0xDCU);
    *(unsigned int *)(void *)(bytes + 0x64U) = 0xA1B2C3D4U;
    bytes[0x24U] = 1U;
    *(unsigned int *)(void *)(bytes + 0x58U) = 3U;
    *(unsigned int *)(void *)(bytes + 0x2CU) = 0x89U;
    *(unsigned int *)(void *)(bytes + 0x70U) = 0x42U;
    OPEN_CFW_LV_GLOBAL_FINALIZE(0x1234ABCDU);
}

#undef OPEN_CFW_LV_GLOBAL_NULL_POINTER
#undef OPEN_CFW_LV_GLOBAL_EXPRESSION
#undef OPEN_CFW_LV_GLOBAL_ASSERTED
#undef OPEN_CFW_LV_GLOBAL_FUNCTION
#undef OPEN_CFW_LV_GLOBAL_FILE
#undef OPEN_CFW_LV_GLOBAL_FATAL
#undef OPEN_CFW_LV_GLOBAL_LOG
#undef OPEN_CFW_LV_GLOBAL_FINALIZE
#undef OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE
